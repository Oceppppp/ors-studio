# Implementation Status — ORS Studio v0.4.0

**Status:** Public Web + Desktop beta foundation; cloud deployment and Windows installer remain unverified.  
**Date:** 18 November 2026

## Implemented in this source snapshot

- Shared solver catalog: 29 stable module keys with exact supported variants listed in `MODULE_IMPLEMENTATION_SCOPE.md`.
- Existing Desktop/local edition retained: FastAPI local API, SQLite persistence, loopback-only listener, HTML/CSS/native JS UI, import/export, and local bounded batch pool.
- Public Web entry point is separate: `orstudio.web_api:app`; it does not expose the unauthenticated desktop API.
- Guest Mode (24-hour temporary session) and registered USER registration/login.
- Guest-to-account upgrade preserves project/data ownership.
- Argon2 password hashing; opaque random session cookies with HMAC-SHA256 digests; HttpOnly/SameSite and Secure production cookies.
- PostgreSQL-ready SQLAlchemy schema and Alembic baseline migration.
- Principal-owned workspaces, datasets, analyses and jobs; tenant isolation regression tests.
- CSV/XLSX Web import, worksheet selection, preview, numeric mapping, row/file limits.
- Synchronous single solver execution and independent batch jobs through RQ/Redis in production; bounded in-process execution in development/tests.
- Owner-scoped analysis history, job status/cancel-while-queued, forecasting comparison, and XLSX/CSV/PDF exports.
- Origin checking for state-changing requests, security response headers, Redis-backed auth rate limit in production, guest quotas, hourly cleanup task.
- Render Blueprint for Web, Postgres, private Key Value/Redis, RQ worker and cleanup cron.
- Docker Compose local Web stack with PostgreSQL + Redis + Web + Worker.
- GitHub Actions workflows for Web tests and Windows Python 3.15.2 x64 Desktop build/installer release.
- Dual-edition documentation, updated Operations Workbench design, MIT License, contribution and security guidance.

## Current verification evidence

Latest local automated suite after Web integration: **48 passed** (Python authoring runtime 3.13.5; SQLite test database). Additional checks completed:

- `python -m compileall -q backend run_app.py`.
- `node --check` on frontend JavaScript modules.
- Alembic upgrade through head against a fresh temporary SQLite database; dataset storage quota migration verified.
- Render Blueprint YAML parse and resource inspection.
- Web API guest/register/login/upgrade, cross-principal dataset/analysis/job isolation, batch worker completion and partial-dispatch failure, storage-quota enforcement, cross-origin and cross-scheme mutation rejection, frontend auth asset mounting, health checks, and 29-module catalogue test.

This is not a substitute for tests on actual Render PostgreSQL/Redis services, Windows Python 3.15.2 packaging, browser E2E, load testing, or an independent security audit.

## Not implemented or not verified

- Live Render deployment, public URL, custom domain, DNS, or production secrets.
- Repository publication of this v0.4.0 source and release tag (publish with `PUBLISH_TO_GITHUB.bat` after reviewing the package).
- Successful Windows installer build or clean-machine Windows installation/upgrade/uninstall test.
- Email verification, password reset/account recovery, formal account deletion and user export workflow.
- Formal privacy/terms consent and retention controls for a public consumer launch.
- Independent penetration test, dependency/security audit, concurrency/load tests, monitoring/alerting, and tested database restore.
- Cloud object storage for original uploaded workbook binary; only parsed rows/columns persist in PostgreSQL.
- Full POM-QM edition parity, all submodels and outputs.
- Cross-analysis workflow DAG and automatic output-to-input dependencies.
- Running job cancellation and durable queue recovery after hard worker termination.

## Release guidance

Call this a **public beta deployment candidate**, not production-audited or launched. First publish source to the new public repository, apply the Render Blueprint with reviewed paid resource plans, verify PostgreSQL/Redis/worker health, test guest and registered flows using separate browser profiles, validate backups and restore, and complete identity/privacy/security release gates. The Windows installer is published only after the `v0.4.0` tag workflow succeeds and the artifact passes clean-machine tests.
