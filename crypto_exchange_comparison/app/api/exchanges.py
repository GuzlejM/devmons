from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.connection import get_db
from app.models import models, schemas
from app.services import coingecko

router = APIRouter()


@router.get("/", response_model=List[schemas.Exchange])
async def get_exchanges(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all exchanges
    """
    exchanges = db.query(models.Exchange).offset(skip).limit(limit).all()
    return exchanges


@router.get("/{exchange_id}", response_model=schemas.Exchange)
async def get_exchange(exchange_id: int, db: Session = Depends(get_db)):
    """
    Get an exchange by ID
    """
    exchange = db.query(models.Exchange).filter(models.Exchange.id == exchange_id).first()
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    return exchange


@router.post("/", response_model=schemas.Exchange)
async def create_exchange(exchange: schemas.ExchangeCreate, db: Session = Depends(get_db)):
    """
    Create a new exchange
    """
    db_exchange = models.Exchange(**exchange.model_dump())
    db.add(db_exchange)
    db.commit()
    db.refresh(db_exchange)
    return db_exchange


@router.get("/{exchange_id}/coins", response_model=List[schemas.Coin])
async def get_exchange_coins(exchange_id: int, db: Session = Depends(get_db)):
    """
    Get all coins listed on an exchange
    """
    exchange = db.query(models.Exchange).filter(models.Exchange.id == exchange_id).first()
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    
    # Get coins via price relationship
    prices = db.query(models.Price).filter(models.Price.exchange_id == exchange_id).all()
    coins = [price.coin for price in prices]
    
    return coins


@router.get("/sync/coingecko", response_model=List[schemas.Exchange])
async def sync_exchanges_from_coingecko(db: Session = Depends(get_db)):
    """
    Sync exchanges from Coingecko API
    """
    try:
        exchanges_data = await coingecko.get_exchanges()
        
        # Create or update exchanges
        added_exchanges = []
        for exchange_data in exchanges_data[:20]:  # Limit to top 20 exchanges
            db_exchange = db.query(models.Exchange).filter(models.Exchange.name == exchange_data["name"]).first()
            
            if not db_exchange:
                db_exchange = models.Exchange(
                    name=exchange_data["name"],
                    website=exchange_data.get("url"),
                    logo_url=exchange_data.get("image")
                )
                db.add(db_exchange)
                db.commit()
                db.refresh(db_exchange)
                added_exchanges.append(db_exchange)
        
        return added_exchanges
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing exchanges: {str(e)}") 