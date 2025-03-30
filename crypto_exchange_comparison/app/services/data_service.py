"""
Service for handling data updates from external sources.
"""
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional

from sqlalchemy.orm import Session

from app.models import models
from app.services.db import coin_service, exchange_service, price_service
from app.services import coingecko_processor

# Configure logging
logger = logging.getLogger("data_service")


async def update_coins(db: Session) -> Tuple[int, int]:
    """
    Update coin data from CoinGecko API.
    
    Args:
        db: Database session
        
    Returns:
        Tuple of (updated_count, created_count)
    """
    logger.info("Starting coin data update")
    
    try:
        # Fetch top coins from CoinGecko API
        top_coins = await coingecko_processor.fetch_top_coins()
        
        updated_count = 0
        created_count = 0
        
        for coin_data in top_coins:
            # Check if coin exists
            db_coin = coin_service.get_by_coingecko_id(db, coin_data["id"])
            
            if db_coin:
                # Update existing coin
                coin_service.update(db, db_coin.id, {
                    "symbol": coin_data["symbol"].upper(),
                    "name": coin_data["name"],
                    "updated_at": datetime.now(timezone.utc)
                })
                updated_count += 1
            else:
                # Create new coin
                coin_service.create(db, {
                    "coingecko_id": coin_data["id"],
                    "symbol": coin_data["symbol"].upper(),
                    "name": coin_data["name"]
                })
                created_count += 1
        
        logger.info(f"Coin update completed: {updated_count} updated, {created_count} created")
        return updated_count, created_count
        
    except Exception as e:
        logger.error(f"Error updating coins: {str(e)}")
        raise


async def update_exchanges(db: Session) -> Tuple[int, int]:
    """
    Update exchange data from CoinGecko API.
    
    Args:
        db: Database session
        
    Returns:
        Tuple of (updated_count, created_count)
    """
    logger.info("Starting exchange data update")
    
    try:
        # Fetch exchanges from CoinGecko API
        top_exchanges = await coingecko_processor.fetch_top_exchanges()
        
        updated_count = 0
        created_count = 0
        
        for exchange_data in top_exchanges:
            # Check if exchange exists
            db_exchange = exchange_service.get_by_name(db, exchange_data["name"])
            
            if db_exchange:
                # Update existing exchange
                exchange_service.update(db, db_exchange.id, {
                    "website": exchange_data.get("url"),
                    "logo_url": exchange_data.get("image"),
                    "updated_at": datetime.now(timezone.utc)
                })
                updated_count += 1
            else:
                # Create new exchange
                exchange_service.create(db, {
                    "name": exchange_data["name"],
                    "website": exchange_data.get("url"),
                    "logo_url": exchange_data.get("image")
                })
                created_count += 1
        
        logger.info(f"Exchange update completed: {updated_count} updated, {created_count} created")
        return updated_count, created_count
        
    except Exception as e:
        logger.error(f"Error updating exchanges: {str(e)}")
        raise


async def update_price_for_coin(
    coin: models.Coin,
    db: Session
) -> int:
    """
    Update price data for a specific coin across all exchanges.
    
    Args:
        coin: Coin model
        db: Database session
        
    Returns:
        Number of price records updated
    """
    update_count = 0
    
    try:
        # Fetch ticker data for the coin
        ticker_data = await coingecko_processor.fetch_coin_tickers(coin.coingecko_id)
        
        # Process exchanges, keeping only highest volume ticker per exchange
        exchange_data = coingecko_processor.filter_best_tickers(ticker_data.get("tickers", []))
        
        # Process the filtered exchanges (one per exchange name)
        for exchange_name, data in exchange_data.items():
            # Find exchange
            exchange = exchange_service.get_by_name(db, exchange_name)
            if not exchange:
                continue
            
            # Update or create price record
            price_service.update_or_create(
                db,
                {"exchange_id": exchange.id, "coin_id": coin.id},
                {
                    "price_usd": data["price"],
                    "volume_24h": data["volume"],
                    "bid_price": data["bid"],
                    "ask_price": data["ask"],
                    "last_updated": datetime.now(timezone.utc)
                }
            )
            
            update_count += 1
        
    except Exception as e:
        logger.error(f"Error updating prices for {coin.name}: {str(e)}")
    
    return update_count


async def update_prices(db: Session) -> int:
    """
    Update price data for all coins.
    
    Args:
        db: Database session
        
    Returns:
        Number of price records updated
    """
    logger.info("Starting price data update")
    
    try:
        # Get all coins from database
        coins = coin_service.get_all(db)
        
        update_count = 0
        
        for coin in coins:
            coin_updates = await update_price_for_coin(coin, db)
            update_count += coin_updates
            
            # Avoid rate limiting
            await asyncio.sleep(1)
        
        logger.info(f"Price update completed: {update_count} prices updated")
        return update_count
        
    except Exception as e:
        logger.error(f"Error in price update task: {str(e)}")
        raise


async def update_all_data(db: Session) -> Dict[str, Any]:
    """
    Update all data types from external sources.
    
    Args:
        db: Database session
        
    Returns:
        Summary of update operations
    """
    results = {}
    
    try:
        # Update coins
        updated_coins, created_coins = await update_coins(db)
        results["coins"] = {"updated": updated_coins, "created": created_coins}
        
        # Update exchanges
        updated_exchanges, created_exchanges = await update_exchanges(db)
        results["exchanges"] = {"updated": updated_exchanges, "created": created_exchanges}
        
        # Update prices
        updated_prices = await update_prices(db)
        results["prices"] = {"updated": updated_prices}
        
        return results
        
    except Exception as e:
        logger.error(f"Error during data update: {str(e)}")
        return {"error": str(e)} 