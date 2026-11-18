---
name: desktop-security-release
description: Secure and package the ORS Tauri desktop application with a local Python sidecar for Windows distribution.
---
# Desktop Security and Release

## Procedure
1. Verify the backend binds only to 127.0.0.1 and uses an ephemeral port.
2. Implement a one-time random handshake token passed from Tauri host to sidecar; do not persist or log it.
3. Restrict Tauri capabilities and sidecar permissions to the minimum required.
4. Validate file paths, upload size, file signature, and generated storage identifiers.
5. Ensure uploaded macros, formulas, scripts, and external content are never executed.
6. Build the Python backend with pinned dependencies and a recorded license inventory.
7. Bundle the executable as a correctly target-suffixed Tauri sidecar.
8. Store mutable data in per-user application data directories, not the installation directory.
9. Test installer, update, repair, uninstall, database migration, and data retention on a clean Windows VM.
10. Produce checksums, release notes, SBOM/dependency inventory, and known limitations.

## Guardrails
- Do not expose the local API to the LAN.
- Do not include developer secrets in installer artifacts.
- Do not claim clean-machine compatibility until the test actually passes.
