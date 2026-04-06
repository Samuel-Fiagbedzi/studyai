"""
Database connection setup for StudyAI backend.

This module provides SQLAlchemy database configuration and utilities
for the StudyAI FastAPI application.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Database URL - using SQLite for MVP
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./studyai.db")

# Create SQLAlchemy engine
# check_same_thread=False is needed for SQLite to allow multiple threads
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create SessionLocal class
# This is a factory for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for all models
# All SQLAlchemy models should inherit from this Base
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.

    This function creates a new database session for each request
    and automatically closes it when the request is finished.

    Usage in FastAPI:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables defined in the models.

    This function should be called once during application startup
    to ensure all tables exist in the database.
    """
    Base.metadata.create_all(bind=engine)


# Example usage and testing
if __name__ == "__main__":
    # Create all tables
    create_tables()
    print("Database tables created successfully!")

    # Test database connection
    db = SessionLocal()
    try:
        # Execute a simple query to test connection
        result = db.execute(text("SELECT 1")).fetchone()
        print(f"Database connection test: {result[0] == 1}")
    except Exception as e:
        print(f"Database connection error: {e}")
    finally:
        db.close()