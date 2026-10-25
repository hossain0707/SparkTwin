# Verification ledger — 2026-10-25

## Confirmed in the local development environment

- **39 tests passed** with `python -m pytest -q` (Python 3.13, Linux container).
- `node --check sparktwin/web/app.js` passed.
- `python desktop_launcher.py --self-test` passed, verifying actual source UI assets and estimator import.
- Tests exercise memory conversion, GQA KV arithmetic, memory pressure, custom hardware, numeric bounds, benchmark domain refusal, persisted SQLite records, bounded atomic benchmark validation, shell-injection rejection, SSH command restrictions, localhost/Origin/token controls, API scenario flows, and PDF signatures.
- Live local API responded to `GET /api/health` with version and readiness.

## Browser acceptance blocker

System Chromium is present but sandbox policy returned `net::ERR_BLOCKED_BY_ADMINISTRATOR` while opening even `http://127.0.0.1` through Playwright. **No successful automated end-to-end browser screenshot or click-through is claimed.** Rerun on GitHub runner or a normal developer workstation.

## External or future gates

| Gate | State |
| --- | --- |
| Windows/macOS/Linux CI matrix and packaged artifacts | Workflow configured; results not yet confirmed |
| Clean machine Windows executable | Pending |
| Mac Intel/Apple Silicon installed DMG test | Pending |
| Ubuntu DEB installed and launched | Pending |
| Direct Ethernet/LAN/VPN against a real DGX Spark | Pending |
| Physical real model memory-fit and throughput calibration | Pending |
| Penetration test, dependency audit and code signing | Pending |
| Model-estimator held-out real-world validation | Pending |

**Do not use percentages of project completion or claim full production readiness without evidence.**

## CI package-build evidence

**Verified cross-platform CI:** On 2026-10-25, [workflow run 40151668581](https://github.com/hossain0707/SparkTwin/actions/runs/40151668581) completed **13/13 jobs successfully**, including 9 OS/Python test combinations and all four packaged targets. Downloadable unsigned preview artifacts were published for Windows x64, macOS Apple Silicon, macOS Intel and Ubuntu x64. This is build verification, **not** clean-machine installation, real DGX Spark hardware acceptance or code signing.

