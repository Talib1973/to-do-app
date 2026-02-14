"""Initialize database tables."""
from src.database import engine, init_db
# Import ALL models to register them with SQLModel metadata
from src.models.user import User
from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message

if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Database tables created successfully!")
