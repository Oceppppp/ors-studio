# ORS Studio v0.4.0 — Local Verification Report

**Date:** 18 November 2026  
**Environment:** Python authoring runtime 3.13.5; temporary SQLite database for Web integration tests.

## Automated tests

```text
48 passed
```

The test suite covers:

- 29-module registry and runnable solver examples.
- Principal/guest registration, login, session and guest upgrade.
- Tenant isolation between separate browser principals for project, dataset, analysis, job and export reads.
- Web batch job dispatch and completion using the development worker pool.
- Partial dispatch failure leaves undispatched jobs in a terminal FAILED state.
- Guest normalized-storage quota enforcement and cross-scheme Origin rejection.
- Public Web frontend and authentication asset mounting.
- Cross-origin state-changing request rejection.
- Existing Desktop/local API, import, exports and solver regression tests.

## Additional checks

- Python source compilation with `python -m compileall -q backend run_app.py`.
- JavaScript syntax check with Node for all frontend JS modules.
- Alembic migrations through head against fresh temporary SQLite, including dataset storage quota column.
- YAML parsing of `render.yaml`: four services (web, worker, cron, keyvalue) and one Postgres database.

## Not verified in this environment

- Windows 10/11 Python 3.15.2 install and PyInstaller/Inno Setup build.
- Actual managed PostgreSQL and Redis/RQ services on Render.
- Public Render deployment, domain, TLS, and production secrets.
- Full browser E2E and accessibility audit on real browsers.
- Load/concurrency and security penetration tests.
- PostgreSQL backup and restore operation.

Therefore this report records **local source verification**, not production certification.
