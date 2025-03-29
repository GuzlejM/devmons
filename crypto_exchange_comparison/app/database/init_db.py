from sqlalchemy.orm import Session
import requests
import time
from app.models.models import Base, Exchange, Coin, Price
from app.database.connection import engine, get_db

def init_db():
    """Initialize the database with tables"""
    Base.metadata.create_all(bind=engine)
    
    # Add seed data
    db = next(get_db())
    fetch_and_save_data(db)
    
def fetch_and_save_data(db: Session):
    """Fetch data from CoinGecko API and save to database"""
    # Check if we already have coins
    existing_coins = db.query(Coin).count()
    if existing_coins > 0:
        print("Database already contains coin data")
        return
    
    # Fetch top coins from CoinGecko
    try:
        print("Fetching coin data from CoinGecko API...")
        response = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 50,
                "page": 1
            }
        )
        response.raise_for_status()
        coins_data = response.json()
        
        coins = []
        for coin_data in coins_data:
            coin = Coin(
                coingecko_id=coin_data["id"],
                symbol=coin_data["symbol"].upper(),
                name=coin_data["name"],
                logo_url=coin_data.get("image")
            )
            coins.append(coin)
        
        db.add_all(coins)
        db.commit()
        print(f"Successfully added {len(coins)} coins from CoinGecko")
        
        # Wait to avoid rate limiting
        time.sleep(1)
        
        # Add popular exchanges
        add_exchanges(db)
        
    except Exception as e:
        print(f"Error fetching data from CoinGecko API: {e}")
        # Fallback to sample data if API fails
        add_sample_data(db)

def add_exchanges(db: Session):
    """Add popular cryptocurrency exchanges"""
    existing_exchanges = db.query(Exchange).count()
    if existing_exchanges > 0:
        return
    
    try:
        print("Fetching exchange data from CoinGecko API...")
        response = requests.get("https://api.coingecko.com/api/v3/exchanges")
        response.raise_for_status()
        exchanges_data = response.json()
        
        # Add top 20 exchanges
        exchanges = []
        for exchange_data in exchanges_data[:20]:
            exchange = Exchange(
                name=exchange_data["name"],
                website=exchange_data.get("url"),
                api_url=None,  # CoinGecko doesn't provide API URLs for exchanges
                logo_url=exchange_data.get("image")
            )
            exchanges.append(exchange)
        
        db.add_all(exchanges)
        db.commit()
        print(f"Successfully added {len(exchanges)} exchanges from CoinGecko")
    except Exception as e:
        print(f"Error fetching exchanges from CoinGecko API: {e}")
        # Fallback to sample exchanges
        add_sample_exchanges(db)

def add_sample_data(db: Session):
    """Add sample data as fallback if API fetching fails"""
    print("Using fallback sample coin data...")
    sample_coins = [
        Coin(coingecko_id="bitcoin", symbol="BTC", name="Bitcoin"),
        Coin(coingecko_id="ethereum", symbol="ETH", name="Ethereum"),
        Coin(coingecko_id="ripple", symbol="XRP", name="XRP"),
        Coin(coingecko_id="cardano", symbol="ADA", name="Cardano"),
        Coin(coingecko_id="solana", symbol="SOL", name="Solana"),
        Coin(coingecko_id="dogecoin", symbol="DOGE", name="Dogecoin"),
        Coin(coingecko_id="polkadot", symbol="DOT", name="Polkadot"),
        Coin(coingecko_id="chainlink", symbol="LINK", name="Chainlink"),
    ]
    
    db.add_all(sample_coins)
    db.commit()
    print("Added sample coin data")
    
    add_sample_exchanges(db)

def add_sample_exchanges(db: Session):
    """Add sample exchange data as fallback"""
    print("Using fallback sample exchange data...")
    sample_exchanges = [
        Exchange(name="Binance", website="https://www.binance.com", api_url="https://api.binance.com"),
        Exchange(name="Coinbase", website="https://www.coinbase.com", api_url="https://api.coinbase.com"),
        Exchange(name="Kraken", website="https://www.kraken.com", api_url="https://api.kraken.com"),
        Exchange(name="Bitfinex", website="https://www.bitfinex.com", api_url="https://api.bitfinex.com"),
        Exchange(name="Bitstamp", website="https://www.bitstamp.net", api_url="https://api.bitstamp.net"),
    ]
    
    db.add_all(sample_exchanges)
    db.commit()
    print("Added sample exchange data")

if __name__ == "__main__":
    init_db()
    print("Database tables created.") 