"""
Service for analyzing and sorting exchange data.
"""
from typing import Dict, Any, List, Optional

from app.models import schemas


def calculate_spread(bid_price: Optional[float], ask_price: Optional[float]) -> Optional[float]:
    """
    Calculate spread percentage between bid and ask prices.
    
    Args:
        bid_price: Bid price
        ask_price: Ask price
        
    Returns:
        Spread percentage or None if prices are not available
    """
    if bid_price and ask_price:
        return abs(ask_price - bid_price) / ((ask_price + bid_price) / 2) * 100
    return None


def process_ticker_data(ticker_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Process ticker data from CoinGecko to extract exchange information.
    
    Args:
        ticker_data: Raw ticker data from CoinGecko API
        
    Returns:
        Dictionary of exchange data keyed by exchange name
    """
    exchange_data = {}
    
    for ticker in ticker_data.get("tickers", []):
        exchange_name = ticker.get("market", {}).get("name")
        if not exchange_name:
            continue
        
        # Get exchange volume for this ticker
        volume = ticker.get("converted_volume", {}).get("usd", 0)
        
        # If we've seen this exchange before, only keep the highest volume entry
        if exchange_name in exchange_data and volume <= exchange_data[exchange_name]["volume"]:
            continue
        
        # Store this exchange data
        exchange_data[exchange_name] = {
            "name": exchange_name,
            "price": ticker.get("converted_last", {}).get("usd", 0),
            "volume": volume,
            "bid": ticker.get("bid"),
            "ask": ticker.get("ask"),
            "spread": ticker.get("bid_ask_spread_percentage"),
            "ticker": ticker
        }
    
    return exchange_data


def sort_exchanges_by_price(
    exchange_prices: List[schemas.ExchangePrice]
) -> List[schemas.ExchangePrice]:
    """
    Sort exchanges by price.
    
    Args:
        exchange_prices: List of exchange price DTOs
        
    Returns:
        Sorted list of exchange price DTOs
    """
    return sorted(exchange_prices, key=lambda x: x.price_usd)


def find_best_volume_exchange(
    exchange_prices: List[schemas.ExchangePrice]
) -> Optional[schemas.ExchangePrice]:
    """
    Find the exchange with the highest trading volume.
    
    Args:
        exchange_prices: List of exchange price DTOs
        
    Returns:
        Exchange price DTO with highest volume or None if list is empty
    """
    if not exchange_prices:
        return None
        
    return sorted(
        exchange_prices,
        key=lambda x: x.volume_24h if x.volume_24h else 0,
        reverse=True
    )[0]


def build_comparison_result(
    coin_name: str,
    exchange_prices: List[schemas.ExchangePrice]
) -> schemas.ComparisonResult:
    """
    Build the final comparison result object.
    
    Args:
        coin_name: Name of the coin
        exchange_prices: List of exchange price DTOs
        
    Returns:
        Comparison result DTO
    """
    sorted_prices = sort_exchanges_by_price(exchange_prices)
    best_volume = find_best_volume_exchange(exchange_prices)
    
    return schemas.ComparisonResult(
        coin=coin_name,
        exchanges=sorted_prices,
        best_price=sorted_prices[0] if sorted_prices else None,
        best_for_large_orders=best_volume
    ) 