# Project: Personal Todo App

## Overview

A lightweight personal todo application built as a REST API using FastAPI and SQLite. The app provides standard CRUD operations for managing todo items, including the ability to mark todos as completed.

The application follows clean architecture principles with clear separation between the API layer, business logic, and data persistence. SQLAlchemy is used as the ORM for type-safe database interactions with SQLite as the storage backend.

This is a focused, minimal API — no frontend, no authentication, no multi-user support. It serves as a clean, well-structured backend that can be extended or consumed by any client.

## Target Users

- Solo developer managing personal tasks via API calls (curl, Postman, or a future frontend)

## Technical Stack

- **Language**: Python 3.13+
- **Framework**: FastAPI
- **Database**: SQLite (via SQLAlchemy ORM)
- **Package Manager**: uv
- **Validation**: Pydantic v2 (bundled with FastAPI)
- **Server**: Uvicorn (ASGI)

## Architecture

```
app/
├── main.py              # FastAPI app entry point, lifespan, CORS
├── config.py            # Settings (DB URL, app config)
├── database.py          # SQLAlchemy engine, session factory, Base
├── models/
│   └── todo.py          # SQLAlchemy ORM model (Todo table)
├── schemas/
│   └── todo.py          # Pydantic request/response schemas
├── routers/
│   └── todos.py         # API route handlers (/api/todos)
└── repositories/
    └── todo.py          # Data access layer (DB queries)
```

### Layer Responsibilities

| Layer | Module | Responsibility |
|-------|--------|----------------|
| API | `routers/todos.py` | HTTP handling, request validation, response formatting |
| Schema | `schemas/todo.py` | Pydantic models for request/response serialization |
| Repository | `repositories/todo.py` | Database queries via SQLAlchemy, no business logic leaking |
| Model | `models/todo.py` | SQLAlchemy ORM table definition |
| Database | `database.py` | Engine, session, and Base declarative class |
| Config | `config.py` | Centralized settings |

## Data Model

### Todo

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | Integer | Primary key, auto-increment |
| `title` | String(255) | Required, non-empty |
| `completed` | Boolean | Default: `false` |

## API Endpoints

All endpoints are under `/api/todos`.

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|--------------|----------|
| `POST` | `/api/todos` | Create a new todo | `{ "title": "..." }` | `201` + Todo |
| `GET` | `/api/todos` | List all todos | — | `200` + Todo[] |
| `GET` | `/api/todos/{id}` | Get a single todo | — | `200` + Todo |
| `PUT` | `/api/todos/{id}` | Update a todo | `{ "title": "...", "completed": true }` | `200` + Todo |
| `DELETE` | `/api/todos/{id}` | Delete a todo | — | `204` No Content |
| `PATCH` | `/api/todos/{id}/complete` | Mark todo as completed | — | `200` + Todo |

### Response Schema

```json
{
  "id": 1,
  "title": "Buy groceries",
  "completed": false
}
```

### Error Responses

- `404` — Todo not found
- `422` — Validation error (empty title, wrong types)

## Features

### MVP (Must Have)

#### Feature 1: Project Scaffolding & Database Setup
- **Issue ID**: ACA-739
- **Priority**: 1 (Urgent)
- **Description**: Set up the project structure, FastAPI app, SQLAlchemy engine, SQLite database, and the Todo ORM model. This is the foundation everything else builds on.
- **Acceptance Criteria**:
  - [ ] FastAPI app initializes and runs with `uvicorn`
  - [ ] SQLAlchemy engine connects to a local SQLite file (`todos.db`)
  - [ ] `Todo` model creates the `todos` table on startup
  - [ ] Project follows the clean architecture folder layout
  - [ ] Dependencies added to `pyproject.toml` (fastapi, uvicorn, sqlalchemy)
- **Dependencies**: None
- **Labels**: chore

#### Feature 2: Create Todo
- **Issue ID**: ACA-740
- **Priority**: 1 (Urgent)
- **Description**: Implement `POST /api/todos` to create a new todo item. Accepts a JSON body with `title`, persists to SQLite, and returns the created todo with its generated `id`.
- **Acceptance Criteria**:
  - [ ] `POST /api/todos` with `{ "title": "..." }` returns `201` with the created todo
  - [ ] `title` is required and non-empty (returns `422` otherwise)
  - [ ] `completed` defaults to `false`
  - [ ] Todo is persisted in the SQLite database
  - [ ] Uses Pydantic schema for request validation and response serialization
  - [ ] Uses repository pattern for database access
