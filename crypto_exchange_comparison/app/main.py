from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from app.database.connection import get_db
from app.api import exchanges, coins, compare
from app.database.init_db import init_db
from app.tasks import scheduler

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

# Add new router for data updates
@app.get("/update", tags=["maintenance"])
async def trigger_updates(background_tasks: BackgroundTasks):
    """
    Manually trigger data updates in the background
    """
    return scheduler.schedule_updates(background_tasks)

@app.get("/update/status", tags=["maintenance"])
async def update_status():
    """
    Get the status of the last data updates
    """
    return scheduler.get_last_update_times()

@app.on_event("startup")
async def startup_event():
    """Initialize database and schedule updates on startup"""
    # Initialize database
    init_db()
    print("Database tables initialized at startup")
    
    # Schedule initial background updates
    background_tasks = BackgroundTasks()
    scheduler.schedule_updates(background_tasks)
    print("Initial data update scheduled")
    
    # Start a background task to periodically update data every 4 hours
    asyncio.create_task(periodic_updates())

async def periodic_updates():
    """
    Run updates periodically in the background
    """
    while True:
        # Sleep for 4 hours
        await asyncio.sleep(4 * 60 * 60)  
        
        # Create new background tasks
        background_tasks = BackgroundTasks()
        scheduler.schedule_updates(background_tasks)
        print("Scheduled periodic data update")

@app.get("/", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "API is running"}
