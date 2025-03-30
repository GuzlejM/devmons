"""
Service for Exchange-related database operations.
"""
from sqlalchemy.orm import Session
from app.models import models
from typing import Dict, Any, Optional, List


def get_by_name(db: Session, name: str) -> Optional[models.Exchange]:
    """
    Get an exchange by its name.
    
    Args:
        db: Database session
        name: Name of the exchange
        
    Returns:
        Exchange model if found, None otherwise
    """
    return db.query(models.Exchange).filter(models.Exchange.name == name).first()


def get_by_id(db: Session, exchange_id: int) -> Optional[models.Exchange]:
    """
    Get an exchange by its database ID.
    
    Args:
        db: Database session
        exchange_id: Database ID of the exchange
        
    Returns:
        Exchange model if found, None otherwise
    """
    return db.query(models.Exchange).filter(models.Exchange.id == exchange_id).first()


def get_all(db: Session, limit: int = 100, offset: int = 0) -> List[models.Exchange]:
    """
    Get all exchanges with pagination.
    
    Args:
        db: Database session
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        List of exchange models
    """
    return db.query(models.Exchange).order_by(models.Exchange.name).offset(offset).limit(limit).all()


def create(db: Session, exchange_data: Dict[str, Any]) -> models.Exchange:
    """
    Create a new exchange record.
    
    Args:
        db: Database session
        exchange_data: Dictionary containing exchange attributes
        
    Returns:
        Newly created exchange model
    """
    exchange = models.Exchange(
        name=exchange_data["name"],
        website=exchange_data.get("website"),
        logo_url=exchange_data.get("logo_url")
    )
    db.add(exchange)
    db.commit()
    db.refresh(exchange)
    return exchange


def update(db: Session, exchange_id: int, exchange_data: Dict[str, Any]) -> Optional[models.Exchange]:
    """
    Update an existing exchange record.
    
    Args:
        db: Database session
        exchange_id: ID of the exchange to update
        exchange_data: Dictionary containing exchange attributes to update
        
    Returns:
        Updated exchange model if found, None otherwise
    """
    exchange = get_by_id(db, exchange_id)
    if not exchange:
        return None
        
    for key, value in exchange_data.items():
        setattr(exchange, key, value)
        
    db.commit()
    db.refresh(exchange)
    return exchange 