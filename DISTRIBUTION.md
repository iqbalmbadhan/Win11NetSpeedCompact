# Distribution guide

## Build a standalone EXE locally

On Windows 11, run `scripts\build_release.bat`. It:

1. Creates an isolated build environment in `.venv-build`.
2. Installs the hash-locked dependencies from `requirements-build.txt`.
3. Runs the unit tests.
4. Builds `dist\Win11NetSpeedCompact.exe` (without UPX) and writes its SHA-256 checksum.

## Build with GitHub Actions

Open the repository's **Actions** tab, choose **Build and Release Windows EXE** and click **Run workflow**. The workflow audits dependencies, runs the tests, builds the EXE, signs it if a certificate is configured, creates a build provenance attestation and uploads the EXE and checksum as a run artifact.

## Updating dependencies

Edit `requirements.in` (runtime) or `requirements-build.in` (build tools), then regenerate the locked files with [pip-tools](https://pip-tools.readthedocs.io/):

```powershell
pip-compile --generate-hashes --strip-extras requirements.in
pip-compile --generate-hashes --strip-extras --allow-unsafe requirements-build.in
```

Commit the `.in` and `.txt` files together. Dependabot also opens weekly update pull requests.

## Trusted code signing

A publicly trusted signature requires a code-signing certificate or a signing service. A self-signed certificate is intentionally not generated, because it is only suitable for development and testing and is not trusted on other people's computers.

With a PFX certificate and the Windows SDK installed, run:

```powershell
$pw = Read-Host "PFX password" -AsSecureString
.\scripts\sign_release.ps1 -PfxPath "C:\path\publisher-certificate.pfx" -PfxPassword $pw
```

The script imports the certificate only for the duration of signing, signs with SHA-256, adds an RFC 3161 timestamp, verifies the Authenticode signature, regenerates the checksum, and then removes the certificate and its private key from the store.

## GitHub Actions signing secrets

Add these repository secrets to have the workflow sign the EXE:

- `WINDOWS_SIGNING_PFX_BASE64`: Base64 content of the PFX certificate
- `WINDOWS_SIGNING_PFX_PASSWORD`: PFX password

If the secrets are absent, the workflow builds an unsigned EXE. If they are present, it signs and verifies the EXE before checksumming and attesting it.
