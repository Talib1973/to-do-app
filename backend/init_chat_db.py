"""Initialize database schema for AI chatbot feature (conversations and messages tables)."""

import os
from sqlmodel import SQLModel, create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all models to ensure they're registered with SQLModel
from src.models import User, Task, Conversation, Message

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

print(f"Creating chat tables in database: {DATABASE_URL}")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Create all tables (will only create tables that don't exist)
print("\nCreating tables...")
SQLModel.metadata.create_all(engine)

print("\n✅ Chat feature tables created successfully!")
print("   - conversations (id, user_id, created_at, updated_at)")
print("   - messages (id, conversation_id, user_id, role, content, created_at)")
print("\n🎉 Database schema ready for AI chatbot!")
