import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock

from app.models.models import Coin, Exchange, Price
from app.services import coingecko

# Mock data for Coingecko API responses
MOCK_COIN_PRICE = {
    "bitcoin": {
        "usd": 50000,
        "usd_24h_vol": 2000000000,
        "usd_market_cap": 1000000000000
    },
    "ethereum": {
        "usd": 3000,
        "usd_24h_vol": 1000000000,
        "usd_market_cap": 500000000000
    }
}

MOCK_TICKERS = {
    "name": "Bitcoin",
    "tickers": [
        {
            "market": {"name": "Binance"},
            "converted_last": {"usd": 50000},
            "converted_volume": {"usd": 500000000},
            "bid": 49900,
            "ask": 50100,
            "bid_ask_spread_percentage": 0.4
        },
        {
            "market": {"name": "Coinbase"},
            "converted_last": {"usd": 50050},
            "converted_volume": {"usd": 400000000},
            "bid": 49950,
            "ask": 50150,
            "bid_ask_spread_percentage": 0.4
        }
    ]
}

MOCK_ETH_TICKERS = {
    "name": "Ethereum",
    "tickers": [
        {
            "market": {"name": "Binance", "identifier": "binance"},
            "converted_last": {"usd": 3000},
            "converted_volume": {"usd": 200000000},
            "bid": 2990,
            "ask": 3010,
            "bid_ask_spread_percentage": 0.4
        },
        {
            "market": {"name": "Coinbase", "identifier": "coinbase"},
            "converted_last": {"usd": 3005},
            "converted_volume": {"usd": 190000000},
            "bid": 2995,
            "ask": 3015,
            "bid_ask_spread_percentage": 0.4
        }
    ]
}

@pytest.fixture
def mock_redis():
    """Fixture to mock Redis client"""
    with patch('app.services.cache.redis_client') as mock_redis:
        # Configure the mock redis client behavior
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        yield mock_redis

@pytest.fixture
def mock_coingecko_responses():
    """Fixture to mock Coingecko API responses"""
    with patch('app.services.coingecko.get_coin_price') as mock_price, \
         patch('app.services.coingecko.get_coin_tickers') as mock_tickers:
        
        # Configure mock to return appropriate response based on coin_id
        async def mock_get_coin_price(coin_id, *args, **kwargs):
            if coin_id == "ethereum":
                return {"ethereum": MOCK_COIN_PRICE["ethereum"]}
            return {"bitcoin": MOCK_COIN_PRICE["bitcoin"]}
            
        async def mock_get_coin_tickers(coin_id, *args, **kwargs):
            if coin_id == "ethereum":
                return MOCK_ETH_TICKERS
            return MOCK_TICKERS
        
        mock_price.side_effect = mock_get_coin_price
        mock_tickers.side_effect = mock_get_coin_tickers
        
        yield

@pytest.fixture
def seed_database(test_db):
    """Seed the database with test data"""
    # Add exchanges
    binance = Exchange(name="Binance", website="https://binance.com")
    coinbase = Exchange(name="Coinbase", website="https://coinbase.com")
    test_db.add(binance)
    test_db.add(coinbase)
    
    # Add a coin
    bitcoin = Coin(coingecko_id="bitcoin", symbol="BTC", name="Bitcoin")
    test_db.add(bitcoin)
    
    test_db.commit()
    
    # Add price data
    price1 = Price(
        exchange_id=binance.id,
        coin_id=bitcoin.id,
        price_usd=50000,
        volume_24h=500000000,
        bid_price=49900,
        ask_price=50100,
        trading_fee=0.1
    )
    
    price2 = Price(
        exchange_id=coinbase.id,
        coin_id=bitcoin.id,
        price_usd=50050,
        volume_24h=400000000,
        bid_price=49950,
        ask_price=50150,
        trading_fee=0.2
    )
    
    test_db.add(price1)
    test_db.add(price2)
    test_db.commit()
    
    return {"binance": binance, "coinbase": coinbase, "bitcoin": bitcoin}

def test_compare_exchanges_existing_coin(client, test_db, seed_database, mock_coingecko_responses, mock_redis):
    """Test comparing exchanges for an existing coin"""
    bitcoin = seed_database["bitcoin"]
    
    response = client.get(f"/compare/{bitcoin.coingecko_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["coin"] == bitcoin.name
    assert len(data["exchanges"]) == 2
    assert data["best_price"]["exchange_name"] == "Binance"
    assert data["best_for_large_orders"]["exchange_name"] == "Binance"

@patch('app.services.cache.get_cache')
@patch('app.services.cache.set_cache')
def test_compare_exchanges_new_coin(mock_set_cache, mock_get_cache, client, test_db, mock_coingecko_responses, mock_redis):
    """Test comparing exchanges for a new coin that needs to be fetched from Coingecko"""
    # Ensure cache returns None
    mock_get_cache.return_value = None
    
    response = client.get("/compare/ethereum")
    
    assert response.status_code == 200
    data = response.json()
    
    # The coin should have been created and the comparison should work
    assert data["coin"] == "Ethereum"  # Capitalized in our mock
    assert len(data["exchanges"]) == 2
    
    # Verify the coin was added to the database
    db_coin = test_db.query(Coin).filter(Coin.coingecko_id == "ethereum").first()
    assert db_coin is not None

def test_get_exchange_fees(client, test_db, seed_database):
    """Test getting fee structure for an exchange"""
    binance = seed_database["binance"]
    
    response = client.get(f"/compare/fees/{binance.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1  # Only one coin with fee data
    assert data[0]["coin"] == "BTC"
    assert data[0]["trading_fee"] == 0.1 