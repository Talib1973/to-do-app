"""Run migration to add conversations and messages tables for AI chatbot feature."""

import os
from pathlib import Path
from sqlmodel import create_engine, Session, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

print(f"Connecting to database: {DATABASE_URL}")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Read migration SQL
migration_path = Path(__file__).parent / "migrations" / "001_add_chat_tables.sql"
with open(migration_path, "r") as f:
    migration_sql = f.read()

# Execute migration
with Session(engine) as session:
    print("Running migration: 001_add_chat_tables.sql")

    # Split by statement (each CREATE/INDEX command)
    statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip() and not stmt.strip().startswith('--')]

    for stmt in statements:
        if stmt:
            print(f"\nExecuting:\n{stmt[:100]}...")
            session.exec(text(stmt))

    session.commit()
    print("\n✅ Migration completed successfully!")

# Verify tables created
with Session(engine) as session:
    # Check conversations table
    result = session.exec(text("""
        SELECT table_name FROM information_schema.tables
        WHERE table_name IN ('conversations', 'messages')
        ORDER BY table_name
    """))
    tables = result.all()
    print(f"\n✅ Tables created: {[t[0] for t in tables]}")

    # Check indexes
    result = session.exec(text("""
        SELECT indexname FROM pg_indexes
        WHERE tablename IN ('conversations', 'messages')
        AND indexname LIKE 'idx_%'
        ORDER BY indexname
    """))
    indexes = result.all()
    print(f"✅ Indexes created: {[i[0] for i in indexes]}")

print("\n🎉 Chat feature database schema ready!")
