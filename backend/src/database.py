"""Database connection and session management."""
import os
from typing import Generator

from sqlmodel import Session, create_engine
from sqlalchemy import event
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

# SQLite-specific configuration for better concurrency
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False,  # Allow multiple threads
        "timeout": 30,  # Wait up to 30 seconds for locks
    }

# Create SQLModel engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (set to False in production)
    connect_args=connect_args,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Connection pool size
    max_overflow=10,  # Maximum overflow connections
)

# Configure SQLite for better concurrency on every connection
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")  # 30 seconds in milliseconds
        cursor.close()


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

    # Enable WAL mode for SQLite (better concurrency)
    if DATABASE_URL.startswith("sqlite"):
        with engine.connect() as connection:
            connection.exec_driver_sql("PRAGMA journal_mode=WAL;")
            connection.commit()
