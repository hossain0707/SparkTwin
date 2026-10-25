# Installation, packaging and production-release gates

## Supported source install

Requirements: Python 3.11+, internet for initial reportlab dependency download, browser. Optional SSH commands require a system OpenSSH client and working SSH credentials. Source quick-start commands are in README.

## GitHub Actions: unsigned development packages

The workflow `.github/workflows/ci.yml` runs Python tests on Windows, Ubuntu and macOS with Python 3.11/3.12/3.13. Build jobs then package the optional webview desktop launcher with PyInstaller and upload **unsigned preview artifacts** to GitHub Actions:

- Windows x64: ZIP with the executable and runtime files.
- macOS Intel and Apple Silicon: unsigned DMG containing `.app`.
- Ubuntu x64: DEB and portable TAR.GZ. Linux requires WebKitGTK/GTK system libraries.

These are **targets**, not verified releases until the actual workflows succeed and packages are installed on clean machines. PyInstaller packaging includes the frontend under `sparktwin/web`. `desktop_launcher.py --self-test` checks included assets before app distribution.

## Signed release sign-off checklist

1. All CI OS builds green, dependencies audited, checksum generated and provenance retained.
2. Test ordinary installation, first launch, local access and update/uninstall on clean physical/virtual machines for all supported targets.
3. Test network and SSH alias diagnostics using actual DGX Spark with independently checked host key.
4. Run representative real model experiments and validate estimator confidence; no unverified throughput claims.
5. Penetration test local API/IPC, file import, input validation and native app packaging.
6. Windows code signing (appropriate identity) and macOS Developer ID notarization, or clearly label unsigned previews without asserting bypass safety.
7. User-readable release notes, accessible onboarding, checksum verification, security disclosure and rollback plan.

## Developer package procedure

`python -m pip install -e '.[build,dev]'`; `python -m pytest -q`; `pyinstaller --onedir --windowed --name SparkTwin --add-data "sparktwin/web:sparktwin/web" --collect-all webview desktop_launcher.py` (use semicolon instead of colon on Windows). Run packaged binary with `--self-test`.

## Preview artifact availability — 2026-10-25

**Verified cross-platform CI:** On 2026-10-25, [workflow run 40151668581](https://github.com/hossain0707/SparkTwin/actions/runs/40151668581) completed **13/13 jobs successfully**, including 9 OS/Python test combinations and all four packaged targets. Downloadable unsigned preview artifacts were published for Windows x64, macOS Apple Silicon, macOS Intel and Ubuntu x64. This is build verification, **not** clean-machine installation, real DGX Spark hardware acceptance or code signing.

