"""
Background task scheduler for automatic data updates from CoinGecko API
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services import coingecko
from app.models import models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("scheduler")

# Global variable to track the last update time
last_coin_update: Optional[datetime] = None
last_exchange_update: Optional[datetime] = None


async def update_coins_task(db: Session):
    """
    Background task to update coin data from CoinGecko
    """
    global last_coin_update
    
    logger.info("Starting coin data update task")
    try:
        # Fetch top coins from CoinGecko API
        coins_data = await coingecko.get_coins()
        
        # We'll update top 50 coins
        top_coins = coins_data[:50]
        
        updated_count = 0
        created_count = 0
        
        for coin_data in top_coins:
            # Check if coin exists
            db_coin = db.query(models.Coin).filter(models.Coin.coingecko_id == coin_data["id"]).first()
            
            if db_coin:
                # Update existing coin
                db_coin.symbol = coin_data["symbol"].upper()
                db_coin.name = coin_data["name"]
                db_coin.updated_at = datetime.now(timezone.utc)
                updated_count += 1
            else:
                # Create new coin
                db_coin = models.Coin(
                    coingecko_id=coin_data["id"],
                    symbol=coin_data["symbol"].upper(),
                    name=coin_data["name"]
                )
                db.add(db_coin)
                created_count += 1
        
        db.commit()
        last_coin_update = datetime.now(timezone.utc)
        logger.info(f"Coin update completed: {updated_count} updated, {created_count} created")
    
    except Exception as e:
        logger.error(f"Error updating coins: {str(e)}")


async def update_exchanges_task(db: Session):
    """
    Background task to update exchange data from CoinGecko
    """
    global last_exchange_update
    
    logger.info("Starting exchange data update task")
    try:
        # Fetch exchanges from CoinGecko API
        exchanges_data = await coingecko.get_exchanges()
        
        # Update top 20 exchanges
        top_exchanges = exchanges_data[:20]
        
        updated_count = 0
        created_count = 0
        
        for exchange_data in top_exchanges:
            # Check if exchange exists
            db_exchange = db.query(models.Exchange).filter(models.Exchange.name == exchange_data["name"]).first()
            
            if db_exchange:
                # Update existing exchange
                db_exchange.website = exchange_data.get("url")
                db_exchange.logo_url = exchange_data.get("image")
                db_exchange.updated_at = datetime.now(timezone.utc)
                updated_count += 1
            else:
                # Create new exchange
                db_exchange = models.Exchange(
                    name=exchange_data["name"],
                    website=exchange_data.get("url"),
                    logo_url=exchange_data.get("image")
                )
                db.add(db_exchange)
                created_count += 1
        
        db.commit()
        last_exchange_update = datetime.now(timezone.utc)
        logger.info(f"Exchange update completed: {updated_count} updated, {created_count} created")
    
    except Exception as e:
        logger.error(f"Error updating exchanges: {str(e)}")


async def update_prices_task(db: Session):
    """
    Background task to update price data for all coins
    """
    logger.info("Starting price data update task")
    try:
        # Get all coins from database
        coins = db.query(models.Coin).all()
        
        update_count = 0
        
        for coin in coins:
            try:
                # Fetch ticker data for each coin
                ticker_data = await coingecko.get_coin_tickers(coin.coingecko_id)
                
                for ticker in ticker_data.get("tickers", []):
                    exchange_name = ticker.get("market", {}).get("name")
                    if not exchange_name:
                        continue
                    
                    # Find exchange
                    exchange = db.query(models.Exchange).filter(models.Exchange.name == exchange_name).first()
                    if not exchange:
                        continue
                    
                    # Update or create price record
                    price = db.query(models.Price).filter(
                        models.Price.exchange_id == exchange.id,
                        models.Price.coin_id == coin.id
                    ).first()
                    
                    if price:
                        # Update existing price
                        price.price_usd = ticker.get("converted_last", {}).get("usd", 0)
                        price.volume_24h = ticker.get("converted_volume", {}).get("usd", 0)
                        price.bid_price = ticker.get("bid")
                        price.ask_price = ticker.get("ask")
                        price.last_updated = datetime.now(timezone.utc)
                    else:
                        # Create new price record
                        price = models.Price(
                            exchange_id=exchange.id,
                            coin_id=coin.id,
                            price_usd=ticker.get("converted_last", {}).get("usd", 0),
                            volume_24h=ticker.get("converted_volume", {}).get("usd", 0),
                            bid_price=ticker.get("bid"),
                            ask_price=ticker.get("ask")
                        )
                        db.add(price)
                    
                    update_count += 1
                
                # Avoid rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error updating prices for {coin.name}: {str(e)}")
                continue
        
        db.commit()
        logger.info(f"Price update completed: {update_count} prices updated")
    
    except Exception as e:
        logger.error(f"Error in price update task: {str(e)}")


def schedule_updates(background_tasks: BackgroundTasks):
    """
    Schedule all update tasks to run in the background
    """
    # Get a database session
    db = next(get_db())
    
    # Schedule tasks
    background_tasks.add_task(update_coins_task, db)
    background_tasks.add_task(update_exchanges_task, db)
    background_tasks.add_task(update_prices_task, db)
    
    return {"status": "Update tasks scheduled"}


def get_last_update_times():
    """
    Get the timestamps of the last updates
    """
    return {
        "coins": last_coin_update.isoformat() if last_coin_update else None,
        "exchanges": last_exchange_update.isoformat() if last_exchange_update else None
    } 