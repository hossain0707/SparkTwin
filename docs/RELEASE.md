# SparkTwin cross-platform desktop release pipeline

## GitHub releases — one-click downloads

The distribution workflow `.github/workflows/ci.yml` runs on pushes to `main`. Its testing matrix covers Python 3.11–3.13 on Windows, macOS and Ubuntu. After tests pass, platform builders package a self-contained native app, run `desktop_launcher.py --self-test` on each packaged executable, and upload distribution artifacts.

The `preview-release` job runs only for `main`, downloads platform artifacts, verifies **all six** expected packages are nonempty, produces a `SHA256SUMS.txt`, and creates an **immutable prerelease tag** of the form `v0.1.0-preview.<GitHub Actions run number>` with the assets and `docs/PREVIEW_RELEASE_NOTES.md`. That GitHub Release is the user-friendly download location; Actions artifacts remain temporary.

### Installer output matrix

| OS | Format | Notes |
| --- | --- | --- |
| Windows x64 | `SparkTwin-Setup-Windows-x64.exe` | Per-user Inno Setup installer, Start Menu entry, optional desktop icon, uninstaller. Unsigned. |
| Windows x64 | `SparkTwin-Portable-Windows-x64.zip` | Extract whole folder, launch EXE. |
| macOS Apple Silicon | `SparkTwin-macOS-Apple-Silicon-unsigned.dmg` | Drag the app into Applications. Unsigned and not notarized. |
| macOS Intel | `SparkTwin-macOS-Intel-unsigned.dmg` | Drag the app into Applications. Unsigned and not notarized. |
| Ubuntu Linux x64 | `SparkTwin-Linux-Ubuntu-x64.deb` | DEB installation using system GTK / WebKit dependencies. |
| Linux x64 | `SparkTwin-Portable-Linux-x64.tar.gz` | Extract portable folder with GUI dependencies available. |

Detailed user onboarding: [INSTALL.md](INSTALL.md). Published notes: [PREVIEW_RELEASE_NOTES.md](PREVIEW_RELEASE_NOTES.md).

## Constraints

- The binaries are **developer previews**, not signed stable releases. Successful CI means packages built and packaged smoke checks passed; it does not prove clean installation, functional GUI correctness or DGX Spark hardware compatibility.
- Do not market memory/throughput estimates as measured or guaranteed. Benchmarks are only imported and calibrated from user-supplied evidence.
- Releases are tagged from GitHub Actions using `GITHUB_TOKEN` scoped to `contents: write` only in the publish job. PRs cannot create releases. Tags are never force-updated or overwritten.
- Commit updates to `main` create a **new** numbered preview release; this preserves reproducibility at the cost of release clutter. Settle a version/release process before general availability.
- SHA256SUMS.txt is generated from exact release assets; verify downloads against it.

## Pending stable-release checklist

1. Windows code signing and macOS Developer ID signing/notarization, and publisher verification.
2. Clean-machine install / first-launch / uninstall tests, including Windows Defender and macOS Gatekeeper outcomes, on each advertised target.
3. Actual DGX Spark SSH tests using verified host fingerprints over LAN/Ethernet/VPN.
4. Independent security review of all local API and import surfaces and provenance hardening of the release workflow.
5. Correlate analytical memory estimates with physical inference measurements, document any discrepancies and limitations.
6. Accessible GUI acceptance on real OS desktops, formal release notes and tested upgrade/rollback procedures.

**Never claim the software is a certified NVIDIA product or a production-tested simulator before these gates close.**
