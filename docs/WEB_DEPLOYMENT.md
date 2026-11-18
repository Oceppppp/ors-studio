# Public Web Deployment — Render Blueprint

The repository contains `render.yaml` to describe the first hosted deployment. It provisions:

- Public FastAPI web service (`ors-studio-web`).
- Managed PostgreSQL (`ors-studio-postgres`).
- Private Redis-compatible Key Value (`ors-studio-redis`).
- Private RQ background worker (`ors-studio-worker`, initially two instances for independent batch tasks).
- Hourly guest-data cleanup cron (`ors-studio-guest-cleanup`).

The Blueprint uses paid starter resources for durable data and continuous worker availability. Render's free web services can spin down and lose local filesystem changes; free Postgres databases expire after 30 days and are not suitable for production data. Check Render pricing before applying the Blueprint.

## Before deployment

1. Publish this repository to `Oceppppp/ors-studio` with the `main` branch.
2. Create a Render account and connect the GitHub repository.
3. Open Render Dashboard → **New** → **Blueprint** and select this repository.
4. Review the services and region. Singapore is selected as the initial region; it can be changed before provisioning.
5. Review estimated costs and create the Blueprint. PostgreSQL and Redis should only accept private/internal connections.
6. Wait for PostgreSQL, Key Value, worker, and web service to become healthy.
7. Verify the web service health endpoint: `/api/health`.
8. Test guest mode, registration/login, workspace isolation, upload, single analysis, batch analysis, and exports with two separate browser profiles.

## Environment configuration

Render Blueprint generates `ORS_SESSION_SECRET`. `DATABASE_URL` and `REDIS_URL` are injected from private Render services. `ORS_ENV=production` and `ORS_COOKIE_SECURE=true` are set automatically.

Set `ORS_ALLOWED_ORIGINS` only when adding a deliberate same-origin-compatible public hostname. The service validates the request's Origin host against the request Host by default.

## Custom domain

After the first deploy:

1. Open the web service in Render.
2. Settings → Custom Domains → Add Custom Domain.
3. Enter a domain you own, configure the DNS records shown by Render, and wait for certificate provisioning.
4. Re-test login cookies and file uploads over HTTPS.

A domain such as `ors-studio.com` is only an example; it is not registered by this project.

## Local cloud stack (Docker)

Copy `.env.example` to `.env`, change the development session secret, then run:

```bash
docker compose -f compose.web.yaml up --build
```

The Compose file starts PostgreSQL, Redis, the Web API, and the RQ worker. Open `http://localhost:8000`. Stop with Ctrl+C; data in the named Postgres volume persists between restarts.

## Database migrations

Render's web start command runs:

```bash
alembic upgrade head
```

Create a new Alembic revision whenever the cloud schema changes. Do not modify a database manually or rely on `create_all` for schema evolution. `cloud_store.init_db()` remains an idempotent first-run safety net.

## Release and deployment sequence

1. Push a reviewed commit to `main`.
2. GitHub Actions runs the public-Web test workflow and the Windows Desktop build workflow.
3. Render auto-deploys Web and worker from `main`.
4. Confirm health and functional smoke tests.
5. Create a version tag only after the deploy is verified; the Windows GitHub Release workflow publishes installer artifacts on tag push.

## Rollback

Use Render's Deploys page to roll back the Web and worker services to the previous known-good commit. Review database compatibility before rollback if a migration added or changed columns. Back up PostgreSQL before destructive schema migrations.

## Current release caveats

- This repository is prepared for deployment; a live public URL does not exist until the repository is published and the Blueprint is applied in your Render account.
- Email verification and password recovery are not yet implemented. This is a public beta foundation and should not be advertised as a fully production-audited identity platform.
- Dataset rows/columns are stored in PostgreSQL. Original uploaded binary workbooks are not currently retained in object storage.
- Render services incur usage costs; the paid plans in the Blueprint are illustrative starter sizes, not a cost quote.
