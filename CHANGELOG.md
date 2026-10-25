# Changelog

## [0.1.0] — 2026-10-25 (development MVP)

- Built a private, responsive AI memory planning dashboard for NVIDIA DGX Spark and custom unified-memory hardware.
- Added mathematically explicit weight/KV cache budgets, reserves and what-if comparisons.
- Added local scenario database, provenance-aware benchmark storage, conservative interpolation and JSON backups.
- Added read-only existing-OpenSSH remote memory/GPU inspection without a remote agent.
- Added PDF engineering assessment exports with caveats, authenticated loopback API, and strict input validation.
- Added animated GitHub README, technical architecture, equations, security notes and developer handover.
- Created cross-platform build/test workflow; native package and real hardware validation are not yet certified.
- Local result: 39 Python tests pass, JavaScript syntax and desktop source integrity checks pass; Chromium automated browsing blocked by sandbox policy.

### Cross-platform verification

**Verified cross-platform CI:** On 2026-10-25, [workflow run 40151668581](https://github.com/hossain0707/SparkTwin/actions/runs/40151668581) completed **13/13 jobs successfully**, including 9 OS/Python test combinations and all four packaged targets. Downloadable unsigned preview artifacts were published for Windows x64, macOS Apple Silicon, macOS Intel and Ubuntu x64. This is build verification, **not** clean-machine installation, real DGX Spark hardware acceptance or code signing.

