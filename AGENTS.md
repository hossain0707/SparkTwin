# Instructions for coding agents — SparkTwin

Start with `START_HERE.md`. Never guess existing implementation or replace functional code with a mockup.

## Architecture and code map

- `sparktwin/model.py`: rigorous unit conversion and deterministic memory accounting.
- `sparktwin/calibration.py`: conservative provenance-aware interpolation from imported observations.
- `sparktwin/store.py`: SQLite and backup format; no secret storage.
- `sparktwin/ssh.py`: optional, *read-only* OpenSSH subprocess commands.
- `sparktwin/app.py`: 127.0.0.1 HTTP API with per-session token and request validation.
- `sparktwin/pdf.py`: PDF evidence export; do not certify findings.
- `sparktwin/web`: browser UI, responsive design and local assets; no CDNs.
- `desktop_launcher.py`: PyInstaller/pywebview entry and browser fallback.
- `.github/workflows/ci.yml`: OS matrix and unsigned development build candidates.

## Invariants

1. Never fabricate measured tokens/sec, GPU utilization, latency, power usage, test outcomes, benchmark provenance or certification.
2. DGX Spark shares CPU/GPU unified memory. Clearly label assumptions and convert vendor decimal GB into binary GiB correctly.
3. Do not silently reinterpret KV head geometry, quantization metadata or available memory; validate user inputs.
4. Local API must bind only 127.0.0.1, guard Host/Origin and API token. Avoid accepting CORS, network-exposed listeners or unauthenticated writes.
5. No SSH host-key auto-acceptance (`StrictHostKeyChecking=yes`), no shell interpolation of user-controlled input, no password/private key storage, no remote installation without explicit user action.
6. Do not add paid cloud services or real customer secrets; do not commit `.env`, database files, private keys or tokens.
7. All UI dynamic content must be escaped; honor reduced-motion and responsive design. Keep the GitHub README professionally styled and truthful.
8. Tests must cover mathematical invariants, API guards, data persistence, import limits and report generation. Run tests before each push.
9. Preserve clean, documented development continuity; update START_HERE, docs, README and roadmap when scope changes.
10. Signing, notarization, hardware acceptance and independent audit remain external release gates until genuinely performed.
