from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
import datetime
from datetime import timezone

from app.database.connection import Base

def utcnow():
    """Return timezone-aware UTC datetime"""
    return datetime.datetime.now(timezone.utc)

class Exchange(Base):
    """Exchange model"""
    __tablename__ = "exchanges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    website = Column(String, nullable=True)
    api_url = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    has_trading_fees = Column(Boolean, default=True)
    has_withdrawal_fees = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    prices = relationship("Price", back_populates="exchange")
    
    def __repr__(self):
        return f"<Exchange {self.name}>"


class Coin(Base):
    """Cryptocurrency model"""
    __tablename__ = "coins"
    
    id = Column(Integer, primary_key=True, index=True)
    coingecko_id = Column(String, unique=True, index=True, nullable=False)
    symbol = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    logo_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    prices = relationship("Price", back_populates="coin")
    
    def __repr__(self):
        return f"<Coin {self.symbol}>"


class Price(Base):
    """Price data model for coin on exchange"""
    __tablename__ = "prices"
    
    id = Column(Integer, primary_key=True, index=True)
    exchange_id = Column(Integer, ForeignKey("exchanges.id"), nullable=False)
    coin_id = Column(Integer, ForeignKey("coins.id"), nullable=False)
    price_usd = Column(Float, nullable=False)
    volume_24h = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=utcnow)
    bid_price = Column(Float, nullable=True)
    ask_price = Column(Float, nullable=True)
    trading_fee = Column(Float, nullable=True)  # As percentage
    withdrawal_fee = Column(Float, nullable=True)  # In USD
    
    # Relationships
    exchange = relationship("Exchange", back_populates="prices")
    coin = relationship("Coin", back_populates="prices")
    
    # Unique constraint to ensure one price record per exchange/coin pair
    __table_args__ = (
        UniqueConstraint('exchange_id', 'coin_id', name='_exchange_coin_uc'),
    )
    
    def __repr__(self):
        return f"<Price {self.exchange_id}:{self.coin_id}>" 