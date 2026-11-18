---
name: qa-release
description: Execute ORS release verification across backend, frontend, mathematical behavior, data import, desktop packaging, and clean Windows installation.
---
# ORS QA and Release

## Procedure
1. Confirm the target commit, version, lockfiles, and release scope.
2. Run format/lint/type checks for Python and TypeScript.
3. Run unit, property, integration, and contract tests.
4. Run a complete test workflow: create project -> import sample workbook -> validate -> configure two analyses -> execute -> view results -> export.
5. Verify a dependency workflow and a parallel independent batch.
6. Verify cancellation, failure, restart recovery, and database migration/backup.
7. Build the backend sidecar and desktop installer from a clean build environment.
8. Install on a clean Windows x64 VM without Python or Node.js.
9. Test launch, local API isolation, data persistence, export, update/uninstall behavior.
10. Publish release notes, hashes, dependency/license inventory, and known limitations.

## Reporting
Never mark a gate passed unless the exact command or manual test was executed and evidence is available. Include environment and logs with secrets redacted.
