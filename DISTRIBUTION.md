# Distribution guide

## Build a standalone EXE

On Windows 11, run `scripts\build_release.bat`. It produces the EXE and its SHA-256 checksum under `dist`.

## Trusted code signing

A publicly trusted signature requires a code-signing certificate or a signing service. A self-signed certificate is intentionally not generated because it is suitable only for development/testing and is not trusted on friends’ computers.

With a PFX certificate, run:

```powershell
$pw = Read-Host "PFX password" -AsSecureString
.\scripts\sign_release.ps1 -PfxPath "C:\path\publisher-certificate.pfx" -PfxPassword $pw
```

The script signs with SHA-256, adds an RFC 3161 timestamp, verifies the Authenticode signature, and regenerates the checksum.

## GitHub Actions signing secrets

Add these repository secrets:

- `WINDOWS_SIGNING_PFX_BASE64`: Base64 content of the PFX certificate
- `WINDOWS_SIGNING_PFX_PASSWORD`: PFX password

If the secrets are absent, GitHub builds an unsigned EXE. If present, the workflow signs and verifies it before publishing.

## Release

```powershell
git tag v3.1.0
git push origin v3.1.0
```
