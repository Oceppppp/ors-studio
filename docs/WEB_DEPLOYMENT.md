# Public Web Deployment

The supported public hosting architecture for ORS Studio 0.4.0 is **Netlify + Railway**.

- Netlify serves the static frontend from the repository's frontend directory.
- Railway runs the FastAPI API, PostgreSQL, Redis, private RQ worker, and scheduled guest cleanup.
- The browser calls same-origin /api/* paths. Netlify rewrites these requests to Railway using the generated frontend/_redirects file.
- Guest and account sessions remain in HttpOnly Secure cookies on the Netlify site origin.

Follow the step-by-step [Netlify + Railway deployment guide](RAILWAY_NETLIFY_DEPLOYMENT.md).

## Required configuration

Netlify environment variable:
- ORS_API_ORIGIN = the HTTPS public origin generated for the Railway API service (no trailing slash).

Railway API environment variables:
- DATABASE_URL = reference to Railway PostgreSQL DATABASE_URL.
- REDIS_URL = reference to Railway Redis REDIS_URL.
- ORS_ENV = production.
- ORS_COOKIE_SECURE = true.
- ORS_SESSION_SECRET = long random secret generated in Railway.
- ORS_ALLOWED_ORIGINS = exact Netlify origin, such as https://your-site.netlify.app.
- PYTHONPATH = /app/backend.

Railway worker environment variables:
- DATABASE_URL and REDIS_URL references to the same PostgreSQL and Redis services.
- ORS_ENV = production.
- PYTHONPATH = /app/backend.

The API runs Alembic migrations before starting. The worker uses scripts/start-railway-worker.sh. Guest cleanup is a Railway scheduled job that runs python -m orstudio.cleanup_guests hourly.

## Local development

~~~bash
docker compose -f compose.web.yaml up --build
~~~

The local Docker stack provides PostgreSQL, Redis, Web API, and worker.

## Operational caveats

- The Railway API, PostgreSQL, Redis, and worker are required for production batch processing. Do not deploy the Web API with ORS_ENV=production but without DATABASE_URL, REDIS_URL, and ORS_SESSION_SECRET.
- Keep PostgreSQL, Redis, worker, and cleanup services private. Only the API receives a public domain.
- Railway resources are usage-billed. Review the current plan and estimated usage in your Railway account before provisioning.
- The original uploaded workbook binary is not retained; parsed rows and columns are stored in PostgreSQL.
- Email verification, password recovery, independent security review, load testing, and backup-restore testing remain before a production-audited launch.
