"""
Service for Coin-related database operations.
"""
from sqlalchemy.orm import Session
from app.models import models
from typing import Dict, Any, Optional, List


def get_by_coingecko_id(db: Session, coingecko_id: str) -> Optional[models.Coin]:
    """
    Get a coin by its Coingecko ID.
    
    Args:
        db: Database session
        coingecko_id: Coingecko identifier for the coin
        
    Returns:
        Coin model if found, None otherwise
    """
    return db.query(models.Coin).filter(models.Coin.coingecko_id == coingecko_id).first()


def get_by_id(db: Session, coin_id: int) -> Optional[models.Coin]:
    """
    Get a coin by its database ID.
    
    Args:
        db: Database session
        coin_id: Database ID of the coin
        
    Returns:
        Coin model if found, None otherwise
    """
    return db.query(models.Coin).filter(models.Coin.id == coin_id).first()


def get_all(db: Session, limit: int = 100, offset: int = 0) -> List[models.Coin]:
    """
    Get all coins with pagination.
    
    Args:
        db: Database session
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        List of coin models
    """
    return db.query(models.Coin).order_by(models.Coin.name).offset(offset).limit(limit).all()


def create(db: Session, coin_data: Dict[str, Any]) -> models.Coin:
    """
    Create a new coin record.
    
    Args:
        db: Database session
        coin_data: Dictionary containing coin attributes
        
    Returns:
        Newly created coin model
    """
    coin = models.Coin(
        coingecko_id=coin_data["coingecko_id"],
        symbol=coin_data["symbol"],
        name=coin_data["name"]
    )
    db.add(coin)
    db.commit()
    db.refresh(coin)
    return coin


def update(db: Session, coin_id: int, coin_data: Dict[str, Any]) -> Optional[models.Coin]:
    """
    Update an existing coin record.
    
    Args:
        db: Database session
        coin_id: ID of the coin to update
        coin_data: Dictionary containing coin attributes to update
        
    Returns:
        Updated coin model if found, None otherwise
    """
    coin = get_by_id(db, coin_id)
    if not coin:
        return None
        
    for key, value in coin_data.items():
        setattr(coin, key, value)
        
    db.commit()
    db.refresh(coin)
    return coin 