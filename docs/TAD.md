# Technical Architecture Document (TAD)
## Operations Research Studio (ORS)

**Dokumen:** ORS-TAD-001  
**Versi:** 0.4.0  
**Tanggal:** 18 November 2026  
**Status:** Dual-distribution public beta foundation; public deployment not yet provisioned  
**Distribusi:** Public Web (Guest + account) dan Desktop/local (offline-capable)

## 1. Tujuan

ORS menyediakan satu workspace Operations Research, Production and Operations Management, dan Quantitative Methods. Kedua distribusi menggunakan registry dan solver Python yang sama, tetapi memisahkan proses autentikasi serta penyimpanannya: Web memakai principal-scoped PostgreSQL; Desktop memakai SQLite lokal.

## 2. Architectural drivers

| Driver | Keputusan v0.4.0 |
|---|---|
| Solver reuse | 29 stable module keys; shared `registry.run_module()` |
| Public access | Browser-based Web edition with Guest and registered account flows |
| Desktop continuity | Local-first desktop edition remains available without cloud account |
| Tenant isolation | Every cloud resource is scoped to `principal_id` through project ownership |
| Import | CSV/XLSX upload, preview, worksheet selection, column mapping |
| Multi-analysis | Independent batch tasks, dispatched to bounded background workers |
| Persistence | PostgreSQL/Alembic for Web; SQLite for Desktop |
| Queue | Redis-compatible service + RQ in production; bounded in-process queue for test/development only |
| Distribution | Render Blueprint for Web; GitHub Actions PyInstaller/Inno Setup recipe for Windows Desktop |
| Maintainability | Feature-oriented modules, separated APIs, repositories, services, and solvers |

## 3. High-level system architecture

```text
                           ORS STUDIO v0.4.0
                                  |
                 +----------------+----------------+
                 |                                 |
        DESKTOP / LOCAL                         PUBLIC WEB
                 |                                 |
       run_app.py / START_ORS                HTTPS reverse proxy
                 |                                 |
       orstudio.api:app                  orstudio.web_api:app
                 |                                 |
       Local SQLite store                Session + authorization
                 |                                 |
                 |                        SQLAlchemy cloud store
                 |                                 |
                 |                          PostgreSQL database
                 |                                 |
                 |                          Redis / RQ queue
                 |                                 |
                 |                           Private worker
                 |                                 |
                 +----------------+----------------+
                                  |
                         Shared solver registry
                       backend/orstudio/modules/*
                                  |
                            run_module(key)
```

The Desktop API must remain loopback-only. The Public Web service must never expose the unauthenticated Desktop API. Both editions may use the same static frontend files, while the Web edition displays an authentication gate and workspace identity.

## 4. Technology decisions — as built

| Layer | Technology | Use |
|---|---|---|
| Frontend | HTML, CSS, native JavaScript ES modules | Same-origin responsive UI |
| API framework | FastAPI + Uvicorn | Local/Desktop API and separate Web API entry points |
| Calculation engine | Python; Windows Desktop build targets 3.15.2 x64 | Shared solver implementations |
| Numerical engine | NumPy, SciPy/HiGHS, pandas, openpyxl | Optimization and tabular data |
| Export | XlsxWriter, ReportLab | Excel, CSV, PDF output |
| Desktop persistence | SQLite via Python `sqlite3` | Per-computer local data |
| Web persistence | SQLAlchemy Core + PostgreSQL + Alembic | Accounts, sessions, projects, datasets, analyses, jobs |
| Password security | Argon2 (`argon2-cffi`) | Password hashing |
| Session | Opaque random cookie + HMAC-SHA256 digest | Browser sessions; raw token is not persisted |
| Background queue | Redis-compatible Key Value + RQ | Web batch processing |
| Testing | pytest + Node syntax checks | Unit and integration tests |
| Windows packaging | PyInstaller onedir + Inno Setup | Self-contained installer recipe |
| Web deployment | Render Blueprint | Web, worker, Postgres, Key Value, guest-cleanup cron |

React, TypeScript, Vite, and Tauri are not used by the current build. Do not document them as implemented.

## 5. API and service separation

### 5.1 Desktop/local API

- Entry point: `orstudio.api:app`.
- Persistence: `backend/orstudio/database.py` using SQLite.
- Intended listener: `127.0.0.1` only.
- No online account is required; operating-system user separation protects local files.
- Desktop setup and installer must keep data out of the installation folder.

### 5.2 Public Web API

- Entry point: `orstudio.web_api:app`.
- Production database must be PostgreSQL (`DATABASE_URL`).
- Production batch queue and shared authentication rate limits require Redis (`REDIS_URL`).
- Production sessions require a long random `ORS_SESSION_SECRET`.
- Web service is behind HTTPS/reverse proxy and binds to `0.0.0.0:$PORT`.
- Same-origin frontend/API avoids broad CORS. State-changing requests are checked against Origin/Fetch Metadata and responses include security headers.

