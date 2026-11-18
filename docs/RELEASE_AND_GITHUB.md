# Public Repository, Web Deployment, and Desktop Release

## Public repository

Target: **`Oceppppp/ors-studio`** with Public visibility. The project includes MIT License, README (English and Indonesian), docs, issue templates, CI workflows, and `PUBLISH_TO_GITHUB.bat`.

Run `PUBLISH_TO_GITHUB.bat` from the project root on Windows. It:

1. Checks Git for Windows and GitHub CLI; offers `winget` install if the CLI is absent.
2. Opens browser-based GitHub authentication if needed.
3. Verifies the authenticated account is `Oceppppp`.
4. Requests `repo` and `workflow` scopes so it can create/push the public repository and workflow files.
5. Checks for `.env`, local databases and generated files before staging.
6. Creates the public repository if absent, or verifies the existing target origin before pushing.
7. Pushes `main`, then tag `v0.4.0` (without force-pushing or overwriting a different tag).

The GitHub connector session in ChatGPT and the Windows GitHub CLI login are separate credentials. Never paste a token into chat or commit it to the repository.

## Public Web deployment

1. Publish `main` to `Oceppppp/ors-studio`.
2. Sign in to Render and connect that public GitHub repository.
3. Render Dashboard → **New** → **Blueprint** → select `ors-studio` and review `render.yaml`.
4. Confirm service plans/costs and Singapore region. Provision Web, PostgreSQL, private Key Value/Redis, RQ worker and cleanup cron.
5. Wait for services to deploy; check `/api/health` and verify that database and queue report healthy.
6. Test Guest, registration, login, guest upgrade, upload, dataset privacy between two browser profiles, single analysis, batch worker, exports, logout and guest cleanup.
7. Configure backups and restore test before public promotion.
8. Add a custom domain only after you own it, configure DNS, verify TLS and test secure cookies. `ors-studio.com` is only an example and is not included or registered.

The repository Blueprint is configuration only. It does not provision resources until applied in your hosting account. Render services and persistent storage cost money; consult the Render Dashboard for exact current estimates.

## Local cloud rehearsal

Copy `.env.example` to `.env`, replace the development secret, then run:

```bash
docker compose -f compose.web.yaml up --build
```

Open `http://localhost:8000`. PostgreSQL and Redis run as local containers. Stop with Ctrl+C. The named Postgres volume persists local test data.

## Windows Desktop release

`.github/workflows/build-windows.yml` builds on a Windows runner with Python 3.15.2 x64, PyInstaller and Inno Setup. To produce release assets:

```bash
git tag v0.4.0
git push origin v0.4.0
```

The workflow publishes `ORS-Studio-Setup-0.4.0.exe`, portable ZIP and `SHA256SUMS.txt` if tests and installer build succeed. The first installer is unsigned; Windows SmartScreen may warn about an unknown publisher. Do not call the installer released until clean-machine tests pass.

## Release blockers

Email verification, password reset, data/account deletion/export workflows, privacy/terms, independent security review, load tests, monitoring, and tested restore are not complete. v0.4.0 is a public beta foundation, not a fully audited production identity service. Original uploaded workbook binary is not retained, only parsed rows and columns.
