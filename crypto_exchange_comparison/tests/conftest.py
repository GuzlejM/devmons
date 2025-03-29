import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.connection import get_db, Base

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def test_db():
    """Create a fresh database for each test"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create the tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session for testing
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after the test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    """Create a test client with the test database"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    # Override the get_db dependency
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
        
    # Remove the override
    app.dependency_overrides = {} 