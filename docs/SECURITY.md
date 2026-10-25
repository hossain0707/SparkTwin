# Security model — SparkTwin MVP

## Controls present

- Local-only HTTP server bound to `127.0.0.1` with strict Host/Origin checks, no CORS, CSP, no cloud telemetry and an unpredictable session token for API requests.
- Input schema bounds prevent non-finite / unreasonable numeric values, oversized JSON and batch imports.
- SQL statements are parameterized; data are stored in the user's home directory with restricted Unix permissions.
- Untrusted strings in UI tables are HTML-escaped and in PDFs XML-escaped.
- SSH uses system OpenSSH (`StrictHostKeyChecking=yes`, `BatchMode=yes`, timeout and sanitized alias) for predefined read-only commands only.
- No saved SSH password, private key, AI API credential, cloud account or telemetry service.

## Limitations and unverified controls

- Anyone with the user's local OS/browser access may access the application; no per-user account separation or database encryption.
- External processes on a compromised user account may inspect loopback traffic/process memory; not a defence against compromised desktops.
- USB/Ethernet/VPN connectivity is provided by the OS; SparkTwin does not discover machines, install VPN clients or change network configuration.
- Data exported to JSON/PDF are unencrypted and can contain sensitive notes or benchmark sources.
- Dependencies, PyInstaller binaries, macOS notarization, Windows signing and independent penetration testing must be verified before enterprise deployment.
- Browser navigation blocked in the current automated Chromium environment. This is an **unverified** GUI acceptance gate.

## Report a vulnerability

Use a private security channel with the repository owner rather than posting proof-of-exploit details in a public GitHub issue.
