import httpx
from typing import Dict, List, Any, Optional
import asyncio

from app.services.cache import get_cache, set_cache

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
CACHE_PREFIX = "coingecko"


async def get_coins() -> List[Dict[str, Any]]:
    """
    Get list of all coins from Coingecko API with cache
    """
    cache_key = f"{CACHE_PREFIX}:coins"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{COINGECKO_API_URL}/coins/list")
        response.raise_for_status()
        coins = response.json()
        
        # Cache the result
        set_cache(cache_key, coins, 86400)  # Cache for 24 hours
        
        return coins


async def get_exchanges() -> List[Dict[str, Any]]:
    """
    Get list of all exchanges from Coingecko API with cache
    """
    cache_key = f"{CACHE_PREFIX}:exchanges"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{COINGECKO_API_URL}/exchanges")
        response.raise_for_status()
        exchanges = response.json()
        
        # Cache the result
        set_cache(cache_key, exchanges, 86400)  # Cache for 24 hours
        
        return exchanges


async def get_coin_price(coin_id: str, vs_currencies: str = "usd") -> Dict[str, Dict[str, float]]:
    """
    Get price of a specific coin
    """
    cache_key = f"{CACHE_PREFIX}:price:{coin_id}:{vs_currencies}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{COINGECKO_API_URL}/simple/price",
            params={
                "ids": coin_id,
                "vs_currencies": vs_currencies,
                "include_24hr_vol": "true",
                "include_market_cap": "true"
            }
        )
        response.raise_for_status()
        price_data = response.json()
        
        # Cache the result
        set_cache(cache_key, price_data, 300)  # Cache for 5 minutes
        
        return price_data


async def get_coin_tickers(coin_id: str) -> Dict[str, Any]:
    """
    Get tickers (exchange data) for a specific coin
    """
    cache_key = f"{CACHE_PREFIX}:tickers:{coin_id}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{COINGECKO_API_URL}/coins/{coin_id}/tickers")
        response.raise_for_status()
        ticker_data = response.json()
        
        # Cache the result
        set_cache(cache_key, ticker_data, 300)  # Cache for 5 minutes
        
        return ticker_data 