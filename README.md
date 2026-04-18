# Intelligent Task Management System

A FastAPI-based task management system built for the `CODING_CHALLENGE.md` backend track, with a lightweight browser dashboard for demonstration.

The project supports task CRUD, filtering, sorting, pagination, dependency management, search, caching, and unified error handling. It also includes Docker support and a basic GitHub Actions CI workflow for easier local setup and submission review.

## Role Track

Backend

## Tech Stack

- Language: Python 3.13
- Framework: FastAPI
- Database: SQLite
- Other tools: SQLAlchemy, Pydantic v2, pytest, Docker, Docker Compose, GitHub Actions, Vanilla JavaScript

## Features Implemented

- [x] Task CRUD API
- [x] Filter by status, priority, and tags
- [x] Sort by creation date, priority, and status
- [x] Pagination support
- [x] Task dependencies and dependency tree API
- [x] Prevent completing tasks with unfinished dependencies
- [x] Prevent duplicate, self-referential, and cyclic dependencies
- [x] Keyword search on title and description
- [x] Local TTL cache for frequently accessed read endpoints
- [x] Unified validation and error responses
- [x] Browser dashboard for task management and filtering
- [x] Docker / Docker Compose support
- [x] Basic GitHub Actions CI

## Setup Instructions

### 1. Prerequisites

- Python 3.13
- `pip`
- Docker, if you want to run the containerized version

### 2. Installation Steps

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### 3. Configuration

Optional environment variables:

- `DATABASE_URL`
  Default: `sqlite:///./task_manager.db`

- `CACHE_TTL_SECONDS`
  Default: `60`

### 4. Running the Application

Run locally:

```bash
uvicorn app.main:app --reload
```

Available URLs after startup:

