"""
Service for handling exchange comparison business logic.
"""
from typing import Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models import models, schemas
from app.services import coingecko
from app.services.db import coin_service, exchange_service, price_service
from app.services.exchange_analyzer import calculate_spread, process_ticker_data, build_comparison_result


async def get_or_create_coin(coin_id: str, db: Session) -> models.Coin:
    """
    Get a coin or create it if it doesn't exist.
    
    Args:
        coin_id: Coingecko ID of the coin
        db: Database session
        
    Returns:
        Coin model instance
    """
    # Try to get from database first
    coin = coin_service.get_by_coingecko_id(db, coin_id)
    if coin:
        return coin
        
    # Fetch from API and create
    coin_data = await coingecko.get_coin_price(coin_id)
    return coin_service.create(db, {
        "coingecko_id": coin_id,
        "symbol": coin_id.upper(),
        "name": coin_id.capitalize()
    })


async def update_exchange_prices(
    coin: models.Coin,
    exchange_data: Dict[str, Dict[str, Any]],
    db: Session
) -> List[schemas.ExchangePrice]:
    """
    Update price records in database and build exchange price list.
    
    Args:
        coin: Coin model
        exchange_data: Dictionary of processed exchange data
        db: Database session
        
    Returns:
        List of exchange price DTOs
    """
    exchange_prices = []
    
    for exchange_name, data in exchange_data.items():
        # Get or create exchange
        exchange = exchange_service.get_by_name(db, exchange_name)
        if not exchange:
            exchange = exchange_service.create(db, {
                "name": exchange_name,
                "website": data["ticker"].get("market", {}).get("identifier")
            })
        
        # Calculate spread
        bid_price = data["bid"]
        ask_price = data["ask"]
        spread = calculate_spread(bid_price, ask_price)
        
        # Update or create price record
        price = price_service.update_or_create(
            db,
            {"exchange_id": exchange.id, "coin_id": coin.id},
            {
                "price_usd": data["price"],
                "volume_24h": data["volume"],
                "bid_price": bid_price,
                "ask_price": ask_price,
                "last_updated": datetime.now(timezone.utc)
            }
        )
        
        # Create exchange price DTO
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
    
    return exchange_prices


async def compare_exchanges_for_coin(
    coin_id: str,
    db: Session
) -> schemas.ComparisonResult:
    """
    Compare exchanges for a specific coin.
    
    Args:
        coin_id: Coingecko ID of the coin
        db: Database session
        
    Returns:
        Comparison result with price data
    """
    # Get or create coin
    coin = await get_or_create_coin(coin_id, db)
    
    # Get ticker data from Coingecko
    ticker_data = await coingecko.get_coin_tickers(coin_id)
    
    # Process exchange data
    exchange_data = process_ticker_data(ticker_data)
    
    # Update database and build price list
    exchange_prices = await update_exchange_prices(coin, exchange_data, db)
    
    # Build final result
    return build_comparison_result(coin.name, exchange_prices) 