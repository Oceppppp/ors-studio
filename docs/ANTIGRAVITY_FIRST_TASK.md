# Antigravity Continuation Prompt — ORS Studio v0.4.0

You are continuing the Operations Research Studio project. Read `AGENTS.md`, `docs/SRS.md`, `docs/TAD.md`, `docs/CLOUD_ARCHITECTURE.md`, `docs/SECURITY_MODEL.md`, `docs/MODULE_CATALOG.md`, `docs/MODULE_IMPLEMENTATION_SCOPE.md`, and `docs/IMPLEMENTATION_STATUS.md` before modifying code.

## Product decision

Maintain two editions:

1. Public Web: Guest access and registered accounts; PostgreSQL persistence; tenant isolation; Redis/RQ background jobs; Render deployment target.
2. Desktop/local: offline-capable local edition using SQLite and a loopback-only FastAPI endpoint.

Both editions must reuse the same Python solver registry and the same 29 module keys. Do not remove Desktop to build Web, or change a solver unless tests and scope docs are updated.

## Non-negotiable rules

- Never expose the unauthenticated Desktop API publicly.
- Every cloud project/dataset/analysis/job read or write must be owner-scoped in the database query.
- Keep opaque sessions, HMAC digest storage, Argon2 passwords, CSRF/origin controls, upload quotas and Redis rate limits.
- Do not claim email verification, password recovery, account deletion/export, workflow DAG, full POM-QM parity or live hosting until implemented and independently verified.
- Keep code modular and use the existing ORS UI design system; no generic AI-generated SaaS dashboard treatment.
- Preserve Python 3.15.2 x64 support for Windows Desktop source and the separate Render Python runtime.
- Apply Alembic migrations for cloud schema changes.

## Development workflow

Use the user-provided Antigravity skill catalog and `docs/SKILL_USAGE_MATRIX.md` to select relevant skills. Read each selected `SKILL.md` in full from the skill installation and read referenced resources where required. Apply TDD for security and domain logic, then run:

```bash
PYTHONPATH=backend python -m pytest -q
python -m compileall -q backend run_app.py
```

Run `node --check` on changed frontend files. For Web changes test Guest, register/login, guest upgrade, second-principal isolation, migrations, upload, solver, batch, job status, and export. For Desktop changes test local SQLite and loopback behavior.

## Next release gates

Complete account email verification and password recovery, formal terms/privacy and data deletion/export workflows, dataset storage quotas, independent security review, PostgreSQL/Redis integration tests, load/concurrency tests, monitoring/alerting, backup/restore, successful Render deployment, successful Windows installer workflow, and clean-machine testing before declaring production readiness.
