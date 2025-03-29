import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch

from app.models.models import Coin

def test_get_coins_empty(client, test_db):
    """Test getting coins when there are none"""
    response = client.get("/coins/")
    assert response.status_code == 200
    assert response.json() == []

@patch('app.services.coingecko.get_coin_price')
def test_create_coin(mock_get_coin_price, client, test_db):
    """Test creating a new coin"""
    # Mock the CoinGecko API response
    async def mock_coin_price(*args, **kwargs):
        return {"bitcoin": {"usd": 50000}}
    
    mock_get_coin_price.side_effect = mock_coin_price
    
    coin_data = {
        "coingecko_id": "bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
        "logo_url": "https://example.com/btc.png"
    }
    
    response = client.post("/coins/", json=coin_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["coingecko_id"] == coin_data["coingecko_id"]
    assert data["symbol"] == coin_data["symbol"]
    assert data["name"] == coin_data["name"]
    assert data["id"] == 1
    
    # Verify it's in the database
    db_coin = test_db.query(Coin).filter(Coin.id == 1).first()
    assert db_coin is not None
    assert db_coin.coingecko_id == coin_data["coingecko_id"]

@patch('app.services.coingecko.get_coin_price')
def test_create_coin_invalid_coingecko_id(mock_get_coin_price, client, test_db):
    """Test creating a coin with an invalid CoinGecko ID"""
    # Mock the CoinGecko API response for non-existent coin
    async def mock_coin_price(*args, **kwargs):
        # Return empty dict for specific coin, which will trigger the "not found" check
        return {}
    
    mock_get_coin_price.side_effect = mock_coin_price
    
    coin_data = {
        "coingecko_id": "nonexistentcoin",
        "symbol": "FAKE",
        "name": "Fake Coin",
        "logo_url": "https://example.com/fake.png"
    }
    
    response = client.post("/coins/", json=coin_data)
    
    # Should return an error status code
    assert response.status_code >= 400
    
    # Verify it's not in the database
    db_coin = test_db.query(Coin).filter(Coin.coingecko_id == coin_data["coingecko_id"]).first()
    assert db_coin is None

def test_get_coin_by_id(client, test_db):
    """Test getting a coin by ID"""
    # First create a coin
    coin = Coin(
        coingecko_id="ethereum",
        symbol="ETH",
        name="Ethereum"
    )
    test_db.add(coin)
    test_db.commit()
    
    # Now get it by ID
    response = client.get(f"/coins/{coin.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["coingecko_id"] == coin.coingecko_id
    assert data["symbol"] == coin.symbol
    assert data["name"] == coin.name

def test_get_coin_by_coingecko_id(client, test_db):
    """Test getting a coin by Coingecko ID"""
    # First create a coin
    coin = Coin(
        coingecko_id="cardano",
        symbol="ADA",
        name="Cardano"
    )
    test_db.add(coin)
    test_db.commit()
    
    # Now get it by Coingecko ID
    response = client.get(f"/coins/by-coingecko-id/{coin.coingecko_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["coingecko_id"] == coin.coingecko_id
    assert data["symbol"] == coin.symbol
    assert data["name"] == coin.name

def test_get_coin_not_found(client, test_db):
    """Test getting a non-existent coin"""
    response = client.get("/coins/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_update_coin(client, test_db):
    """Test updating a coin"""
    # First create a coin
    coin = Coin(
        coingecko_id="litecoin",
        symbol="LTC",
        name="Litecoin"
    )
    test_db.add(coin)
    test_db.commit()
    
    # Update the coin
    update_data = {
        "symbol": "LTC-UPDATED",
        "name": "Litecoin Updated",
        "logo_url": "https://example.com/ltc-updated.png"
    }
    
    response = client.put(f"/coins/{coin.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == update_data["symbol"]
    assert data["name"] == update_data["name"]
    assert data["logo_url"] == update_data["logo_url"]
    
    # Verify change in database
    db_coin = test_db.query(Coin).filter(Coin.id == coin.id).first()
    assert db_coin.symbol == update_data["symbol"]
    assert db_coin.name == update_data["name"]
    assert db_coin.logo_url == update_data["logo_url"]

def test_delete_coin(client, test_db):
    """Test deleting a coin"""
    # First create a coin
    coin = Coin(
        coingecko_id="dogecoin",
        symbol="DOGE",
        name="Dogecoin"
    )
    test_db.add(coin)
    test_db.commit()
    
    # Delete the coin
    response = client.delete(f"/coins/{coin.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == coin.id
    
    # Verify it's gone from the database
    db_coin = test_db.query(Coin).filter(Coin.id == coin.id).first()
    assert db_coin is None 