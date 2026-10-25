# START HERE — SparkTwin development handover

**Repository:** https://github.com/hossain0707/SparkTwin  
**Creator:** Md Najmul Hossain  
**Product:** SparkTwin — local-first AI model memory-capacity planner for NVIDIA DGX Spark and private inference hosts  
**State:** v0.1.0 development MVP, 25 October 2026; **not** production certified.

## Continue in another workspace

1. Clone `https://github.com/hossain0707/SparkTwin.git` and read this file, `AGENTS.md`, `README.md`, `docs/ARCHITECTURE.md`, `docs/CALCULATIONS.md`, `docs/VERIFICATION.md`, and `docs/PRODUCT_ROADMAP.md`.
2. Create a Python 3.11+ environment: `python -m pip install -e '.[dev]'` and run `python -m pytest -q`.
3. Run `node --check sparktwin/web/app.js` and `python desktop_launcher.py --self-test`.
4. Start `python -m sparktwin` to inspect the local UI. The machine does not need a DGX Spark for analytical scenario planning.
5. Implement only verified, evidence-backed features; update tests, README, docs, screenshot/demo and changelog for every material change.

## What was implemented

- Cross-platform local HTTP controller (`sparktwin/app.py`) bound to `127.0.0.1`, with random session token, Host/Origin validation, no CORS, restrictive CSP and bounded JSON bodies.
- Transparent memory model (`sparktwin/model.py`): model weights, geometry-aware KV cache, concurrency, quantization overhead, OS/runtime/activation reserve, safety margin, fit/tight/exceeds heuristics and what-if variations.
- Conservative benchmark calibration (`sparktwin/calibration.py`): no throughput predictions without at least two matching near-neighbor, user-provided measurements; sources and qualitative confidence surfaced.
- SQLite scenario and benchmark history (`sparktwin/store.py`), bounded imports, JSON export and restore. Data stored locally.
- Optional read-only SSH inspection (`sparktwin/ssh.py`) via existing `~/.ssh/config`, strict `known_hosts`, batch key/agent; Linux memory and device identity only; no remote agent.
- PDF reports (`sparktwin/pdf.py`) with scope labels, assumptions and calibration caveats.
- Fully local responsive dashboard (`sparktwin/web/index.html`, `styles.css`, `app.js` and `mark.svg`): live metrics, donut and segmented charts, form designer, scenario comparisons, benchmark import, read-only SSH panel and guide.
- Desktop entry point (`desktop_launcher.py`) uses pywebview optionally and falls back to browser.
- CI workflow (`.github/workflows/ci.yml`) tests Python 3.11–3.13 on Windows/macOS/Linux, packages unsigned platform builds and uploads artifacts if successful.
- Branded README SVGs in `docs/`, with tasteful CSS-only animation and reduced-motion fallback.

## Verified / not verified

**Local:** 39 pytest tests pass; JavaScript parses under Node; native app source self-test passes. Python runtime HTTP endpoints including auth, scenario CRUD and PDF have tests.  
**Not yet verified:** physical DGX Spark SSH connectivity, Chrome UI acceptance (Chromium automation policy blocked local navigations in this environment), Windows/macOS/Linux installers on clean machines, code signing/notarization, independent pen test, real-inference benchmarking.

**Never describe** analytic memory-fit heuristics as validated deployability, bandwidth ceiling as tokens/sec, or a user-entered throughput record as a measured SparkTwin result.

## Highest-priority remaining work

1. Run CI on GitHub and examine every OS matrix result. Address pywebview/backend bundling failures, including Linux WebKitGTK, without hiding them.
2. Test actual source app in real browsers: desktop/mobile flows, export/import, document keyboard navigation, responsive behavior.
3. Run read-only SSH checks on a real DGX Spark over Ethernet/LAN/VPN. Record OS/GPU info and limitations; never bypass SSH host-key verification.
4. Gather a real benchmark matrix for exact model revisions, context, concurrency, runtime and quantization; validate calibration error and tighten the applicability rule.
5. Build and manually test Windows/macOS/Linux deliverables on clean machines; sign Windows artifacts, notarize macOS, audit dependencies and perform independent security review.
6. Release a signed version only after acceptance evidence, changelog, release notes, and installation verification. Keep README truthful.

## Decisions

- Independence: no NVIDIA affiliation; no official capacity certification.
- Local-first: no paid cloud, hosted account, remote agent or telemetry needed.
- OpenSSH: use installed system OpenSSH, not a homebuilt SSH crypto implementation.
- Memory: separate decimal vendor GB and binary GiB; explicit assumptions.
- Calibration: measured input only, no extrapolation without comparable observations.
- Auth: loopback-only with an in-memory session token; no credentials in SQLite.
- All rights under Md Najmul Hossain pending a deliberate license selection.

## Suggested continuation prompt

> Continue the existing SparkTwin repository. Read START_HERE.md, AGENTS.md and all linked architecture, methodology, verification, security and release documents. First inspect existing files and run tests. Preserve the local-first design, avoid unsupported performance claims or invented benchmarks, and prioritize cross-platform CI, real DGX Spark SSH acceptance, browser tests and validated calibration. Update the complete README, documentation, status, changelog and tests with each change. Commit safely to this repository without exposing personal credentials or requiring paid services.
