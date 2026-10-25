# SparkTwin v0.1.0 — unsigned developer preview

**SparkTwin is an independent, local-first AI memory-capacity planner.** It does not issue official NVIDIA certifications or guarantee that a model will fit or meet performance targets. Inference throughput estimates require matching, user-provided measurement evidence.

## Which file should I download?

| Platform | Recommended file | Optional portable file |
| --- | --- | --- |
| Windows 10/11 x64 | `SparkTwin-Setup-Windows-x64.exe` | `SparkTwin-Portable-Windows-x64.zip` |
| macOS Apple Silicon (M-series) | `SparkTwin-macOS-Apple-Silicon-unsigned.dmg` | — |
| macOS Intel | `SparkTwin-macOS-Intel-unsigned.dmg` | — |
| Ubuntu Linux 24.04 x64 | `SparkTwin-Linux-Ubuntu-x64.deb` | `SparkTwin-Portable-Linux-x64.tar.gz` |

**Installation:** [docs/INSTALL.md](https://github.com/hossain0707/SparkTwin/blob/main/docs/INSTALL.md).

## Important preview limitations

- All desktop packages are **unsigned**; Windows may show SmartScreen warnings and macOS Gatekeeper may block running the app. Do not disable system-wide security protections to install it. Production signing/notarization and clean-machine user acceptance are pending.
- Source and packaged application self-tests check included files and the calculation engine. They are not full interactive GUI or DGX Spark hardware acceptance tests.
- Initial operation is local and does not require DGX Spark. Optional SSH inspection requires the user's verified OpenSSH configuration.
- The planner's memory estimates use explicit assumptions, not guaranteed real-world throughput or vendor certification.
- Verify downloaded asset integrity against the attached `SHA256SUMS.txt` before installing.

**Developer:** Md Najmul Hossain. Unofficial project; not affiliated with or endorsed by NVIDIA.
