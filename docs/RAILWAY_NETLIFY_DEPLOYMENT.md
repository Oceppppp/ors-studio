# ORS Studio — Netlify + Railway Deployment

This is the recommended public-web hosting topology for ORS Studio. Netlify serves the static frontend. Railway runs the Python/FastAPI API, PostgreSQL, Redis, and private RQ worker. The Desktop edition and its local SQLite database remain separate.

## Service map

| Service | Platform | Role |
|---|---|---|
| ors-studio-web | Netlify | Static UI, pages, CSS, JavaScript |
| ors-studio-api | Railway | FastAPI public API |
| Postgres | Railway | Accounts, sessions, workspaces, datasets, analyses, jobs |
| Redis | Railway | Batch queue and shared rate-limit counters |
| ors-studio-worker | Railway | Private RQ solver worker |
| ors-studio-guest-cleanup | Railway Cron | Deletes expired guest workspaces |

The browser calls same-origin /api/* routes. Netlify rewrites those requests to the Railway API, keeping the browser URL and session cookie on the Netlify origin. Do not expose PostgreSQL or Redis public domains.

## 1. Railway: create the backend project

1. Open Railway and create a new project.
2. Add a service from GitHub and choose Oceppppp/ors-studio, branch main.
3. Railway detects the root Dockerfile. Keep the repository root as the service root.
4. Name the service ors-studio-api.
5. In the API service, confirm the config-as-code file is /railway.toml.
6. Generate a public domain for the API from Settings → Networking. Netlify needs this origin.

## 2. Railway: add PostgreSQL and Redis

From the Railway project canvas, add Database → PostgreSQL and Database → Redis. Keep both private.

In the API service Variables, add reference variables:
- DATABASE_URL = ${{Postgres.DATABASE_URL}}
- REDIS_URL = ${{Redis.REDIS_URL}}

Replace Postgres and Redis with the exact service names shown on the Railway project canvas if you named them differently.

Also set:
- ORS_ENV = production
- ORS_COOKIE_SECURE = true
- ORS_SESSION_SECRET = generate a long random secret in Railway
- ORS_ALLOWED_ORIGINS = https://<your-netlify-site>.netlify.app

ORS_ALLOWED_ORIGINS must be the exact Netlify site origin (scheme + host, no path, no trailing slash). It is used by the API same-origin mutation guard because Netlify proxies browser requests to Railway.

Railway injects PORT. Do not hard-code a different listening port.

## 3. Railway: create the worker service

1. Add another service from the same GitHub repository and branch.
2. Use the same repository root and root Dockerfile.
3. Name it ors-studio-worker.
4. In Settings → Deploy → Start Command, override the API command with:

~~~sh
sh /app/scripts/start-railway-worker.sh
~~~

5. Add the same reference variables:
   - DATABASE_URL = ${{Postgres.DATABASE_URL}}
   - REDIS_URL = ${{Redis.REDIS_URL}}
   - ORS_ENV = production

Do not generate a public domain for the worker. It only consumes jobs from Redis and writes results to PostgreSQL.

## 4. Railway: scheduled guest cleanup

Add a third service from the same repository for scheduled jobs:
- Service name: ors-studio-guest-cleanup
- Same root Dockerfile.
- Start Command: python -m orstudio.cleanup_guests
- Variables: DATABASE_URL = ${{Postgres.DATABASE_URL}} and PYTHONPATH = /app/backend
- Settings → Cron Schedule: 0 * * * * (hourly).

The cleanup command applies Alembic migrations before deleting expired guest workspaces. Do not assign this service a public domain.

## 5. Deploy and verify the Railway API

Wait until the API, Postgres, Redis, and worker are running. Open:

~~~text
https://<your-railway-api-domain>/api/health
~~~

Expected response includes status ok, database ok, queue_health ok, and module_count 29.

If the response is degraded, inspect API logs and verify both database reference variables before continuing.

## 6. Netlify: deploy the frontend

1. Open Netlify → Add new site → Import an existing project.
2. Connect GitHub and select Oceppppp/ors-studio, branch main.
3. Set:
   - Base directory: repository root (leave blank).
   - Build command: bash scripts/netlify-build.sh.
   - Publish directory: frontend.
4. In Site configuration → Environment variables, add:
   - ORS_API_ORIGIN = https://<your-railway-api-domain>
5. Deploy the site.

The build script generates frontend/_redirects with a proxy rule for /api/*. It requires HTTPS and fails early if the Railway API origin is missing.

## 7. Connect the Netlify origin back to Railway

After Netlify assigns a site URL, update the API service variable:
- ORS_ALLOWED_ORIGINS = https://<your-site>.netlify.app

Redeploy the Railway API. If you later attach a custom domain to Netlify, add that exact HTTPS origin to the comma-separated ORS_ALLOWED_ORIGINS list and redeploy the API.

## 8. Public smoke test

Test in two separate browser profiles:
1. Open the Netlify site and continue as Guest.
2. Create a project, import a small sample CSV, run one analysis, and run a small batch.
3. Register a separate account in the second browser profile.
4. Confirm the second user cannot read, update, export, or delete the first user's objects.
5. Confirm the batch job reaches SUCCEEDED and its result appears in history.
6. Test Excel, CSV, and PDF exports, then logout/login.

## Important operating notes

- PostgreSQL and Redis are required for production web mode. Do not set ORS_ENV=production without valid DATABASE_URL, REDIS_URL, and ORS_SESSION_SECRET.
- API and worker must use the same database and Redis references.
- Only the API should have public networking. PostgreSQL, Redis, worker, and cleanup service should remain private.
- Netlify proxying preserves the browser-facing origin; the API must allow the exact Netlify origin using ORS_ALLOWED_ORIGINS.
- Original binary Excel workbooks are not retained; parsed rows and columns are stored in PostgreSQL.
- Monitor Railway usage and Netlify build usage. Railway services and managed databases are usage-billed; do not assume the complete backend runs for free.
- Email verification, password recovery, independent security audit, load testing, and backup-restore drills remain launch requirements before describing this beta as production-audited.

## Desktop edition

This deployment does not change the Windows Desktop distribution. Desktop continues using local SQLite and its own local API. The Netlify site is the public browser edition.
