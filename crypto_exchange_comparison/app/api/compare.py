from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from app.database.connection import get_db
from app.models import models, schemas
from app.services import coingecko, cache

router = APIRouter()


@router.get("/{coin_id}", response_model=schemas.ComparisonResult)
async def compare_exchanges(
    coin_id: str, 
    amount: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Compare prices across exchanges for a specific coin
    """
    # Check if data is cached
    cache_key = f"compare:{coin_id}:{amount if amount else 'default'}"
    cached_data = cache.get_cache(cache_key)
    if cached_data:
        return cached_data
    
    # Get coin from database by Coingecko ID
    coin = db.query(models.Coin).filter(models.Coin.coingecko_id == coin_id).first()
    if not coin:
        # Try to fetch from Coingecko and add to DB
        try:
            coin_data = await coingecko.get_coin_price(coin_id)
            if not coin_data or coin_id not in coin_data:
                raise HTTPException(status_code=404, detail="Coin not found on Coingecko")
            
            # Create new coin in DB
            coin = models.Coin(
                coingecko_id=coin_id,
                symbol=coin_id.upper(),  # Simplified for now
                name=coin_id.capitalize()  # Simplified for now
            )
            db.add(coin)
            db.commit()
            db.refresh(coin)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching coin data: {str(e)}"
            )
    
    # Get ticker data from Coingecko
    try:
        ticker_data = await coingecko.get_coin_tickers(coin_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching ticker data: {str(e)}"
        )
    
    # Process exchange data
    exchange_prices = []
    for ticker in ticker_data.get("tickers", []):
        exchange_name = ticker.get("market", {}).get("name")
        if not exchange_name:
            continue
        
        # Check if exchange exists in DB, otherwise create it
        exchange = db.query(models.Exchange).filter(models.Exchange.name == exchange_name).first()
        if not exchange:
            exchange = models.Exchange(
                name=exchange_name,
                website=ticker.get("market", {}).get("identifier")
            )
            db.add(exchange)
            db.commit()
            db.refresh(exchange)
        
        # Calculate spread if bid and ask are available
        spread = None
        bid_price = ticker.get("bid_ask_spread_percentage")
        ask_price = ticker.get("ask")
        
        if bid_price and ask_price:
            spread = abs(ask_price - bid_price) / ((ask_price + bid_price) / 2) * 100
        
        # Create or update price record
        price = db.query(models.Price).filter(
            models.Price.exchange_id == exchange.id,
            models.Price.coin_id == coin.id
        ).first()
        
        if not price:
            price = models.Price(
                exchange_id=exchange.id,
                coin_id=coin.id,
                price_usd=ticker.get("converted_last", {}).get("usd", 0),
                volume_24h=ticker.get("converted_volume", {}).get("usd", 0),
                bid_price=ticker.get("bid"),
                ask_price=ticker.get("ask"),
                trading_fee=None  # Not available from basic API
            )
            db.add(price)
            db.commit()
            db.refresh(price)
        else:
            price.price_usd = ticker.get("converted_last", {}).get("usd", 0)
            price.volume_24h = ticker.get("converted_volume", {}).get("usd", 0)
            price.bid_price = ticker.get("bid")
            price.ask_price = ticker.get("ask")
            price.last_updated = datetime.now(timezone.utc)
            db.commit()
            db.refresh(price)
        
        # Add to results
        exchange_price = schemas.ExchangePrice(
            exchange_name=exchange.name,
            price_usd=price.price_usd,
            volume_24h=price.volume_24h,
            bid_price=price.bid_price,
            ask_price=price.ask_price,
            trading_fee=price.trading_fee,
            withdrawal_fee=price.withdrawal_fee,
            last_updated=price.last_updated,
            spread=spread
        )
        exchange_prices.append(exchange_price)
    
    # Sort by price
    exchange_prices.sort(key=lambda x: x.price_usd)
    
    # Determine best exchange for large orders (highest volume)
    best_for_large = None
    if exchange_prices:
        volume_sorted = sorted(exchange_prices, key=lambda x: x.volume_24h if x.volume_24h else 0, reverse=True)
        if volume_sorted:
            best_for_large = volume_sorted[0]
    
    # Create comparison result
    result = schemas.ComparisonResult(
        coin=coin.name,
        exchanges=exchange_prices,
        best_price=exchange_prices[0] if exchange_prices else None,
        best_for_large_orders=best_for_large
    )
    
    # Cache the result
    cache.set_cache(cache_key, result.model_dump(), 300)  # Cache for 5 minutes
    
    return result


@router.get("/fees/{exchange_id}", response_model=List[dict])
async def get_exchange_fees(exchange_id: int, db: Session = Depends(get_db)):
    """
    Get fee structure for an exchange
    """
    exchange = db.query(models.Exchange).filter(models.Exchange.id == exchange_id).first()
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    
    # Get all prices with fee data for this exchange
    prices = db.query(models.Price).filter(
        models.Price.exchange_id == exchange_id,
        models.Price.trading_fee.isnot(None)
    ).all()
    
    fees = []
    for price in prices:
        fees.append({
            "coin": price.coin.symbol,
            "trading_fee": price.trading_fee,
            "withdrawal_fee": price.withdrawal_fee
        })
    
    return fees 