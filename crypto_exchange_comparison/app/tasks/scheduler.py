"""
Background task scheduler for automatic data updates from CoinGecko API.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import BackgroundTasks

from app.database.connection import get_db
from app.services import data_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("scheduler")

# Global variables to track the last update time
last_coin_update: Optional[datetime] = None
last_exchange_update: Optional[datetime] = None
last_price_update: Optional[datetime] = None


async def update_coins_task(db):
    """
    Background task to update coin data from CoinGecko.
    """
    global last_coin_update
    
    try:
        await data_service.update_coins(db)
        last_coin_update = datetime.now(timezone.utc)
    except Exception as e:
        logger.error(f"Error in update_coins_task: {str(e)}")


async def update_exchanges_task(db):
    """
    Background task to update exchange data from CoinGecko.
    """
    global last_exchange_update
    
    try:
        await data_service.update_exchanges(db)
        last_exchange_update = datetime.now(timezone.utc)
    except Exception as e:
        logger.error(f"Error in update_exchanges_task: {str(e)}")


async def update_prices_task(db):
    """
    Background task to update price data for all coins.
    """
    global last_price_update
    
    try:
        await data_service.update_prices(db)
        last_price_update = datetime.now(timezone.utc)
    except Exception as e:
        logger.error(f"Error in update_prices_task: {str(e)}")


async def update_all_task(db):
    """
    Background task to update all data types.
    """
    global last_coin_update, last_exchange_update, last_price_update
    
    try:
        results = await data_service.update_all_data(db)
        current_time = datetime.now(timezone.utc)
        
        if "coins" in results:
            last_coin_update = current_time
            
        if "exchanges" in results:
            last_exchange_update = current_time
            
        if "prices" in results:
            last_price_update = current_time
            
        logger.info(f"All data updated successfully: {results}")
    except Exception as e:
        logger.error(f"Error in update_all_task: {str(e)}")


def schedule_updates(background_tasks: BackgroundTasks) -> Dict[str, str]:
    """
    Schedule all update tasks to run in the background.
    
    Args:
        background_tasks: FastAPI BackgroundTasks object
        
    Returns:
        Status message
    """
    # Get a database session
    db = next(get_db())
    
    # Schedule tasks
    background_tasks.add_task(update_all_task, db)
    
    return {"status": "Update tasks scheduled"}


def get_last_update_times() -> Dict[str, Optional[str]]:
    """
    Get the timestamps of the last updates.
    
    Returns:
        Dictionary with last update times for each data type
    """
    return {
        "coins": last_coin_update.isoformat() if last_coin_update else None,
        "exchanges": last_exchange_update.isoformat() if last_exchange_update else None,
        "prices": last_price_update.isoformat() if last_price_update else None
    }


async def periodic_updates(interval_hours: int = 4):
    """
    Run updates periodically in the background.
    
    Args:
        interval_hours: Number of hours between updates
    """
    while True:
        try:
            # Sleep for the specified interval
            await asyncio.sleep(interval_hours * 60 * 60)
            
            # Get a database session
            db = next(get_db())
            
            # Run update
            await update_all_task(db)
            
            logger.info(f"Scheduled periodic data update completed")
        except Exception as e:
            logger.error(f"Error in periodic update: {str(e)}") 