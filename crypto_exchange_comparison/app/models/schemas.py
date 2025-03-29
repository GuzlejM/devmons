from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class ExchangeBase(BaseModel):
    name: str
    website: Optional[str] = None
    api_url: Optional[str] = None
    logo_url: Optional[str] = None
    has_trading_fees: bool = True
    has_withdrawal_fees: bool = True


class ExchangeCreate(ExchangeBase):
    pass


class Exchange(ExchangeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CoinBase(BaseModel):
    coingecko_id: str
    symbol: str
    name: str
    logo_url: Optional[str] = None


class CoinCreate(CoinBase):
    pass


class Coin(CoinBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PriceBase(BaseModel):
    exchange_id: int
    coin_id: int
    price_usd: float
    volume_24h: Optional[float] = None
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    trading_fee: Optional[float] = None
    withdrawal_fee: Optional[float] = None


class PriceCreate(PriceBase):
    pass


class Price(PriceBase):
    id: int
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


class ExchangePrice(BaseModel):
    exchange_name: str
    price_usd: float
    volume_24h: Optional[float] = None
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    trading_fee: Optional[float] = None
    withdrawal_fee: Optional[float] = None
    last_updated: datetime
    spread: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


class ComparisonResult(BaseModel):
    coin: str
    exchanges: List[ExchangePrice]
    best_price: ExchangePrice
    best_for_large_orders: Optional[ExchangePrice] = None 