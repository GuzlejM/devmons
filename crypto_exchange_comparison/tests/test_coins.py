import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.models import Coin

def test_get_coins_empty(client, test_db):
    """Test getting coins when there are none"""
    response = client.get("/coins/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_coin(client, test_db):
    """Test creating a new coin"""
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