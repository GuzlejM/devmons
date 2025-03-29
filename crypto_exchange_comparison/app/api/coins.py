from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.connection import get_db
from app.models import models, schemas
from app.services import coingecko

router = APIRouter()


@router.get("/", response_model=List[schemas.Coin])
async def get_coins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all coins
    """
    coins = db.query(models.Coin).offset(skip).limit(limit).all()
    return coins


@router.get("/{coin_id}", response_model=schemas.Coin)
async def get_coin(coin_id: int, db: Session = Depends(get_db)):
    """
    Get a coin by ID
    """
    coin = db.query(models.Coin).filter(models.Coin.id == coin_id).first()
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    return coin


@router.get("/by-coingecko-id/{coingecko_id}", response_model=schemas.Coin)
async def get_coin_by_coingecko_id(coingecko_id: str, db: Session = Depends(get_db)):
    """
    Get a coin by Coingecko ID
    """
    coin = db.query(models.Coin).filter(models.Coin.coingecko_id == coingecko_id).first()
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    return coin


@router.post("/", response_model=schemas.Coin)
async def create_coin(coin: schemas.CoinCreate, db: Session = Depends(get_db)):
    """
    Create a new coin
    """
    db_coin = models.Coin(**coin.model_dump())
    db.add(db_coin)
    db.commit()
    db.refresh(db_coin)
    return db_coin


@router.get("/sync/top", response_model=List[schemas.Coin])
async def sync_top_coins_from_coingecko(limit: int = 20, db: Session = Depends(get_db)):
    """
    Sync top coins from Coingecko API
    """
    try:
        coins_data = await coingecko.get_coins()
        
        # We'll only sync the first few coins as an example
        # In a real app, you'd want to use the /coins/markets endpoint to get top coins by market cap
        top_coins = coins_data[:limit]
        
        # Create or update coins
        added_coins = []
        for coin_data in top_coins:
            db_coin = db.query(models.Coin).filter(models.Coin.coingecko_id == coin_data["id"]).first()
            
            if not db_coin:
                db_coin = models.Coin(
                    coingecko_id=coin_data["id"],
                    symbol=coin_data["symbol"].upper(),
                    name=coin_data["name"]
                )
                db.add(db_coin)
                db.commit()
                db.refresh(db_coin)
                added_coins.append(db_coin)
        
        return added_coins
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing coins: {str(e)}") 