# Developer Guide — ORS Studio v0.4.0

## 1. Repository layout

- backend/orstudio/api.py: Desktop/local API using SQLite.
- backend/orstudio/web_api.py: optional Public Web API with authentication and tenant checks.
- backend/orstudio/database.py: Desktop SQLite repository.
- backend/orstudio/cloud_store.py: SQLAlchemy cloud persistence.
- backend/orstudio/cloud_security.py: session and password security.
- backend/orstudio/cloud_jobs.py: RQ worker entry point.
- backend/orstudio/modules/: shared mathematical solvers.
- backend/orstudio/registry.py: stable 29-module registry.
- frontend/: HTML/CSS/native JavaScript ES modules.
- migrations/: Alembic schema revisions for Web.
- scripts/: environment verification and deployment helper scripts.
- .github/workflows/: Web tests and Windows packaging/release.

## 2. Local Desktop development (recommended entry point)

### Windows

~~~cmd
setup_windows.bat
START_ORS.bat
~~~

The local API binds to 127.0.0.1 only. Its SQLite data folder is managed by the local runtime. Never expose this unauthenticated endpoint to a LAN or public network.

### macOS / Linux

~~~bash
chmod +x run_local.sh
./run_local.sh
~~~

## 3. Local Web stack (optional)

1. Copy .env.example to .env and replace the development secret.
2. Install Docker Desktop.
3. Run:

~~~bash
docker compose -f compose.web.yaml up --build
~~~

4. Open http://localhost:8000.
5. Stop services with Ctrl+C or docker compose -f compose.web.yaml down.

The named PostgreSQL volume is retained unless explicitly removed. Do not use production data in the development stack.

## 4. Python tests

~~~bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m compileall -q backend run_app.py
~~~

Run node --check on changed JavaScript files. Web tests run against temporary SQLite; actual PostgreSQL/Redis deployment still needs smoke testing.

## 5. Adding a solver

1. Read docs/MODULE_CATALOG.md and docs/MODULE_IMPLEMENTATION_SCOPE.md.
2. Read the relevant ORS project skill under .agents/skills/ and the matching owner-provided Antigravity skill.
3. Create/update a focused solver file under backend/orstudio/modules/.
4. Validate all input domains and units.
5. Add independent golden cases plus boundary/infeasible tests.
6. Register the stable module_key and a runnable example.
7. Update MODULE_IMPLEMENTATION_SCOPE.md and user-facing assumptions.
8. Run the full test suite.

Both Desktop and Web must use registry.run_module(); do not fork solver logic per distribution.

## 6. Web security invariants

- Never route public traffic to orstudio.api:app.
- Public Web uses orstudio.web_api:app, PostgreSQL, session principals, Redis/RQ, and a private worker.
- Enforce owner_id in the database query for every project-scoped object. Do not rely on UI hiding.
- Keep session tokens opaque and store only HMAC digests; hash passwords using Argon2.
- Do not log passwords, session tokens, or raw datasets.
- Reject cross-origin state-changing requests.
- Never execute workbook macros, scripts, or formulas.
- All cloud schema changes require an Alembic migration.

## 7. Optional Web deployment

The supported prepared architecture is Netlify for the static frontend and Railway for the Python API, PostgreSQL, Redis, worker, and scheduled guest cleanup. Read docs/RAILWAY_NETLIFY_DEPLOYMENT.md. It is an optional deployment path; local mode does not require these services.

Do not use Render Blueprint instructions from older notes. Render configuration was removed from the main branch.

## 8. Release gates

A release must not be called production-ready until Web deployment, PostgreSQL/Redis checks, two-principal isolation tests, upload/export flow, backup/restore, independent security review, load tests, and clean Windows installer tests have passed. Email verification and password recovery are not implemented in v0.4.0.
