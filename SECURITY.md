# Security Policy

## Scope

ORS Studio is a local-first desktop-style application. Its API binds to `127.0.0.1`, and user datasets are intended to remain on the user's computer. The GitHub repository and release assets do not need user datasets or credentials.

## Reporting a vulnerability

Please do not publish exploitable vulnerability details in a public issue. Once GitHub Private Vulnerability Reporting is enabled for this repository, use the repository's **Security → Advisories → Report a vulnerability** flow. If that feature is not available, contact the repository maintainers through the contact method listed on the GitHub profile or repository page.

Do not attach personal datasets, database files, access tokens, or other private information to a public report.

## Security expectations

- Never commit secrets, API keys, signing certificates, or user data.
- Keep the local API bound to loopback unless authentication and network security are designed and reviewed first.
- Validate uploaded CSV/XLSX files, size limits, archive structure, and parsed values.
- Treat spreadsheet cell contents as untrusted; do not execute formulas or macros.
- Review third-party dependency updates and build actions before release.
