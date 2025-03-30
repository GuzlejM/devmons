import httpx
from typing import Dict, List, Any, Optional
import asyncio
import random
import time
from fastapi import HTTPException, status

from app.services.cache import get_cache, set_cache

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
CACHE_PREFIX = "coingecko"
MAX_RETRIES = 3

async def make_api_request(url: str, params: Optional[Dict[str, Any]] = None):
    """
    Make a request to CoinGecko API with retry logic for rate limiting
    """
    retry_count = 0
    base_delay = 1  # Base delay in seconds
    
    while retry_count < MAX_RETRIES:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                
                if response.status_code == 429:  # Too Many Requests
                    retry_count += 1
                    if retry_count >= MAX_RETRIES:
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"CoinGecko API rate limit exceeded after {MAX_RETRIES} retries"
                        )
                    
                    # Exponential backoff with jitter
                    delay = base_delay * (2 ** retry_count) + random.uniform(0, 1)
                    print(f"Rate limited by CoinGecko, retrying in {delay:.2f} seconds...")
                    await asyncio.sleep(delay)
                    continue
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Too Many Requests
                retry_count += 1
                if retry_count >= MAX_RETRIES:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=f"CoinGecko API rate limit exceeded after {MAX_RETRIES} retries"
                    )
                
                # Exponential backoff with jitter
                delay = base_delay * (2 ** retry_count) + random.uniform(0, 1)
                print(f"Rate limited by CoinGecko, retrying in {delay:.2f} seconds...")
                await asyncio.sleep(delay)
            else:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Error from CoinGecko API: {str(e)}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch data from CoinGecko: {str(e)}"
            )

async def get_coins() -> List[Dict[str, Any]]:
    """
    Get list of all coins from Coingecko API with cache
    """
    cache_key = f"{CACHE_PREFIX}:coins"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    result = await make_api_request(f"{COINGECKO_API_URL}/coins/list")
    
    # Cache the result
    set_cache(cache_key, result, 86400)  # Cache for 24 hours
    
    return result


async def get_exchanges() -> List[Dict[str, Any]]:
    """
    Get list of all exchanges from Coingecko API with cache
    """
    cache_key = f"{CACHE_PREFIX}:exchanges"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    result = await make_api_request(f"{COINGECKO_API_URL}/exchanges")
    
    # Cache the result
    set_cache(cache_key, result, 86400)  # Cache for 24 hours
    
    return result


async def get_coin_price(coin_id: str, vs_currencies: str = "usd") -> Dict[str, Dict[str, float]]:
    """
    Get price of a specific coin
    """
    cache_key = f"{CACHE_PREFIX}:price:{coin_id}:{vs_currencies}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    params = {
        "ids": coin_id,
        "vs_currencies": vs_currencies,
        "include_24hr_vol": "true",
        "include_market_cap": "true"
    }
    
    result = await make_api_request(f"{COINGECKO_API_URL}/simple/price", params)
    
    # Cache the result
    set_cache(cache_key, result, 300)  # Cache for 5 minutes
    
    return result


async def get_coin_tickers(coin_id: str) -> Dict[str, Any]:
    """
    Get tickers (exchange data) for a specific coin
    """
    cache_key = f"{CACHE_PREFIX}:tickers:{coin_id}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    result = await make_api_request(f"{COINGECKO_API_URL}/coins/{coin_id}/tickers")
    
    # Cache the result
    set_cache(cache_key, result, 300)  # Cache for 5 minutes
    
    return result


async def get_coins_with_market_data(vs_currency: str = "usd", per_page: int = 250, page: int = 1) -> List[Dict[str, Any]]:
    """
    Get list of coins with market data from CoinGecko API with cache
    
    This provides coins with actual price data, market cap, etc.
    """
    cache_key = f"{CACHE_PREFIX}:markets:{vs_currency}:{per_page}:{page}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    params = {
        "vs_currency": vs_currency,
        "per_page": per_page,
        "page": page,
        "sparkline": "false",
        "price_change_percentage": "24h"
    }
    
    result = await make_api_request(f"{COINGECKO_API_URL}/coins/markets", params)
    
    # Cache the result
    set_cache(cache_key, result, 300)  # Cache for 5 minutes (more frequent updates for price data)
    
    return result 