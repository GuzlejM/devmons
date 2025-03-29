from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import get_db
from app.api import exchanges, coins, compare
from app.database.init_db import init_db

app = FastAPI(
    title="Crypto Exchange Comparison API",
    description="API for comparing cryptocurrency prices across exchanges",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(exchanges.router, prefix="/exchanges", tags=["exchanges"])
app.include_router(coins.router, prefix="/coins", tags=["coins"])
app.include_router(compare.router, prefix="/compare", tags=["compare"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("Database tables initialized at startup")

@app.get("/", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "API is running"}
