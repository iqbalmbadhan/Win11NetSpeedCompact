# Changelog

## Unreleased
### Security
- Validates every value in `settings.json` (types, finite numbers, ranges, `#RRGGBB` colors, 64 KB size limit) so a corrupted or tampered file falls back to defaults instead of crashing
- Writes settings atomically to prevent corruption
- Uses explicit `ctypes` prototypes and `use_last_error` for Win32 calls
- Pins all dependencies to exact versions with SHA-256 hashes and installs them into isolated virtual environments
- Hardens GitHub Actions: SHA-pinned actions, least-privilege permissions, no persisted credentials, dependency audit and tests before every build, build provenance attestations
- Adds CI (tests + `pip-audit`), CodeQL scanning and Dependabot
- Signing script no longer exposes the PFX password on the command line, and the workflow now actually signs when signing secrets are configured
- Builds without UPX to reduce antivirus false positives
- `uninstall.bat` no longer risks deleting the wrong folder when `%APPDATA%` is unset

## 1.0.0
- Automatically enables current-user startup on first successful launch
- Adds a checked Start with Windows menu item
- Refreshes startup path after the app is moved and launched again
- Removes only the legacy startup value from earlier project builds
- Fixes duplicate topmost guard timers from the tray Bring to front action
- Adds startup failure handling instead of crashing
- Adds privacy, permissions, security and distribution documentation
