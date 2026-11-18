# ORS Studio — Public Web Security Model

This document describes implemented controls and launch gaps. A public deployment is a multi-user service; the desktop/local API is not used as the cloud entry point.

## Implemented controls

### Identity and sessions

- Guest sessions are explicitly created through `POST /api/auth/guest`.
- Account registration/login use Argon2 password hashing (`argon2-cffi`); plaintext passwords are never stored.
- Browser sessions use random opaque tokens. Only HMAC-SHA256 token digests are persisted in `ors_sessions`.
- Session cookie is `HttpOnly`, `SameSite=Lax`, `Path=/`, and `Secure` in production.
- Registered sessions expire after 14 days; guest sessions expire after 24 hours.
- Guest can upgrade to an account in place, keeping the existing workspace.
- Login errors are generic to reduce account enumeration.

### Authorization and tenant isolation

- Every project belongs to a principal through `owner_id`.
- Dataset, analysis, and job queries are filtered by joining through the project and checking the current principal.
- Mutating project data requires a valid session.
- Cross-origin state-changing requests are rejected; CORS is not enabled for arbitrary origins.
- A second-visitor regression test verifies that one visitor cannot read or delete another visitor's dataset.

### Upload and response protection

- Guest uploads are limited to 5 MiB; registered accounts are limited to 20 MiB.
- Existing CSV UTF-8, XLSX ZIP structure, expanded-size, row, column, and cell-count validation remains active.
- Content-Security-Policy, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, and Permissions-Policy headers are set.
- Analysis exports are scoped to the owner and formula-like spreadsheet content is escaped by the export service.

### Abuse controls

- Login, registration, and guest creation have rate limits.
- When Redis is configured, counters are shared across web processes. Production fails closed when the shared rate limiter is unavailable.
- Guest quotas constrain upload size, normalized storage (15MiB), project count, datasets, batch size, and total analyses. Registered account normalized storage is capped at 250MiB by default.
- Batch processing runs in a private background worker.

## Important launch gaps

The 0.4.0 code is a **public beta foundation**, not an audited production identity service. Before promoting it as a general-purpose production app, implement and configure:

1. Email verification for new accounts.
2. Password reset / account recovery.
3. Terms of service and privacy notice, including dataset retention and deletion rules.
4. Formal account/data deletion and user export workflows.
5. Independent security review, dependency scanning, penetration testing, and concurrency/load testing.
6. Managed backups and a tested restore procedure for PostgreSQL.
7. Optional object storage for raw uploaded files; currently only parsed rows/columns are retained in PostgreSQL.
8. Observability/alerting for worker failure, DB saturation, upload abuse, and authentication anomalies.

Until these are complete, describe account creation as beta and do not promise verified-email recovery. Use a verified email address and a unique password. Guest workspaces are temporary.

## Required production secrets

- `DATABASE_URL`: private PostgreSQL connection string.
- `REDIS_URL`: private Redis-compatible connection string.
- `ORS_SESSION_SECRET`: long random secret for HMAC token digests; do not rotate without invalidating all active sessions.
- `ORS_COOKIE_SECURE=true` and `ORS_ENV=production`.
- `ORS_ALLOWED_ORIGINS`: optional explicit extra allowed origins; default same-origin host validation is active.

Do not commit `.env`, real secrets, database dumps, user datasets, or session tokens.
