# Download and install SparkTwin

**Recommended:** Open the [SparkTwin GitHub Releases](https://github.com/hossain0707/SparkTwin/releases) page, select the most recent **development preview** and choose your operating system's installer under **Assets**. You do **not** need Python to run the packaged desktop app.

| System | Download | Installation |
| --- | --- | --- |
| Windows 10/11, x64 | `SparkTwin-Setup-Windows-x64.exe` | Open the downloaded installer, follow the wizard, then launch from Start Menu. No administrator elevation is required for a per-user install. |
| macOS Apple Silicon | `SparkTwin-macOS-Apple-Silicon-unsigned.dmg` | Open the DMG and drag SparkTwin to Applications. |
| macOS Intel | `SparkTwin-macOS-Intel-unsigned.dmg` | Open the DMG and drag SparkTwin to Applications. |
| Ubuntu 24.04, x64 | `SparkTwin-Linux-Ubuntu-x64.deb` | Install through the software installer or `sudo apt install ./SparkTwin-Linux-Ubuntu-x64.deb`; then launch SparkTwin from the applications menu. |

**Portable alternatives:** Windows ZIP (extract entire `SparkTwin` folder and run `SparkTwin.exe`), Linux `.tar.gz` (extract entire `SparkTwin` directory and launch its executable; GUI libraries are required). Keep all included files together.

## Preview security warning

Packages are currently unsigned. Windows SmartScreen and macOS Gatekeeper may reject them, and there is no signed or notarized commercial release. We do not recommend disabling system-wide security features. If your organization's policy prohibits unsigned software, use the reviewed source installation instead or wait for a signed release.

## Check SHA-256 download integrity

Download `SHA256SUMS.txt` from the **same release**. From the folder containing the installer and checksum file:

```powershell
# Windows PowerShell — compare displayed value with the corresponding SHA256SUMS.txt entry
Get-FileHash .\SparkTwin-Setup-Windows-x64.exe -Algorithm SHA256
```

```bash
# macOS (choose your actual DMG filename)
shasum -a 256 SparkTwin-macOS-Apple-Silicon-unsigned.dmg
# Linux (verifies named files present in the folder)
sha256sum -c SHA256SUMS.txt --ignore-missing
```

Matching a checksum only confirms that the local package matches the release manifest, not the publisher's identity; release provenance and signing are separate future requirements.

## Using SparkTwin

1. Open SparkTwin. The native application starts a local-only service on `127.0.0.1` and displays the interactive planner.
2. Enter model size, precision, context length and concurrency in **Capacity Planner**. Results are estimates, not observed hardware benchmarks.
3. Save/compare scenarios, import recorded measurements in **Benchmark Lab**, and export PDFs.
4. DGX Spark hardware is **optional**. For read-only SSH inspection, first confirm secure command-line OpenSSH connectivity and independently verify the target's host key.

Local scenario data is stored in `~/.sparktwin`. No cloud signup or DGX Spark device is required to use the planner.

## Verification and limitations

CI creates release assets only after automated tests and packaged `--self-test` checks pass on Windows, macOS Intel, macOS Apple Silicon, and Ubuntu. Clean-machine GUI acceptance, signed/notarized distribution and real DGX Spark validation remain open. See [docs/RELEASE.md](RELEASE.md).
