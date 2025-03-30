from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from app.database.connection import get_db
from app.api import exchanges, coins, compare
from app.database.init_db import init_db
from app.tasks import scheduler, cleanup
from app.services.db import price_service

app = FastAPI(
    title="Crypto Exchange Comparison API",
    description="API for comparing cryptocurrency prices across exchanges",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only - in production, specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(exchanges.router, prefix="/exchanges", tags=["exchanges"])
app.include_router(coins.router, prefix="/coins", tags=["coins"])
app.include_router(compare.router, prefix="/compare", tags=["compare"])
app.include_router(cleanup.router, prefix="/maintenance", tags=["maintenance"])

@app.get("/update", tags=["maintenance"])
async def trigger_updates(background_tasks: BackgroundTasks):
    """
    Manually trigger data updates in the background.
    
    Returns:
        Status message
    """
    return scheduler.schedule_updates(background_tasks)

@app.get("/update/status", tags=["maintenance"])
async def update_status():
    """
    Get the status of the last data updates.
    
    Returns:
        Dictionary with last update times for each data type
    """
    return scheduler.get_last_update_times()

async def startup_tasks():
    """
    Initialize the application on startup:
    - Initialize database tables
    - Clean up any duplicate data
    - Schedule initial data updates
    """
    # Get database session
    db = next(get_db())
    
    # Initialize database
    init_db()
    print("Database tables initialized at startup")
    
    # Clean up any duplicate prices in the database
    from app.tasks.cleanup import cleanup_duplicate_prices
    cleanup_result = await cleanup_duplicate_prices(db)
    print(f"Cleaned up database duplicates: {cleanup_result}")
    
    # Schedule initial background updates
    background_tasks = BackgroundTasks()
    scheduler.schedule_updates(background_tasks)
    print("Initial data update scheduled")
    
    # Start a background task to periodically update data
    asyncio.create_task(scheduler.periodic_updates())

@app.on_event("startup")
async def startup_event():
    """
    Startup event handler for the FastAPI application.
    """
    await startup_tasks()

@app.get("/", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Status message
    """
    return {"status": "ok", "message": "API is running"}
