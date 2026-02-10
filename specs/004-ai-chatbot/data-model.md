# Data Model: AI Chatbot for Task Management

**Feature**: 004-ai-chatbot
**Date**: 2026-02-07
**Status**: Design
**References**: [spec.md](./spec.md), [plan.md](./plan.md), [research.md](./research.md)

## Overview

This document defines the database schema for AI chatbot conversations and messages. The design supports stateless conversation management with database-backed state, user-scoped authorization, and efficient message retrieval.

## Entities

### Conversation

Represents a chat session between an authenticated user and the AI chatbot.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique conversation identifier |
| user_id | UUID | FOREIGN KEY → users(id), NOT NULL | Owner of the conversation (enforces user scoping) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When conversation was started |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When conversation was last active (updated on new messages) |

**Indexes**:
- PRIMARY KEY: `id`
- INDEX: `user_id` (for listing user's conversations)
- INDEX: `(user_id, updated_at DESC)` (for recent conversations list)

**Relationships**:
- **User**: Many-to-one (a user can have multiple conversations)
- **Messages**: One-to-many (a conversation contains multiple messages)

**Business Rules**:
- Conversations belong to exactly one user
- Conversations cannot be shared between users
- Conversations are append-only (no deletion in initial implementation)
- `updated_at` timestamp updates whenever a new message is added

**State Transitions**: N/A (conversations don't have state, they're just containers)

---

### Message

Represents a single message within a conversation (either from user or AI assistant).

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique message identifier |
| conversation_id | UUID | FOREIGN KEY → conversations(id), NOT NULL | Parent conversation |
| user_id | UUID | FOREIGN KEY → users(id), NOT NULL | Owner (denormalized for authorization) |
| role | VARCHAR(20) | NOT NULL, CHECK(role IN ('user', 'assistant')) | Speaker role |
| content | TEXT | NOT NULL | Message text content |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When message was sent/received |

**Indexes**:
- PRIMARY KEY: `id`
- COMPOSITE INDEX: `(user_id, conversation_id, created_at ASC)` **[CRITICAL]**
  - Supports: user authorization + conversation filtering + chronological ordering
  - Single index scan for query: "Get all messages in conversation X for user Y, ordered by time"
  - ~10x faster than separate indexes (per research findings)

**Relationships**:
- **Conversation**: Many-to-one (messages belong to one conversation)
- **User**: Many-to-one (messages belong to one user)

**Business Rules**:
- Messages must belong to a valid conversation
- `user_id` must match the conversation's `user_id` (referential integrity)
- Role must be either 'user' (human) or 'assistant' (AI chatbot)
- Messages are immutable once created (no editing or deletion)
- Messages are ordered chronologically by `created_at`

**Validation Rules**:
- `content` cannot be empty
- `role` must be 'user' or 'assistant'
- `user_id` must match parent conversation's `user_id`

**State Transitions**: N/A (messages are immutable)

---

### Existing Entity: Task

**Impact**: No schema changes required. Tasks are accessed by AI agent via MCP tools, not directly.

**MCP Tool Interface**:
- `add_task(user_id, title, description)` → creates task for user
- `list_tasks(user_id, status_filter)` → retrieves user's tasks
- `update_task(user_id, task_id, title, description)` → modifies task
- `complete_task(user_id, task_id)` → marks task complete
- `delete_task(user_id, task_id)` → removes task

**User Scoping**: All MCP tools filter by `user_id` to enforce authorization.

---

### Existing Entity: User

**Impact**: No schema changes required. Users authenticate via JWT, and `user_id` is extracted from token claims.

**Relationships**:
- **Conversations**: One-to-many (user has multiple conversations)
- **Messages**: One-to-many (user has multiple messages)
- **Tasks**: One-to-many (existing relationship)

---

## Relationships Diagram

```text
┌──────────┐
│  User    │
│          │
│ id (PK)  │
│ email    │
│ ...      │
└────┬─────┘
     │
     │ 1:N
     │
     ├──────────────────────┬──────────────────────┐
     │                      │                      │
     │                      │                      │
     ▼                      ▼                      ▼
┌────────────┐      ┌──────────────┐      ┌──────────┐
│Conversation│      │   Message    │      │   Task   │
│            │      │              │      │          │
│ id (PK)    │◄─────┤conversation_id(FK)│ │ id (PK)  │
│ user_id(FK)│      │ user_id (FK) │      │user_id(FK)│
│ created_at │      │ role         │      │ title    │
│ updated_at │      │ content      │      │ ...      │
└────────────┘      │ created_at   │      └──────────┘
     │              └──────────────┘
     │ 1:N
     │
     └─────────────► (messages)
```

## Indexes Strategy

### Primary Indexes (Auto-created)
- `conversations.id` (PRIMARY KEY)
- `messages.id` (PRIMARY KEY)

### User Authorization Indexes
- `conversations.user_id` - Fast user conversation listing
- `messages.user_id` (part of composite) - User message filtering

### Performance Indexes
- `conversations(user_id, updated_at DESC)` - Recent conversations query
- `messages(user_id, conversation_id, created_at ASC)` **[COMPOSITE]** - Message retrieval

**Composite Index Justification**:
The `messages(user_id, conversation_id, created_at ASC)` index supports the most common query pattern:

```sql
SELECT * FROM messages
WHERE user_id = ? AND conversation_id = ?
ORDER BY created_at ASC;
```

This single index provides:
1. **Authorization filtering** (user_id)
2. **Conversation filtering** (conversation_id)
3. **Chronological ordering** (created_at ASC)

Alternative approaches considered and rejected:
- Separate indexes on each column: Requires index merge, ~10x slower
- Two-column index `(conversation_id, created_at)`: Missing user authorization, security risk

## Foreign Key Constraints

### conversations.user_id → users.id
- **Action on DELETE**: CASCADE (delete user → delete their conversations)
- **Action on UPDATE**: CASCADE
- **Rationale**: Conversations are user-owned data; no orphaned conversations

### messages.conversation_id → conversations.id
- **Action on DELETE**: CASCADE (delete conversation → delete all messages)
- **Action on UPDATE**: CASCADE
- **Rationale**: Messages cannot exist without parent conversation

### messages.user_id → users.id
- **Action on DELETE**: CASCADE (delete user → delete their messages)
- **Action on UPDATE**: CASCADE
- **Rationale**: Messages are user-owned data; user_id denormalized for authorization

**Denormalization Note**: `messages.user_id` is denormalized (also available via `conversation_id → conversations.user_id`). This enables single-index authorization checks without joins.

## SQLModel Implementation

### Conversation Model

```python
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
    user: "User" = Relationship(back_populates="conversations")

    class Config:
        # Composite index for recent conversations
        indexes = [
            ("user_id", "updated_at"),
        ]
```

### Message Model

```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    role: str = Field(nullable=False, max_length=20)  # 'user' or 'assistant'
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
    user: "User" = Relationship(back_populates="messages")

    class Config:
        # Composite index for message retrieval
        indexes = [
            ("user_id", "conversation_id", "created_at"),
        ]

    @validator('role')
    def validate_role(cls, v):
        if v not in ('user', 'assistant'):
            raise ValueError('role must be "user" or "assistant"')
        return v
```

### User Model Update

```python
# Add to existing User model
class User(SQLModel, table=True):
    __tablename__ = "users"

    # ... existing fields ...

    # New relationships for AI chatbot
    conversations: List[Conversation] = Relationship(back_populates="user")
    messages: List[Message] = Relationship(back_populates="user")
```

## Migration Strategy

**Alembic Migration**:
1. Add `conversations` table with indexes
2. Add `messages` table with composite index
3. Add foreign key constraints
4. Add CHECK constraint on `messages.role`

**Rollback Plan**:
1. Drop foreign key constraints
2. Drop `messages` table
3. Drop `conversations` table

**Data Migration**: N/A (new tables, no existing data to migrate)

**Backward Compatibility**: Existing tasks and users tables are unchanged; feature is additive.

## Query Patterns

### Load Conversation History
```sql
-- Used by chat endpoint to load full conversation for AI agent
SELECT * FROM messages
WHERE user_id = :user_id AND conversation_id = :conversation_id
ORDER BY created_at ASC;
```
**Index Used**: `messages(user_id, conversation_id, created_at)` (composite)

### List User's Recent Conversations
```sql
-- Dashboard/sidebar showing recent chats
SELECT * FROM conversations
WHERE user_id = :user_id
ORDER BY updated_at DESC
LIMIT 10;
```
**Index Used**: `conversations(user_id, updated_at)`

### Create New Conversation
```sql
-- Start new chat session
INSERT INTO conversations (id, user_id, created_at, updated_at)
VALUES (:id, :user_id, NOW(), NOW());
```

### Append Message to Conversation
```sql
-- Store user message or AI response
INSERT INTO messages (id, conversation_id, user_id, role, content, created_at)
VALUES (:id, :conversation_id, :user_id, :role, :content, NOW());

-- Update conversation's updated_at timestamp
UPDATE conversations
SET updated_at = NOW()
WHERE id = :conversation_id AND user_id = :user_id;
```

## Scalability Considerations

### For Large Conversation Histories (100+ messages)
- **Problem**: Loading 100+ messages on every request is slow
- **Solution** (Future Enhancement): Implement conversation truncation/summarization
  - Load last N messages (e.g., 50) for context
  - Summarize earlier messages into context prompt
  - Keep full history in database for audit/reference

### For Many Concurrent Users (10,000+)
- **Problem**: High read load on messages table
- **Solution**: Composite index provides O(log N) lookup
- **Future Enhancement**: Read replicas for conversation history queries

### Storage Growth
- **Estimate**: ~1KB per message average
- **1M messages** = ~1GB storage (manageable for PostgreSQL)
- **Future Enhancement**: Archive old conversations (>6 months inactive) to cold storage

## Security Enforcement

**User Scoping at Query Level**:
```python
# CORRECT: User ID from JWT, conversation filtered
async def get_conversation_messages(user_id: UUID, conversation_id: UUID):
    return await session.exec(
        select(Message)
        .where(Message.user_id == user_id)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )

# INCORRECT: Missing user_id filter (security violation)
async def get_conversation_messages_INSECURE(conversation_id: UUID):
    return await session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)  # ⚠️ No user check!
        .order_by(Message.created_at.asc())
    )
```

**Authorization Rule**: Every query on `conversations` or `messages` tables MUST filter by `user_id` extracted from JWT token. Route parameters MUST NOT be trusted for user identification.

## Validation Rules Summary

| Entity | Field | Validation |
|--------|-------|------------|
| Conversation | user_id | Must exist in users table (foreign key) |
| Conversation | updated_at | Auto-updated on message insert |
| Message | conversation_id | Must exist in conversations table (foreign key) |
| Message | user_id | Must match conversation.user_id |
| Message | role | Must be 'user' or 'assistant' (CHECK constraint) |
| Message | content | Cannot be empty string (application-level) |

## Referential Integrity

**Cascade Rules**:
- Delete user → cascade delete conversations → cascade delete messages
- Delete conversation → cascade delete messages
- Cannot delete if violates constraints

**Orphan Prevention**:
- Messages cannot exist without conversation (foreign key)
- Conversations cannot exist without user (foreign key)
- User deletion cleans up all related data

## Testing Considerations

### Contract Tests (Database Layer)
- Insert conversation → verify created_at and updated_at set
- Insert message → verify conversation.updated_at updates
- Query messages with user_id filter → verify authorization
- Attempt cross-user access → verify 0 results

### Integration Tests (API Layer)
- Create conversation via POST /api/{user_id}/chat
- Load conversation history via GET
- Verify user A cannot access user B's conversations

### Performance Tests
- Load conversation with 100 messages → measure query time (<100ms)
- Create 1000 conversations for single user → verify index performance
- Concurrent message inserts → verify no deadlocks
