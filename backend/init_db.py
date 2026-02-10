"""Initialize database tables for testing."""
from src.database import engine, init_db
# Import models to register them with SQLModel
from src.models.user import User
from src.models.task import Task

if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Database tables created successfully!")
