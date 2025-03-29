from sqlalchemy.orm import Session
from app.models.models import Base, Exchange, Coin, Price
from app.database.connection import engine, get_db

def init_db():
    """Initialize the database with tables"""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database tables created.") 