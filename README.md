# ORS Studio 0.4.0

**Operations Research Studio** is a dual-distribution Operations Research and Quantitative Methods platform: a public multi-user Web edition (Guest Mode or account) and a local/offline Desktop edition. The baseline catalog contains 29 analysis modules; each module documents its supported models and limitations.

## Choose how to use ORS

### Public Web (multi-user)

The Web edition uses FastAPI, PostgreSQL, Redis/RQ workers, and HttpOnly cookie sessions. Every project belongs to one principal (registered account or guest), and every project-scoped query is filtered by owner_id. Guests can try the app without signing in and have limited quotas with a 24-hour session. Users can register and sign in.

### Public deployment: Netlify + Railway

- **Netlify** hosts the static frontend from the frontend directory.
- **Railway** runs the Python FastAPI API, PostgreSQL, Redis, the private RQ worker, and scheduled guest cleanup.
- Netlify rewrites browser requests from /api/* to the Railway API so session cookies remain same-origin from the browser's perspective.
- The Railway API and worker share the same PostgreSQL database, Redis queue, and solver registry.

Follow the complete [Netlify + Railway deployment guide](docs/RAILWAY_NETLIFY_DEPLOYMENT.md). The repository includes netlify.toml, a build-time proxy configuration script, a Railway Dockerfile, and railway.toml.

### Local Web development

Copy .env.example to .env, replace the development session secret, then run:

~~~bash
docker compose -f compose.web.yaml up --build
~~~

Open http://localhost:8000. Apply database migrations with alembic upgrade head. The worker runs separately from the HTTP process.

### Desktop (local/offline)

The Desktop edition works locally without an account. Data is stored in each computer user's profile using SQLite. Windows source setup supports Python 3.15.2; release installers bundle the runtime and dependencies.

- Windows source setup: run setup_windows.bat, then START_ORS.bat.
- Linux/macOS development: use run_local.sh and the developer guide.

## Modules and features

- 29-module baseline across Operations Research, POM, and Quantitative Methods.
- XLSX and CSV import, preview, validation, worksheet selection, and column mapping.
- Single analysis and batch job processing.
- Forecast comparison with MAD, MSE, RMSE, MAPE, and holdout-MAD method selection.
- Analysis results and Excel, CSV, and PDF exports.
- Web mode with guest/account identity, personal workspaces, and PostgreSQL tenant isolation.

## Development and tests

~~~bash
python -m pip install -r requirements-dev.txt
PYTHONPATH=backend python -m pytest -q
~~~

Web test/runtime dependencies are listed in requirements-web.txt. Railway cloud runtime is pinned to Python 3.13.5; Windows Desktop source targets Python 3.15.2.

## Documentation

- [User Guide](docs/PANDUAN_PENGGUNA.md)
- [Netlify + Railway Deployment](docs/RAILWAY_NETLIFY_DEPLOYMENT.md)
- [Cloud Architecture](docs/CLOUD_ARCHITECTURE.md)
- [Security Model](docs/SECURITY_MODEL.md)
- [Technical Architecture](docs/TAD.md)
- [Module Implementation Scope](docs/MODULE_IMPLEMENTATION_SCOPE.md)
- [UI Design Review](docs/UI_DESIGN_REVIEW.md)
- [Release & GitHub](docs/RELEASE_AND_GITHUB.md)

## Release status

ORS Studio 0.4.0 adds the Public Web multi-user foundation. Source and automated tests can be exercised locally. A live deployment, email verification/password recovery, independent security review, load testing, and the Windows installer built by GitHub Actions must be verified before calling the service production-ready.
