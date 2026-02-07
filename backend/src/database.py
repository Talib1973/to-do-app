"""Database connection and session management."""
import os
from typing import Generator

from sqlmodel import Session, create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please configure it in your .env file."
    )

# Create SQLModel engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (set to False in production)
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Connection pool size
    max_overflow=10,  # Maximum overflow connections
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Usage in FastAPI:
        @app.get("/items")
        def read_items(session: Session = Depends(get_session)):
            ...

    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """
    Initialize database by creating all tables.

    This should be called on application startup for development.
    In production, use Alembic migrations instead.
    """
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
