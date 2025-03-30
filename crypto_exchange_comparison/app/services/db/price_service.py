"""
Service for Price-related database operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import models
from typing import Dict, Any, Optional, List, Tuple


def get_by_exchange_and_coin(
    db: Session, 
    exchange_id: int, 
    coin_id: int
) -> Optional[models.Price]:
    """
    Get a price record for a specific exchange and coin.
    
    Args:
        db: Database session
        exchange_id: ID of the exchange
        coin_id: ID of the coin
        
    Returns:
        Price model if found, None otherwise
    """
    return db.query(models.Price).filter(
        models.Price.exchange_id == exchange_id,
        models.Price.coin_id == coin_id
    ).first()


def get_by_id(db: Session, price_id: int) -> Optional[models.Price]:
    """
    Get a price record by its database ID.
    
    Args:
        db: Database session
        price_id: Database ID of the price record
        
    Returns:
        Price model if found, None otherwise
    """
    return db.query(models.Price).filter(models.Price.id == price_id).first()


def get_all_for_coin(
    db: Session, 
    coin_id: int, 
    limit: int = 100, 
    offset: int = 0
) -> List[models.Price]:
    """
    Get all price records for a specific coin with pagination.
    
    Args:
        db: Database session
        coin_id: ID of the coin
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        List of price models
    """
    return db.query(models.Price).filter(
        models.Price.coin_id == coin_id
    ).order_by(models.Price.price_usd).offset(offset).limit(limit).all()


def create(db: Session, price_data: Dict[str, Any]) -> models.Price:
    """
    Create a new price record.
    
    Args:
        db: Database session
        price_data: Dictionary containing price attributes
        
    Returns:
        Newly created price model
    """
    price = models.Price(
        exchange_id=price_data["exchange_id"],
        coin_id=price_data["coin_id"],
        price_usd=price_data.get("price_usd"),
        volume_24h=price_data.get("volume_24h"),
        bid_price=price_data.get("bid_price"),
        ask_price=price_data.get("ask_price"),
        trading_fee=price_data.get("trading_fee"),
        withdrawal_fee=price_data.get("withdrawal_fee")
    )
    db.add(price)
    db.commit()
    db.refresh(price)
    return price


def update(db: Session, price_id: int, price_data: Dict[str, Any]) -> Optional[models.Price]:
    """
    Update an existing price record.
    
    Args:
        db: Database session
        price_id: ID of the price record to update
        price_data: Dictionary containing price attributes to update
        
    Returns:
        Updated price model if found, None otherwise
    """
    price = get_by_id(db, price_id)
    if not price:
        return None
        
    for key, value in price_data.items():
        setattr(price, key, value)
        
    db.commit()
    db.refresh(price)
    return price


def update_or_create(
    db: Session, 
    filter_data: Dict[str, Any], 
    update_data: Dict[str, Any]
) -> Tuple[models.Price, bool]:
    """
    Update a price record if it exists, or create a new one.
    
    Args:
        db: Database session
        filter_data: Dictionary containing filter criteria (exchange_id, coin_id)
        update_data: Dictionary containing price attributes to update or create
        
    Returns:
        Tuple of (price model, created flag)
    """
    price = get_by_exchange_and_coin(db, filter_data["exchange_id"], filter_data["coin_id"])
    
    if price:
        # Update existing record
        for key, value in update_data.items():
            setattr(price, key, value)
        db.commit()
        db.refresh(price)
        return price
    else:
        # Create new record
        price_data = {**filter_data, **update_data}
        return create(db, price_data)


def get_fees_by_exchange(db: Session, exchange_id: int) -> List[Dict[str, Any]]:
    """
    Get all fee information for a specific exchange.
    
    Args:
        db: Database session
        exchange_id: ID of the exchange
        
    Returns:
        List of dictionaries containing fee information
    """
    prices = db.query(models.Price).join(
        models.Coin, models.Price.coin_id == models.Coin.id
    ).filter(
        models.Price.exchange_id == exchange_id,
        models.Price.trading_fee.isnot(None)
    ).all()
    
    return [
        {
            "coin": price.coin.symbol,
            "trading_fee": price.trading_fee,
            "withdrawal_fee": price.withdrawal_fee
        }
        for price in prices
    ] 