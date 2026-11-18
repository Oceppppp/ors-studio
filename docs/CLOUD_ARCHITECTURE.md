# ORS Studio — Cloud Architecture (0.4.0)

## Distribution decision

ORS is now designed as two distributions with one shared solver catalog:

1. **Desktop/local** — `orstudio.api:app`, SQLite, loopback-only `127.0.0.1`, no account required.
2. **Public Web** — `orstudio.web_api:app`, PostgreSQL, cookie sessions, per-principal projects, Redis/RQ queue, same-origin browser frontend.

The desktop service remains intentionally unauthenticated because it binds only to loopback. The public Web service must never import or expose the desktop API as its public entry point.

## Request path

```text
Browser
  └── HTTPS / same-origin
       └── FastAPI web_api
            ├── session lookup (HMAC-hashed opaque cookie)
            ├── identity/guest quota dependency
            ├── tenant-scoped service functions
            ├── PostgreSQL (users, sessions, projects, datasets, analyses, jobs)
            └── Redis / RQ (batch analysis queue)
                  └── private worker
                       └── shared `registry.run_module()` solver catalog
```

## Tenant model

- `ors_principals`: registered account (`USER`) or temporary guest (`GUEST`).
- `ors_sessions`: opaque random browser token is stored as an HMAC-SHA256 digest, never plaintext.
- `ors_projects`: every row has a non-null `owner_id`.
- `ors_datasets`, `ors_analyses`, and `ors_jobs`: are owned transitively through `project_id`.
- Every project-scoped cloud-store method requires `owner_id`; lookup queries join through `ors_projects` and filter on the principal.
- Not-found responses intentionally do not reveal whether another user's object exists.

## Guest and account behavior

- Guest session expiry: 24 hours.
- Guest workspace: max 2 projects including the automatically-created default workspace.
- Guest upload: max 5 MiB per file, 3 datasets total, 15MiB normalized dataset storage, and 10,000 rows per dataset.
- Guest batch: max 5 tasks and max 10 saved analyses/jobs.
- Registered account limits are configurable in `web_api.py`; current defaults are 50 projects, 100 datasets, 40 tasks per batch, and 1,000 queued jobs / 5,000 saved analyses.
- Guest-to-account upgrade changes the principal record in place, so existing projects and datasets stay attached to the new account.
- `cleanup_guests` is scheduled hourly in the Render Blueprint and deletes guest principals after their expiry. Cascading foreign keys remove their project data.

## Processing model

- Single analysis uses the shared solver directly in FastAPI's sync endpoint threadpool.
- Batch analysis validates every task first, commits analysis/job records, and dispatches jobs to RQ.
- Local Docker development uses Redis + RQ so web and worker follow the same shape as production.
- Production requires `REDIS_URL`; the in-process queue is disabled in production.
- Web and worker processes use the same database and solver code; worker is a private service and receives no public HTTP traffic.

## Storage

- Uploaded workbooks are parsed and normalized into dataset rows/columns stored in PostgreSQL JSON columns.
- The current implementation does not preserve the original uploaded binary workbook after parsing. Re-upload is required to recover the original file. Object storage (R2/S3) is a planned extension for original files and large datasets.
- Exports are generated on demand from saved analysis output; generated files are streamed to the browser and are not retained by default.

## Database lifecycle

- Alembic baseline migration: `0001_initial_cloud_schema`.
- Web deployment start command runs `alembic upgrade head` before starting Uvicorn.
- `cloud_store.init_db()` uses SQLAlchemy metadata `create_all(checkfirst=True)` as a bootstrap safety net; production schema evolution should be made through new Alembic revisions, not ad-hoc table edits.

## Runtime separation

- Netlify: public static frontend. A generated _redirects rule proxies /api/* to the Railway API so the browser uses one origin.
- Railway API service: public HTTPS FastAPI service built from the root Dockerfile.
- Railway PostgreSQL: durable user/project/data store, private networking only.
- Railway Redis: private queue and shared rate-limit counters.
- Railway worker service: RQ worker, no inbound public routes; uses the same image and database/Redis variables as the API.
- Railway scheduled job: hourly cleanup of expired guest workspaces.
- Desktop installer continues using local SQLite and loopback-only local API.
