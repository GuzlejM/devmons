import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.models import Exchange

def test_get_exchanges_empty(client, test_db):
    """Test getting exchanges when there are none"""
    response = client.get("/exchanges/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_exchange(client, test_db):
    """Test creating a new exchange"""
    exchange_data = {
        "name": "Test Exchange",
        "website": "https://test-exchange.com",
        "api_url": "https://api.test-exchange.com",
        "logo_url": "https://test-exchange.com/logo.png",
        "has_trading_fees": True,
        "has_withdrawal_fees": True
    }
    
    response = client.post("/exchanges/", json=exchange_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == exchange_data["name"]
    assert data["website"] == exchange_data["website"]
    assert data["id"] == 1
    
    # Verify it's in the database
    db_exchange = test_db.query(Exchange).filter(Exchange.id == 1).first()
    assert db_exchange is not None
    assert db_exchange.name == exchange_data["name"]

def test_get_exchange_by_id(client, test_db):
    """Test getting an exchange by ID"""
    # First create an exchange
    exchange = Exchange(
        name="Binance",
        website="https://binance.com",
        logo_url="https://binance.com/logo.png"
    )
    test_db.add(exchange)
    test_db.commit()
    
    # Now get it by ID
    response = client.get(f"/exchanges/{exchange.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == exchange.name
    assert data["website"] == exchange.website

def test_get_exchange_not_found(client, test_db):
    """Test getting a non-existent exchange"""
    response = client.get("/exchanges/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower() 