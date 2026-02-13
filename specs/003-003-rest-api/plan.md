# Implementation Plan: REST API

**Branch**: `003-003-rest-api` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)

## Summary

6 CRUD endpoints: POST/GET/PATCH/PUT/DELETE /api/tasks, JWT auth on all, user_id filtering, Pydantic validation, 200/201/204/400/401/403/404 responses.

## Technical Context

**Framework**: FastAPI 0.104+
**Validation**: Pydantic 2.0+
**ORM**: SQLModel (queries filtered by user_id)
**Auth**: JWT dependency injection

## Constitution Check ✅ PASS

All 6 principles satisfied. Security: 100% endpoints require JWT, user_id from token, queries filtered.

## Endpoints

- POST /api/tasks (201) - Create with user_id from JWT
- GET /api/tasks (200) - List user's tasks, ?completed filter
- GET /api/tasks/{id} (200/403/404) - Get single, verify ownership
- PUT /api/tasks/{id} (200/403/404) - Full update, verify ownership
- PATCH /api/tasks/{id} (200/403/404) - Partial update
- DELETE /api/tasks/{id} (204/403/404) - Delete, verify ownership

## Implementation

**Files**:
- `backend/src/api/tasks.py` - All 6 route handlers
- `backend/src/schemas/task.py` - TaskCreate, TaskUpdate, TaskResponse
- Uses get_current_user_id() dependency for auth

**Next**: `/sp.tasks 003-rest-api`
