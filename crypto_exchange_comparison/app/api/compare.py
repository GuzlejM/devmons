"""
API endpoints for comparing cryptocurrency prices across exchanges.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.database.connection import get_db
from app.models import schemas
from app.services import cache, comparison_service
from app.services.db import exchange_service, price_service

router = APIRouter()


@router.get("/{coin_id}", response_model=schemas.ComparisonResult)
async def compare_exchanges(
    coin_id: str, 
    amount: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Compare prices across exchanges for a specific coin.
    
    Args:
        coin_id: CoinGecko ID of the coin
        amount: Optional amount for calculation
        db: Database session
        
    Returns:
        ComparisonResult with exchange price data
    """
    # Check if data is cached
    cache_key = f"compare:{coin_id}:{amount if amount else 'default'}"
    cached_data = cache.get_cache(cache_key)
    if cached_data:
        return cached_data
    
    try:
        # Get comparison result
        result = await comparison_service.compare_exchanges_for_coin(coin_id, db)
        
        # Cache the result
        cache.set_cache(cache_key, result.model_dump(), 300)  # Cache for 5 minutes
        
        return result
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing comparison: {str(e)}"
        )


@router.get("/fees/{exchange_id}", response_model=List[Dict[str, Any]])
async def get_exchange_fees(exchange_id: int, db: Session = Depends(get_db)):
    """
    Get fee structure for an exchange.
    
    Args:
        exchange_id: ID of the exchange
        db: Database session
        
    Returns:
        List of fee information by coin
    """
    exchange = exchange_service.get_by_id(db, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    
    return price_service.get_fees_by_exchange(db, exchange_id) 