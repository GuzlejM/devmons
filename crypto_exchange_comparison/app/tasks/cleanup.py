from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.connection import get_db
from app.models import models
from fastapi import APIRouter, Depends
from typing import Dict, Any

router = APIRouter()

async def cleanup_duplicate_prices(db: Session) -> Dict[str, Any]:
    """
    Remove duplicate price entries for the same exchange-coin pairs,
    keeping only the most recently updated record.
    """
    # Get all exchange-coin pairs with multiple price entries
    duplicates = db.query(
        models.Price.exchange_id,
        models.Price.coin_id,
        func.count(models.Price.id).label('count')
    ).group_by(
        models.Price.exchange_id,
        models.Price.coin_id
    ).having(
        func.count(models.Price.id) > 1
    ).all()
    
    total_removed = 0
    
    # For each pair with duplicates
    for exchange_id, coin_id, count in duplicates:
        # Get all prices for this pair, ordered by last_updated (most recent first)
        prices = db.query(models.Price).filter(
            models.Price.exchange_id == exchange_id,
            models.Price.coin_id == coin_id
        ).order_by(
            models.Price.last_updated.desc()
        ).all()
        
        # Keep the first (most recent) and delete the rest
        for price in prices[1:]:
            db.delete(price)
            total_removed += 1
    
    # Commit changes
    db.commit()
    
    return {
        "status": "success",
        "duplicate_pairs_found": len(duplicates),
        "total_records_removed": total_removed
    }

@router.post("/cleanup/duplicates", response_model=Dict[str, Any])
async def cleanup_duplicates_endpoint(db: Session = Depends(get_db)):
    """
    API endpoint to remove duplicate price entries
    """
    return await cleanup_duplicate_prices(db) 