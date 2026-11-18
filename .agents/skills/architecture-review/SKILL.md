---
name: architecture-review
description: Review ORS code changes against the modular architecture, API boundaries, deployment topology, data integrity, and migration strategy.
---
# Architecture Review

## Review checklist
1. Identify affected layers and verify each responsibility stays in its layer.
2. Check for circular dependencies, cross-module private imports, and oversized files.
3. Check API request/response schemas and backward compatibility.
4. Check transaction boundaries, dataset version immutability, and migration safety.
5. Check local backend loopback binding and one-time token handling.
6. Check job state transitions, dependency DAG, cancellation, retry, and concurrency limits.
7. Check file storage paths, checksums, retention, and backup/restore behavior.
8. Check dependency licensing, maintenance, package size, and installer impact.
9. Add/update tests and architecture decision records when required.
10. Report blocking issues separately from recommendations.
