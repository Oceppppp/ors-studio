# Changelog — ORS Studio

## v0.4.0 — Public Web + Desktop beta foundation (18 November 2026)

- Added a separate Public Web API while retaining the local Desktop API and SQLite data path.
- Added Guest Mode, registered account sign-in, Argon2 password hashing, opaque HMAC-digested session cookies, and guest-to-account upgrade.
- Added PostgreSQL/SQLAlchemy persistence, Alembic baseline migration, per-principal project/data ownership checks, Redis/RQ background jobs, and guest cleanup.
- Added tenant isolation and Web auth/batch regression tests.
- Added Render Blueprint and Docker Compose Web stack.
- Updated release, security, architecture and requirements documentation for dual distribution.
- Maintained shared 29-module solver registry and existing desktop workflows.
- Automated suite: 42 tests passed in authoring Python 3.13.5; production Postgres/Redis, live hosting and Windows installer still require external verification.

## v0.3.0 — Operations Workbench redesign (18 November 2026)

- Updated the interface design system and Operations Workbench navigation.
- Improved spreadsheet import, column mapping, batch work, exports and release preparation.
- Added Python 3.15-compatible Windows setup/build recipes.

## Earlier releases

See repository history and earlier tagged packages for initial local MVP milestones.