### 5.3 Shared solver contract

Both APIs call `registry.run_module(module_key, params)`. Solver modules must not depend on whether the caller is Desktop or Web. All solver outputs are sanitized through the shared JSON-cleaning contract. Module-specific assumptions and exclusions remain in `MODULE_IMPLEMENTATION_SCOPE.md`.

## 6. Web identity and tenant model

- `ors_principals`: `USER` or temporary `GUEST` identity.
- `ors_sessions`: stores only HMAC digest of opaque browser tokens, with expiry.
- `ors_projects`: owned directly by `owner_id`.
- `ors_datasets`, `ors_analyses`, and `ors_jobs`: owned transitively through project membership.
- Cloud repository methods take `owner_id`; selects and mutations include the owner constraint. A missing or foreign object returns a non-disclosing `404`.
- Guest session lifetime: 24 hours; an hourly cleanup task purges expired guest principal and cascading workspace data.
- Guest limits: two workspaces, three datasets, 5 MiB per upload, 10,000 rows per dataset, five tasks per batch, and ten saved analyses/jobs.
- Registered account defaults: 50 workspaces, 100 datasets, 20 MiB per upload, 40 tasks per batch, 1,000 queued jobs, 5,000 saved analyses.
- Guest upgrade changes the principal in place and preserves existing workspace data.

These quotas are beta guardrails and need capacity testing and configuration before a large public launch.

## 7. Web request path and analysis jobs

1. Browser requests `/api/auth/me` and receives session state.
2. Unauthenticated visitor chooses Guest, registers, or signs in.
3. API resolves the HttpOnly cookie and obtains a principal.
4. Data/project APIs enforce ownership at the persistence layer.
5. Dataset upload is parsed and normalized. The original workbook binary is not retained in v0.4.0.
6. A synchronous single analysis calls the shared solver through the Web API.
7. Batch tasks are validated before records are created, committed in PostgreSQL, then dispatched to RQ.
8. A private worker loads the same solver registry, runs the task, and writes status/output scoped to the owner.
9. Browser polls job status and can retrieve owner-scoped results and exports.

Batch jobs are independent. Workflow DAG, dependency scheduling, and automatic output-to-input mapping are not implemented.

## 8. Database lifecycle

- Baseline migration: `migrations/versions/0001_initial_cloud_schema.py`.
- Run `alembic upgrade head` before serving the Web API.
- Schema changes require a new Alembic revision. `metadata.create_all()` is a test/bootstrap aid, not a migration strategy.
- Render PostgreSQL is the durable store. Do not use ephemeral web-service filesystem for production data.
- Backups and restore must be configured and tested before promoting from beta.

## 9. Security boundaries and known gaps

Implemented: Argon2 password hashing, opaque HMAC-digested sessions, HttpOnly/SameSite cookies, Secure cookies in production, same-origin mutation guard, owner-scoped access, upload validation and quotas, security headers, Redis shared rate limits, private RQ worker.

Not yet implemented: email verification, password reset, self-service account deletion/export workflow, verified-email recovery, independent penetration test, privacy/terms workflow, storage object service for original files, alerting, and tested backup restoration. This is a **public beta foundation**, not a fully security-audited production identity platform.

## 10. Deployment architecture

`render.yaml` provisions a public Web service, PostgreSQL, private Key Value/Redis, private RQ worker, and hourly guest cleanup. The blueprint is prepared but does not create resources until it is applied in a Render account. Domain ownership, service costs, secrets, health, and restore strategy require operator confirmation. The first region is Singapore.

`compose.web.yaml` is available for a local multi-service rehearsal with PostgreSQL and Redis. Production requires TLS at the hosting edge and secrets supplied by the hosting provider.

## 11. Desktop packaging

`START_ORS.bat` / Python setup remain developer mode. `.github/workflows/build-windows.yml` describes a Windows runner using Python 3.15.2 x64, PyInstaller, tests, and Inno Setup. An installer is only considered released after the workflow succeeds and a clean Windows machine without Python validates launch, import, solver, export, data persistence, and uninstall behavior.

## 12. Source-of-truth documents

- 29 module baseline: `MODULE_CATALOG.md`.
- Actual solver variants/exclusions: `MODULE_IMPLEMENTATION_SCOPE.md`.
- Tenant and runtime flow: `CLOUD_ARCHITECTURE.md`.
- Security controls and gaps: `SECURITY_MODEL.md`.
- Public deployment: `WEB_DEPLOYMENT.md`.
- Release state and tests: `IMPLEMENTATION_STATUS.md` and `CHANGELOG.md`.