- **Dependencies**: Feature 1
- **Labels**: feature

#### Feature 3: List & Get Todos
- **Issue ID**: ACA-741
- **Priority**: 1 (Urgent)
- **Description**: Implement `GET /api/todos` to list all todos and `GET /api/todos/{id}` to retrieve a single todo by ID.
- **Acceptance Criteria**:
  - [ ] `GET /api/todos` returns `200` with a list of all todos
  - [ ] `GET /api/todos/{id}` returns `200` with the matching todo
  - [ ] `GET /api/todos/{id}` returns `404` if the todo doesn't exist
  - [ ] Both endpoints use Pydantic response models
- **Dependencies**: Feature 1
- **Labels**: feature

#### Feature 4: Update Todo
- **Issue ID**: ACA-742
- **Priority**: 2 (High)
- **Description**: Implement `PUT /api/todos/{id}` to update an existing todo's `title` and/or `completed` status.
- **Acceptance Criteria**:
  - [ ] `PUT /api/todos/{id}` accepts partial or full updates to `title` and `completed`
  - [ ] Returns `200` with the updated todo
  - [ ] Returns `404` if the todo doesn't exist
  - [ ] Validates input via Pydantic schema (optional fields)
- **Dependencies**: Feature 1
- **Labels**: feature

#### Feature 5: Delete Todo
- **Issue ID**: ACA-743
- **Priority**: 2 (High)
- **Description**: Implement `DELETE /api/todos/{id}` to remove a todo from the database.
- **Acceptance Criteria**:
  - [ ] `DELETE /api/todos/{id}` returns `204` No Content on success
  - [ ] Returns `404` if the todo doesn't exist
  - [ ] Todo is removed from the database
- **Dependencies**: Feature 1
- **Labels**: feature

#### Feature 6: Mark Todo as Completed
- **Issue ID**: ACA-744
- **Priority**: 2 (High)
- **Description**: Implement `PATCH /api/todos/{id}/complete` as a convenience endpoint to mark a todo as completed without sending the full update payload.
- **Acceptance Criteria**:
  - [ ] `PATCH /api/todos/{id}/complete` sets `completed = true` and returns `200` with the updated todo
  - [ ] Returns `404` if the todo doesn't exist
  - [ ] Idempotent — calling on an already-completed todo is a no-op (still returns `200`)
- **Dependencies**: Feature 4
- **Labels**: feature

## Dependency Graph

```
Feature 1: Project Scaffolding & Database Setup (no deps)
├── Feature 2: Create Todo (depends on 1)
├── Feature 3: List & Get Todos (depends on 1)
├── Feature 4: Update Todo (depends on 1)
│   └── Feature 6: Mark Todo as Completed (depends on 4)
└── Feature 5: Delete Todo (depends on 1)
```

## Implementation Order

1. **Feature 1** — Scaffolding & DB setup
2. **Features 2, 3** — Create + Read (can be parallel)
3. **Features 4, 5** — Update + Delete (can be parallel)
4. **Feature 6** — Mark complete (depends on update logic)

## Created Issues

| Feature | Linear ID | Status |
|---------|-----------|--------|
| Project Scaffolding & Database Setup | ACA-739 | Created |
| Create Todo | ACA-740 | Created |
| List & Get Todos | ACA-741 | Created |
| Update Todo | ACA-742 | Created |
| Delete Todo | ACA-743 | Created |
| Mark Todo as Completed | ACA-744 | Created |

## Validation Commands

```bash
# Install dependencies
uv sync

# Run the server
uv run uvicorn app.main:app --reload

# Test health (after Feature 1)
curl http://localhost:8000/docs

# Test CRUD (after Features 2-6)
curl -X POST http://localhost:8000/api/todos -H "Content-Type: application/json" -d '{"title": "Test todo"}'
curl http://localhost:8000/api/todos
curl http://localhost:8000/api/todos/1
curl -X PUT http://localhost:8000/api/todos/1 -H "Content-Type: application/json" -d '{"title": "Updated", "completed": true}'
curl -X PATCH http://localhost:8000/api/todos/1/complete
curl -X DELETE http://localhost:8000/api/todos/1
```
