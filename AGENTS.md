# ORS Workspace Rules for Antigravity

## Read specifications first

Before implementing or refactoring, read the relevant parts of:
- `docs/SRS.md` — product requirements and release boundaries;
- `docs/TAD.md` — the v0.4.0 dual Web/Desktop architecture;
- `docs/CLOUD_ARCHITECTURE.md` and `docs/SECURITY_MODEL.md` — tenancy, authentication, and security invariants;
- `docs/MODULE_CATALOG.md` and `docs/MODULE_IMPLEMENTATION_SCOPE.md` — 29-module baseline and exact solver coverage;
- `docs/IMPLEMENTATION_STATUS.md` — implemented, unverified, and deferred features;
- `docs/DECISIONS.md` and `design-system/ors-studio/MASTER.md` — accepted architecture/UI decisions.

Do not invent requirements, solver capabilities, test results, deployment state, or installed Antigravity skills.

## Current architecture (v0.4.0)

ORS has two distributions sharing the same Python solver registry:

1. **Desktop/local:** `orstudio.api:app`, SQLite through `backend/orstudio/database.py`, loopback-only `127.0.0.1`, no online account required. The desktop launcher remains local-first.
2. **Public Web:** `orstudio.web_api:app`, SQLAlchemy persistence (`cloud_store.py`), PostgreSQL in production, opaque cookie sessions, Guest and registered USER principals, per-principal project/data authorization, Redis/RQ batch queue, and private background worker.
3. **Shared solver layer:** stable module keys and algorithms live in `backend/orstudio/modules/` and are dispatched through `registry.run_module()` by both editions.
4. **Frontend:** HTML/CSS/native JavaScript ES modules in `frontend/`, served by FastAPI on a same-origin route. Do not claim React/TypeScript/Vite/Tauri are implemented.
5. **Public deployment blueprint:** `render.yaml` defines Web, worker, Redis-compatible Key Value, PostgreSQL, and guest cleanup. A blueprint file is not proof of a live deployment.
6. **Windows Desktop packaging:** GitHub Actions builds Python 3.15.2 x64 PyInstaller onedir + Inno Setup. It is a build recipe until a successful workflow and clean-machine test are recorded.

## Security invariants

- Never expose `orstudio.api:app` on a public interface. It is the local desktop API and is unauthenticated by design.
- Public Web must use `orstudio.web_api:app`, PostgreSQL, secure cookies, Redis-backed rate limiting and RQ in production.
- Every cloud read/write for project, dataset, analysis, or job data must enforce principal ownership in the database query. Frontend hiding is not authorization.
- Session tokens are random, opaque, and stored only as HMAC digests. Passwords use Argon2. Never log raw tokens, passwords, full datasets, or private paths.
- Reject cross-origin state-changing requests. Keep `HttpOnly`, `SameSite=Lax`, and production `Secure` cookie flags.
- Guest sessions expire after 24 hours and are purged by the scheduled cleanup job. Guest quotas are product controls, not a substitute for abuse monitoring.
- Uploaded macros, formulas, scripts, or workbook external links must never be executed.
- Do not commit `.env`, credentials, database dumps, local SQLite data, uploaded datasets, build outputs, or secrets.
- Do not advertise account email verification or password recovery: they are not implemented in v0.4.0.

## Architectural invariants

1. Keep code modular; do not create giant files that combine UI, API, database, solver, and export responsibilities.
2. Keep the local SQLite repository separate from the cloud PostgreSQL repository. Do not silently mix local and cloud data paths.
3. Preserve the 29 stable module keys. Document every implemented variant and limitation in `MODULE_IMPLEMENTATION_SCOPE.md`.
4. Validate solver inputs at the backend boundary and inside the model implementation. Do not fabricate iterations, sensitivity values, dual values, confidence intervals, or convergence diagnostics.
5. Output must be JSON-serializable and identify assumptions/limits. Mark exact, heuristic, approximate, or stochastic methods accurately.
6. Preserve dataset mapping provenance in saved analysis input; strip provenance before calling the solver.
7. Batch items are independent jobs in v0.4.0. Do not claim workflow DAG/dependency scheduling or output-to-input chaining.
8. Production batch work must use Redis/RQ. The in-process worker pool is development/test-only and must never be the production fallback.
9. PostgreSQL schema changes require an Alembic revision. Never rely on `create_all()` as a schema migration strategy.
10. Use the ORS Operations Workbench design system; avoid generic AI dashboards, random gradients, emoji icons, and decorative cards with fake data.

## Coding and verification standards

- Python: type hints for public interfaces, small functions, clear exceptions, Pydantic at API boundaries, pytest tests.
- JavaScript: ES modules, feature-oriented files, safe DOM rendering, no inline event handlers, explicit API error handling.
- Use UTC for persisted timestamps; localize only in presentation.
- Before meaningful changes, identify and read the applicable owner-provided Antigravity `SKILL.md` and ORS project-specific skill. Use progressive disclosure; do not load all 339 catalogued skills for every task.
- Run `python -m pytest -q`, `python -m compileall -q backend run_app.py`, and `node --check` for changed frontend JS files.
- For cloud changes, also test Guest flow, registered account flow, second-user isolation, migration, and queue behavior.
- For public release, additionally require successful Windows CI, successful Render deploy, HTTPS checks, PostgreSQL backup/restore validation, and an independent security review.
- Report exactly which skills, commands, and tests were actually used. Never claim a cloud URL, installer, or GitHub release exists before verifying it.

## Mathematical correctness gate

Before declaring a solver variant complete:
1. Document formulation, variables, constraints, units, objective, assumptions, and tolerances.
2. Add independently verified golden test vectors.
3. Add infeasible/boundary/degenerate tests relevant to the model.
4. Cross-check small cases independently or by hand.
5. State whether the method is exact, heuristic, approximate, or stochastic.
6. Keep `MODULE_IMPLEMENTATION_SCOPE.md` synchronized with code.

## Antigravity skill protocol

Use `docs/ANTIGRAVITY_SKILL_CATALOG.md`, `docs/SKILL_USAGE_MATRIX.md`, and `docs/skill-audit.md` to identify relevant user-provided skills. Skill presence does not prove a CLI, MCP connector, browser, or deployment account is connected. Verify capabilities before use.
