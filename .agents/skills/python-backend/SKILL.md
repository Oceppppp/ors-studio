---
name: python-backend
description: Implement ORS backend APIs, typed domain services, data processing, persistence, and worker orchestration in a modular Python package.
---
# ORS Python Backend

## Procedure
1. Read TAD layer boundaries and SRS requirements.
2. Keep API routers, Pydantic schemas, application services, domain models, repositories, and solver adapters separate.
3. Add type hints and explicit error types; avoid global mutable state.
4. Use SQLAlchemy sessions with explicit transaction scopes and Alembic migrations.
5. Keep database transactions short; never hold a DB transaction while a solver runs.
6. Pass dataset/artifact identifiers to worker processes instead of serializing large in-memory data objects.
7. Expose stable error codes and correlation IDs; keep stack traces out of user-facing responses.
8. Add unit/integration tests and test data fixtures.
9. Run Ruff, type checks, and pytest for affected packages.
10. Update OpenAPI and documentation when API behavior changes.

## Guardrails
- Do not put solver algorithms in FastAPI route handlers.
- Do not let worker processes race to update UI state or database rows.
- Do not trust file paths or filenames from requests.
- Never silently coerce ambiguous numeric/date formats.