- Dashboard: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`

Run with Docker:

```bash
docker compose up --build
```

Stop containers:

```bash
docker compose down
```

## API Documentation

Main endpoints:

- `GET /health`
- `POST /api/tasks`
- `GET /api/tasks`
- `GET /api/tasks/search`
- `GET /api/tasks/{task_id}`
- `PATCH /api/tasks/{task_id}`
- `DELETE /api/tasks/{task_id}`
- `POST /api/tasks/{task_id}/dependencies/{dependency_id}`
- `DELETE /api/tasks/{task_id}/dependencies/{dependency_id}`
- `GET /api/tasks/{task_id}/dependencies/tree`

### Example 1: Create Task

Request:

```http
POST /api/tasks
Content-Type: application/json
```

```json
{
  "title": "Prepare release checklist",
  "description": "Finalize docs, image build, and test results",
  "status": "pending",
  "priority": "high",
  "tags": ["backend", "release"]
}
```

Response:

```json
{
  "id": "9b6c9f7f-7a1e-4d0b-84ec-7f7fbe7e1d25",
  "title": "Prepare release checklist",
  "description": "Finalize docs, image build, and test results",
  "status": "pending",
  "priority": "high",
  "created_at": "2026-04-18T17:00:00.000000",
  "updated_at": "2026-04-18T17:00:00.000000",
  "tags": ["backend", "release"]
}
```

### Example 2: List Tasks with Filters

Request:

```http
GET /api/tasks?status=pending&tags=backend&sort_by=priority&order=desc&page=1&page_size=10
```

Response:

```json
{
  "items": [
    {
      "id": "9b6c9f7f-7a1e-4d0b-84ec-7f7fbe7e1d25",
      "title": "Prepare release checklist",
      "description": "Finalize docs, image build, and test results",
      "status": "pending",
      "priority": "high",
      "created_at": "2026-04-18T17:00:00.000000",
      "updated_at": "2026-04-18T17:00:00.000000",
      "tags": ["backend", "release"]
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

### Example 3: Dependency Tree

Request:

```http
GET /api/tasks/{task_id}/dependencies/tree
```

Response:

```json
{
  "id": "task-c",
  "title": "Add integration tests",
  "description": null,
  "status": "pending",
  "priority": "low",
  "tags": ["test"],
  "dependencies": [
    {
      "id": "task-b",
      "title": "Implement service layer",
      "description": null,
      "status": "pending",
      "priority": "medium",
      "tags": ["backend"],
      "dependencies": [
        {
          "id": "task-a",
          "title": "Finish database design",
          "description": null,
          "status": "completed",
          "priority": "high",
          "tags": ["backend"],
          "dependencies": []
        }
      ]
    }
  ]
}
```

For the full schema and interactive debugging, see Swagger at `/docs`.

## Performance Check

A lightweight benchmark script is included:

```bash
python scripts/benchmark_basic_ops.py
```

Notes:

- The script uses `TestClient` in-process, so it does not include real network overhead.
- It is intended as a quick implementation-level sanity check, not a replacement for production-grade load testing.

One local reference run (`2026-04-18`, temporary SQLite database, 120 seeded tasks):

```text
POST /api/tasks                avg=2.29ms  p95=2.64ms  max=2.72ms
GET /api/tasks/{id} MISS       avg=1.59ms  p95=1.82ms  max=3.54ms
GET /api/tasks/{id} HIT        avg=0.65ms  p95=0.71ms  max=0.90ms
GET /api/tasks MISS            avg=2.93ms  p95=3.89ms  max=4.00ms
GET /api/tasks HIT             avg=0.84ms  p95=0.89ms  max=0.92ms
GET /api/tasks/search MISS     avg=2.60ms  p95=3.17ms  max=3.18ms
GET /api/tasks/search HIT      avg=0.79ms  p95=0.87ms  max=1.03ms
```

These results show that the current local implementation stays well below the `<100ms` target mentioned in the challenge for basic operations. That said, these are still development-machine, in-process reference numbers rather than real deployment benchmarks.

## Design Decisions

- FastAPI was chosen for rapid development, clean typing, and built-in OpenAPI documentation.
- SQLAlchemy was used to keep data modeling and query logic structured and extensible.
- The project uses a `Router -> Service -> Repository` layering approach to separate HTTP concerns, business rules, and persistence logic.
- SQLite was selected as a lightweight persistence option that is easy to run and demonstrate within challenge constraints.
- Tags and task dependencies are modeled in separate tables to support filtering, validation rules, and future extension.
- A local in-process TTL cache was added to improve repeated read performance with low implementation complexity.
- A more detailed architecture write-up is available in [docs/architecture.md](docs/architecture.md).

## Challenges & Solutions

- Challenge: Tag selection state and filter state affected each other in the frontend.  
  Solution: I separated form tag state, filter tag state, and available tag statistics so they no longer share a mutable source of truth.

- Challenge: The dashboard statistics section once showed zero after refresh because of an invalid pagination request.  
  Solution: I changed the frontend aggregation flow to respect the backend `page_size <= 100` constraint and added better frontend error handling.

- Challenge: GitHub Actions failed in a clean environment.  
  Solution: I added `httpx` to dependencies because `fastapi.testclient.TestClient` depends on it.

- Challenge: Dependency handling needed both business safety and graph safety.  
  Solution: I added validation rules in the service layer for self-dependency, duplicate dependency, cyclic dependency, and unfinished dependency completion.

## Known Limitations

- The current cache is in-process only and is not suitable for multi-instance deployment.
- SQLite is appropriate for local development and challenge delivery, but not for larger production workloads.
- Search is currently keyword-based rather than full-text or semantic search.
- Authentication, authorization, and rate limiting are not implemented.
- Tests currently focus on API-level integration coverage; repository and service unit tests could be expanded further.

## Future Improvements

- Migrate from SQLite to PostgreSQL and introduce Alembic for schema migrations.
- Replace local cache with Redis and add more granular invalidation strategies.
- Add full-text search or semantic search.
- Add authentication, authorization, and rate limiting.
- Improve support for 100k+ task scenarios with stronger indexing, cursor pagination, and better aggregation strategies.
- Add export capabilities, attachments, and richer observability.

## AI Usage

AI coding assistance was used during development for requirement interpretation, debugging support, documentation refinement, and frontend presentation improvements.

Tools used:

- Codex / ChatGPT

Notes:

- I personally focused on the Python backend implementation and my own technical background is mainly in Python.
- The original goal for the frontend was simply to create a basic HTML visualization layer for demonstrating the backend APIs and task data.
- After the basic visualization was working, I asked AI to help improve the page because the original UI felt too plain and minimal.
- AI mainly contributed to polishing the presentation layer, including CSS, JavaScript, and some HTML structure refinements.
- Final integration decisions, feature scope, testing, and submitted changes were still reviewed and confirmed by me.
- The running project itself does not depend on any external AI API or AI service configuration.

## Time Spent

Approximately 3 hours for the original challenge scope, plus additional time later for bug fixes, UI improvements, CI repair, and documentation refinement.
