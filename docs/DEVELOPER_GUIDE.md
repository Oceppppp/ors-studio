# Developer Guide — ORS Studio v0.4.0

## 1. Repository layout

- `backend/orstudio/api.py`: Desktop/local API using SQLite.
- `backend/orstudio/web_api.py`: Public Web API with authentication and tenant checks.
- `backend/orstudio/database.py`: Desktop SQLite repository.
- `backend/orstudio/cloud_store.py`: SQLAlchemy cloud persistence.
- `backend/orstudio/cloud_security.py`: session and password security.
- `backend/orstudio/cloud_jobs.py`: RQ worker entry point.
- `backend/orstudio/modules/`: shared mathematical solvers.
- `backend/orstudio/registry.py`: stable 29-module registry.
- `frontend/`: HTML/CSS/native JavaScript ES modules.
- `migrations/`: Alembic schema revisions for Web.
- `render.yaml`: Render Blueprint.
- `.github/workflows/`: Web tests and Windows packaging/release.

## 2. Local Desktop development

```bash
setup_windows.bat
START_ORS.bat
```

The local API binds to `127.0.0.1` only. Its SQLite data folder is managed by the local runtime. Never expose this unauthenticated endpoint to a LAN or public network.

## 3. Local Web stack

1. Copy `.env.example` to `.env` and replace the development secret.
2. Install Docker Desktop.
3. Run:

```bash
docker compose -f compose.web.yaml up --build
```

4. Open `http://localhost:8000`.
5. Stop services with Ctrl+C or `docker compose -f compose.web.yaml down`.

The named PostgreSQL volume is retained unless explicitly removed. Do not use production data in the development stack.

## 4. Python tests

```bash
python -m pip install -r requirements-dev.txt
PYTHONPATH=backend python -m pytest -q
python -m compileall -q backend run_app.py
```

Run `node --check` on changed JavaScript files. Web tests run against temporary SQLite; Render production uses PostgreSQL/Redis, which still need deployment smoke tests.

## 5. Adding a solver

1. Read `docs/MODULE_CATALOG.md` and `docs/MODULE_IMPLEMENTATION_SCOPE.md`.
2. Read the relevant ORS project skill under `.agents/skills/` and the matching owner-provided Antigravity skill.
3. Create/update a focused solver file under `backend/orstudio/modules/`.
4. Validate all input domains and units.
5. Add independent golden cases plus boundary/infeasible tests.
6. Register the stable `module_key` and a runnable example.
7. Update `MODULE_IMPLEMENTATION_SCOPE.md` and the user-facing assumptions.
8. Run the full test suite.

Both Desktop and Web must use `registry.run_module()`; do not fork solver logic per distribution.

## 6. Web security invariants

- Never route public traffic to `orstudio.api:app`.
- Public Web uses `orstudio.web_api:app`, PostgreSQL, session principals, Redis/RQ, and a private worker.
- Enforce `owner_id` in the database query for every project-scoped object. Do not rely on UI hiding.
- Keep session tokens opaque and store only HMAC digests; hash passwords using Argon2.
- Do not log passwords, session tokens, or raw datasets.
- Reject cross-origin state-changing requests.
- Never execute workbook macros, scripts, or formulas.
- All cloud schema changes require an Alembic migration.

## 7. Deployment

Read `docs/WEB_DEPLOYMENT.md`, `docs/CLOUD_ARCHITECTURE.md`, and `docs/SECURITY_MODEL.md`. `render.yaml` is a prepared configuration, not proof of a live deployment. Review plan/cost settings, secrets, backup and restore before applying it.

## 8. Release gates

A release must not be called production-ready until the Web deploy, PostgreSQL/Redis checks, two-principal isolation tests, upload/export flow, backup/restore, independent security review, load tests, and clean Windows installer tests have passed. Email verification and password recovery are not implemented in v0.4.0.
