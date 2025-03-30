"""
Service for processing data from the CoinGecko API.
"""
from typing import Dict, Any, List, Tuple, Optional

from app.services import coingecko


async def fetch_top_coins(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch top coins from CoinGecko API.
    
    Args:
        limit: Maximum number of coins to fetch
        
    Returns:
        List of coin data dictionaries
    """
    coins_data = await coingecko.get_coins()
    return coins_data[:limit]


async def fetch_top_exchanges(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Fetch top exchanges from CoinGecko API.
    
    Args:
        limit: Maximum number of exchanges to fetch
        
    Returns:
        List of exchange data dictionaries
    """
    exchanges_data = await coingecko.get_exchanges()
    return exchanges_data[:limit]


async def fetch_coin_tickers(coin_id: str) -> Dict[str, Any]:
    """
    Fetch ticker data for a specific coin.
    
    Args:
        coin_id: CoinGecko ID of the coin
        
    Returns:
        Dictionary with ticker data
    """
    return await coingecko.get_coin_tickers(coin_id)


def extract_ticker_data(ticker: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant data from a ticker object.
    
    Args:
        ticker: Ticker data from CoinGecko API
        
    Returns:
        Dictionary with extracted ticker data
    """
    exchange_name = ticker.get("market", {}).get("name")
    if not exchange_name:
        return {}
    
    return {
        "name": exchange_name,
        "price": ticker.get("converted_last", {}).get("usd", 0),
        "volume": ticker.get("converted_volume", {}).get("usd", 0),
        "bid": ticker.get("bid"),
        "ask": ticker.get("ask"),
        "ticker": ticker
    }


def filter_best_tickers(tickers: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Filter tickers to keep only the highest volume ticker for each exchange.
    
    Args:
        tickers: List of ticker data
        
    Returns:
        Dictionary of exchange data keyed by exchange name
    """
    exchange_data = {}
    
    for ticker in tickers:
        ticker_data = extract_ticker_data(ticker)
        if not ticker_data:
            continue
            
        exchange_name = ticker_data["name"]
        volume = ticker_data["volume"]
        
        # If we've seen this exchange before, only keep the highest volume entry
        if exchange_name in exchange_data and volume <= exchange_data[exchange_name]["volume"]:
            continue
        
        # Store this exchange data
        exchange_data[exchange_name] = ticker_data
    
    return exchange_data 