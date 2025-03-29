# Crypto Exchange Comparison API

A simple API for comparing cryptocurrency prices, fees, and liquidity across different exchanges.

## Features

- Compare cryptocurrency prices across multiple exchanges
- View trading fees and withdrawal fees for exchanges
- Find the best exchange for buying or selling specific cryptocurrencies
- Historical price data for exchanges

## Technology Stack

- Python 3.9+
- FastAPI
- PostgreSQL
- Redis (for caching)
- SQLAlchemy
- Docker & Docker Compose

## Setup

### Using Docker

1. Clone the repository
2. Run `docker-compose up -d`
3. API will be available at http://localhost:8000
4. Swagger documentation at http://localhost:8000/docs

### Local Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up PostgreSQL and Redis locally
6. Run the application: `uvicorn app.main:app --reload`

## API Endpoints

- `GET /exchanges` - List all exchanges
- `GET /coins` - List all supported cryptocurrencies
- `GET /compare/{coin_id}` - Compare prices across exchanges
- `GET /fees/{exchange_id}` - Get fee structure for an exchange

## Testing

Run tests with pytest:

```
pytest tests/
```

## License

MIT
