---
title: Todo App API
emoji: ✅
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Todo App - FastAPI Backend

A secure, multi-user task management API built with FastAPI, SQLModel, and PostgreSQL.

## Features

- 🔐 JWT Authentication
- ✅ Task CRUD Operations
- 👥 Multi-user support with data isolation
- 🗄️ PostgreSQL database
- 📚 Interactive API documentation

## API Documentation

Once deployed, visit:
- **Interactive Docs:** `/docs`
- **Health Check:** `/`

## Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user profile

### Tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks` - List user's tasks
- `GET /api/tasks/{id}` - Get single task
- `PUT /api/tasks/{id}` - Update task
- `PATCH /api/tasks/{id}` - Partial update
- `DELETE /api/tasks/{id}` - Delete task

All task endpoints require JWT authentication.

## Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection string
- `BETTER_AUTH_SECRET` - JWT secret key (min 32 characters)

## Tech Stack

- FastAPI 0.128+
- SQLModel 0.0.14
- PostgreSQL (via Neon)
- JWT Authentication
- Pydantic validation

## Local Development

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```

Visit http://localhost:8000/docs for API documentation.
