# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 1.0.x | ✅ |
| Earlier builds ("Net Speed Widget Pro") | ❌ |

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

- Preferred: use GitHub's [private vulnerability reporting](https://github.com/iqbalmbadhan/Win11NetSpeedCompact/security/advisories/new).
- Alternatively, contact the maintainer through [Iqbal Mahmud's website](https://iqbalmahmud.com).

Please include the version, steps to reproduce and the impact. You can expect an acknowledgement within 7 days.

## What the application does

| Area | Behavior |
| --- | --- |
| Network | No network client code. No HTTP/API calls, telemetry or update checks. The only outbound action is opening the developer website in your browser when you choose that menu item. |
| Data read | Local network adapter byte counters (via `psutil`) and its own settings file. |
| Data written | `%APPDATA%\Win11NetSpeedCompact\settings.json`, plus one `Win11NetSpeedCompact` value under `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` while Start with Windows is on. |
| Privileges | Runs as the signed-in user and never requests elevation. |

## Hardening in place

**Application**

- `settings.json` is treated as untrusted input. Unknown keys are dropped, types are checked, numbers must be finite and are clamped to safe ranges, colors must be `#RRGGBB`, and files over 64 KB are ignored. A corrupted or tampered file falls back to defaults instead of crashing.
- Settings are written atomically (temp file + rename), so an interrupted write cannot corrupt them.
- Win32 calls use explicit `ctypes` prototypes and `use_last_error`, avoiding handle truncation and unreliable error codes.
- The startup command is a fully quoted absolute path, so paths with spaces cannot be misinterpreted.
- Only this app's own legacy startup value is ever removed; other startup entries are never touched.

**Supply chain**

- Every dependency, including transitive ones, is pinned to an exact version and SHA-256 hash (`requirements.txt`, `requirements-build.txt`) and installed with `--require-hashes`.
- Dependencies are installed into isolated virtual environments, never the global Python.
- `pip-audit` checks the locked dependencies for known vulnerabilities on every push, every pull request, weekly, and before every build.
- Dependabot proposes updates for Python packages and GitHub Actions weekly.
- CodeQL (`security-extended`) scans the Python code and the workflow files.

**Build and release**

- GitHub Actions are pinned to full commit SHAs, not movable tags.
- Workflows start with no permissions and each job requests only what it needs. Only the release job can write to the repository.
- Checkouts do not persist the GitHub token.
- Tests must pass before an EXE is built.
- The EXE is built without UPX compression, which reduces antivirus false positives.
- Each workflow build gets a signed [build provenance attestation](https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations) and a SHA-256 checksum.
- Optional Authenticode signing: the certificate is imported only for the duration of signing and selected by thumbprint, so its password never appears on a command line.

## Verifying a download

Check the SHA-256 checksum as described in the [README](README.md#verifying-downloads). For EXEs built by the workflow after build attestations were added, you can also confirm the file was built from this repository by GitHub Actions:

```powershell
gh attestation verify .\Win11NetSpeedCompact.exe --repo iqbalmbadhan/Win11NetSpeedCompact
```

## Known limitations

- The EXE is not yet signed with a publicly trusted code-signing certificate, so Windows SmartScreen may warn on first run.
- Anyone who can already run code as your Windows user can change the settings file or startup entry. That is outside this app's security boundary.
- Single-file PyInstaller builds unpack to `%TEMP%` at launch. Run the EXE from a folder only you can write to, such as `%LOCALAPPDATA%\Programs\Win11NetSpeedCompact`.
