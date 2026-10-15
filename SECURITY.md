# Security

## Data handling
The application reads local network byte counters and local UI preferences only. It has no telemetry or network client code.

## Permissions
The application runs as the signed-in user. It does not request elevation. Auto-start uses the current-user Run key.

## Reporting
Please report security issues privately to the maintainer through [Iqbal Mahmud's website](https://iqbalmahmud.com) before opening a public issue.

## Distribution
Publish SHA-256 checksums for release files. For wider distribution, code-sign the Windows executable with a trusted signing certificate.
