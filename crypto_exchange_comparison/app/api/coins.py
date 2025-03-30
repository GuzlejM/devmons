from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database.connection import get_db
from app.models import models, schemas
from app.services import coingecko
from app.services.cache import invalidate_cache

router = APIRouter()


@router.get("/", response_model=List[schemas.Coin])
async def get_coins(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    """
    Get all coins
    """
    coins = db.query(models.Coin).offset(skip).limit(limit).all()
    return coins


@router.get("/search", response_model=List[dict])
async def search_available_coins(
    query: str = Query(..., min_length=2), 
    limit: int = 20, 
    db: Session = Depends(get_db)
):
    """
    Search for coins on CoinGecko that aren't already in the database
    """
    try:
        # Get current coins in database
        db_coins = db.query(models.Coin.coingecko_id).all()
        existing_coin_ids = {coin.coingecko_id for coin in db_coins}
        
        # First get coins with market data (which have price information)
        market_coins = await coingecko.get_coins_with_market_data(per_page=250)
        
        # Create a lookup for quick access
        market_coins_by_id = {coin["id"]: coin for coin in market_coins}
        
        # Get the full list of coins for broader search
        all_coins = await coingecko.get_coins()
        
        # Filter coins that match the query in id, name, or symbol
        # and aren't already in the database
        query = query.lower()
        matching_coins = []
        
        for coin in all_coins:
            # Skip if already in database
            if coin["id"] in existing_coin_ids:
                continue
                
            if (query in coin["id"].lower() or 
                query in coin["symbol"].lower() or 
                query in coin["name"].lower()):
                
                # Check if this coin has market data
                market_data = market_coins_by_id.get(coin["id"])
                
                result = {
                    "id": coin["id"],
                    "symbol": coin["symbol"],
                    "name": coin["name"],
                    "has_market_data": market_data is not None
                }
                
                # Add market data if available
                if market_data:
                    result.update({
                        "current_price": market_data.get("current_price"),
                        "market_cap": market_data.get("market_cap"),
                        "image": market_data.get("image"),
                        "price_change_24h": market_data.get("price_change_percentage_24h")
                    })
                
                matching_coins.append(result)
        
        # Sort by best match and whether they have market data
        def get_sort_key(coin):
            # Has market data gets highest priority
            has_market_data = 0 if coin.get("has_market_data") else 1
            
            # Exact matches get next priority
            if coin["id"].lower() == query or coin["symbol"].lower() == query or coin["name"].lower() == query:
                return (has_market_data, 0)
                
            # Starts with query gets next priority  
            if coin["id"].lower().startswith(query) or coin["symbol"].lower().startswith(query) or coin["name"].lower().startswith(query):
                return (has_market_data, 1)
                
            # Contains query gets lowest priority
            return (has_market_data, 2)
            
        matching_coins.sort(key=get_sort_key)
        
        # Limit to top results
        return matching_coins[:limit]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching coins: {str(e)}"
        )


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
    # Check if coin already exists
    existing_coin = db.query(models.Coin).filter(models.Coin.coingecko_id == coin.coingecko_id).first()
    if existing_coin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Coin '{coin.name}' ({coin.symbol}) already exists in the system"
        )
    
    # Verify coin exists in CoinGecko
    try:
        coin_data = await coingecko.get_coin_price(coin.coingecko_id)
        if not coin_data or coin.coingecko_id not in coin_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Coin with ID '{coin.coingecko_id}' not found on CoinGecko"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying coin on CoinGecko: {str(e)}"
        )
    
    # Create the coin in the database
    try:
        db_coin = models.Coin(**coin.model_dump())
        db.add(db_coin)
        db.commit()
        db.refresh(db_coin)
        return db_coin
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating coin: {str(e)}"
        )


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


@router.put("/{coin_id}", response_model=schemas.Coin)
async def update_coin(coin_id: int, coin_update: schemas.CoinUpdate, db: Session = Depends(get_db)):
    """
    Update a coin
    """
    db_coin = db.query(models.Coin).filter(models.Coin.id == coin_id).first()
    if not db_coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    
    # Update coin attributes
    update_data = coin_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_coin, key, value)
    
    db.commit()
    db.refresh(db_coin)
    return db_coin


@router.delete("/{coin_id}", response_model=schemas.Coin)
async def delete_coin(coin_id: int, db: Session = Depends(get_db)):
    """
    Delete a coin
    """
    db_coin = db.query(models.Coin).filter(models.Coin.id == coin_id).first()
    if not db_coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    
    try:
        db.delete(db_coin)
        db.commit()
        return db_coin
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting coin: {str(e)}"
        ) 