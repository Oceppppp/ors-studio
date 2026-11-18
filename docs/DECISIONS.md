# ORS Architectural Decision Log

Baseline: 18 November 2026.

| ID | Decision | Status | Notes |
|---|---|---|---|
| ADR-001 | Keep Desktop local-first with per-user SQLite | Accepted | Desktop API remains loopback-only and does not require a Web account. |
| ADR-002 | Keep Public Web as a separate FastAPI entry point | Accepted | `orstudio.web_api:app`; never expose unauthenticated local `orstudio.api:app`. |
| ADR-003 | Reuse the 29-module solver registry across both editions | Accepted | Both editions dispatch through `registry.run_module()`. |
| ADR-004 | Public Web uses PostgreSQL via SQLAlchemy Core | Accepted | Schema evolution uses Alembic. |
| ADR-005 | Web identity uses Guest and registered USER principals | Accepted for beta | 24-hour guest sessions, 14-day account sessions; email verification/recovery deferred. |
| ADR-006 | Owner-scoped tenant data | Accepted | Every project-scoped cloud read/write requires owner filtering through project membership. |
| ADR-007 | Opaque session cookie, HMAC digest storage, Argon2 passwords | Accepted | HttpOnly, SameSite=Lax and Secure in production. |
| ADR-008 | Redis/RQ for production batch processing | Accepted | Production does not fall back to in-process worker pool. |
| ADR-009 | Batch tasks remain independent | Accepted | No cross-analysis DAG or output-to-input workflow in v0.4.0. |
| ADR-010 | HTML/CSS/native JavaScript ES modules | Accepted | React, TypeScript, Vite and Tauri are not current dependencies. |
| ADR-011 | Render Blueprint for first Public Web deployment | Accepted as deployment path | Blueprint is prepared, but no live service is provisioned yet. |
| ADR-012 | PyInstaller onedir + Inno Setup for Windows Desktop | Accepted as build path | Needs successful Windows workflow and clean-machine validation. |
| ADR-013 | No fabricated mathematical traces or unsupported solver claims | Accepted | Exact model coverage remains in `MODULE_IMPLEMENTATION_SCOPE.md`. |
| ADR-014 | User-provided Antigravity skills used progressively | Accepted | Read relevant full skill resources before each meaningful task; catalog presence is not integration proof. |

## Consequences

- Cloud features must not write to the Desktop SQLite database; Desktop API must not access Web principal tables.
- Render costs, secrets, TLS, backup/restore and domain setup require operator confirmation.
- v0.4.0 is beta foundation only; do not advertise email verification, password reset, user deletion/export, live cloud URL, or released installer until implemented and verified.
- The GitHub publishing script must never force-push or overwrite a version tag that points elsewhere.
