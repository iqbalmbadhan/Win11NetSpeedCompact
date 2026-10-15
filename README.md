# Win11 Net Speed Compact

A small, always-on-top network speed meter for Windows 11. It sits on or near the taskbar and shows live download (↓) and upload (↑) speed, with no telemetry, no admin rights and no network requests.

Developed by [Iqbal Mahmud](https://iqbalmahmud.com) · Current version: **[1.0.0](https://github.com/iqbalmbadhan/Win11NetSpeedCompact/releases/tag/v1.0.0)** · [Changelog](CHANGELOG.md)

<p align="center">
  <img src="screenshots/widget-taskbar.png" alt="Widget docked on the Windows 11 taskbar showing download and upload speed" />
</p>

| Default dark theme | Custom theme |
| --- | --- |
| ![Default theme next to the notification area](screenshots/widget-default.png) | ![Light background with blue text](screenshots/widget-custom-theme.png) |

## Features

- Live download and upload speed, refreshed twice per second
- Auto-scaling units in bytes (B/s → GB/s) or bits (bps → Gbps), or fixed MB/s, Mbps, KB/s or Kbps
- Monitor all network interfaces combined, or a single adapter
- Custom font color, weight and size, plus a custom background color
- Drag to move it anywhere, and resize it with Ctrl + mouse wheel
- Stays above the taskbar and other windows
- System tray icon with **Bring to front** and **Exit**
- Optional **Start with Windows** for the current user only
- Remembers position, size and appearance between sessions
- Single-instance guard, so launching it twice does not open a second copy

## Requirements

- Windows 11
- Using the EXE: nothing else
- Running from source: Python 3.10+ (CI builds with 3.12) with the `py` launcher. The dependencies (`psutil`, `Pillow`, `pystray`) are installed automatically into a private virtual environment, pinned to exact versions and verified by SHA-256 hash.

## Installation

### Option A: Download the EXE (recommended)

1. Download `Win11NetSpeedCompact.exe` and `Win11NetSpeedCompact.exe.sha256.txt` from the [v1.0.0 release](https://github.com/iqbalmbadhan/Win11NetSpeedCompact/releases/tag/v1.0.0). A copy is also kept in the [`dist`](dist) folder of this repository.
2. [Verify the checksum](#verifying-downloads).
3. Move the EXE to a permanent folder, for example `%LOCALAPPDATA%\Programs\Win11NetSpeedCompact\`, and double-click it.

The EXE is not code-signed yet, so Windows SmartScreen may show "Windows protected your PC". If the checksum matches, choose **More info → Run anyway**.

### Option B: Run from source

1. Clone or download this repository and keep it in a permanent folder.
2. Double-click **`install_and_run.bat`**. It creates a `.venv` folder, installs the hash-verified dependencies into it and starts the widget. Your global Python installation is not modified.
3. After that, start it with **`run_widget.bat`**.

To do the same from a terminal:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install --require-hashes --no-deps -r requirements.txt
.venv\Scripts\pythonw.exe src\widget.py
```

## First launch

- The widget appears next to the notification area on the taskbar.
- **Start with Windows** is turned on automatically the first time it launches. You can turn it off from the right-click menu at any time.
- If you later move the folder or EXE, launch it once from the new location and the startup entry will point to the new path.

## Usage

| Action | How |
| --- | --- |
| Move the widget | Left-click and drag anywhere on it |
| Resize | Hold **Ctrl** and scroll the mouse wheel over the widget |
| Open settings | Right-click the widget |
| Bring it back on top | Click the tray icon, or right-click it and choose **Bring to front** from its menu |
| Quit | Right-click → **Exit**, or tray icon → **Exit** |

### Right-click menu

| Menu item | What it does |
| --- | --- |
| Speed unit | Auto bytes, Auto bits, MB/s, Mbps, KB/s or Kbps |
| Network interface | All interfaces, or one adapter that is currently up |
| Font color | Preset colors (white, black, blue, green, purple, orange) or Custom… |
| Font weight | Normal, Semi-bold or Bold |
| Font size | 8 to 12 pt |
| Background color… | Choose any background color |
| Reset position to taskbar | Moves the widget back next to the notification area |
| Start with Windows | Turns auto-start on or off for your user account |
| Open iqbalmahmud.com | Opens the developer's website in your browser |
| Exit | Closes the widget and removes the tray icon |

## Configuration

Settings are saved as JSON in:

```
%APPDATA%\Win11NetSpeedCompact\settings.json
```

Most settings change from the menu. A few advanced values can only be changed by editing the file while the widget is closed:

| Key | Default | Description |
| --- | --- | --- |
| `interval_ms` | `500` | How often the speed updates, in milliseconds (minimum 200) |
| `opacity` | `0.96` | Window opacity, from `0.0` to `1.0` |
| `topmost_refresh_ms` | `1500` | How often the widget re-asserts always-on-top (minimum 500) |
| `border` | `#334155` | Border color |
| `width` / `height` | `220` / `42` | Widget size in pixels (minimum 150 × 30) |

To reset everything to the defaults, delete `settings.json`.

## Privacy and security

- Reads only local network byte counters (via `psutil`) and its own settings file.
- Makes **no** HTTP or API requests, sends **no** telemetry and collects **no** browsing data.
- Runs as the signed-in user and never requests administrator privileges.
- Writes exactly one registry value, `Win11NetSpeedCompact`, under `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`, and only when Start with Windows is on.
- On launch, removes the `Win11NetSpeedWidgetPro` startup value left by earlier builds of this project. It does not touch any other startup entries.
- Opens a web page only when you choose **Open iqbalmahmud.com**.
- Treats its settings file as untrusted input. Invalid, tampered or oversized settings fall back to safe defaults instead of crashing the app.

The full list of hardening measures, and how to report a vulnerability privately, are in [SECURITY.md](SECURITY.md).

## Verifying downloads

Each EXE comes with a SHA-256 checksum file. Use the checksum from the same place you downloaded the EXE, because the release and the `dist` folder hold separate builds. In PowerShell, from the folder that contains the download:

```powershell
(Get-FileHash .\Win11NetSpeedCompact.exe -Algorithm SHA256).Hash.ToLower()
Get-Content .\Win11NetSpeedCompact.exe.sha256.txt
```

The two hashes must match exactly. If they do not, do not run the file.

There are two separate builds of v1.0.0, so each has its own checksum:

| Download location | SHA-256 |
| --- | --- |
| [v1.0.0 release](https://github.com/iqbalmbadhan/Win11NetSpeedCompact/releases/tag/v1.0.0) | `f9f48b44299ca6410203e5e8cc01c7326be98356ef57386559b9c0863b273673` |
| [`dist`](dist) folder | `17054436d64533e63f19dfa04b98395a41e453726bd488946cae4c05c60b7f36` |

The release build is produced by the GitHub Actions workflow; the `dist` copy was built and uploaded separately. Your hash only needs to match the one for the place you downloaded from.

EXEs built by the workflow from now on also carry a signed [build provenance attestation](https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations), which proves the file was built from this repository by GitHub Actions. With the [GitHub CLI](https://cli.github.com/) installed:

```powershell
gh attestation verify .\Win11NetSpeedCompact.exe --repo iqbalmbadhan/Win11NetSpeedCompact
```

## Upgrading from older versions

If you used an earlier build of this widget (such as "Net Speed Widget Pro"), exit it before starting this version, so that two widgets don't run at the same time. The old startup entry is cleaned up automatically.

## Uninstall

1. Right-click the widget and choose **Exit**.
2. Run [`scripts\uninstall.bat`](scripts/uninstall.bat). It removes the startup entry and the settings folder.
3. Delete the EXE or the project folder.

If you only have the EXE, you can do step 2 manually by turning off **Start with Windows** before exiting and then deleting `%APPDATA%\Win11NetSpeedCompact`.

## Building from source

Requires Windows and Python with the `py` launcher.

| Script | What it does |
| --- | --- |
| `scripts\build_release.bat` | Builds `dist\Win11NetSpeedCompact.exe` and its SHA-256 checksum |
| `scripts\build_exe.bat` | Same as `build_release.bat` (kept for compatibility) |
| `scripts\sign_release.ps1` | Signs the EXE with a PFX certificate, then verifies it and regenerates the checksum |

The build script creates an isolated `.venv-build` environment, installs the hash-locked dependencies from `requirements-build.txt`, runs the unit tests, and only then builds a single-file windowed EXE with PyInstaller.

### Running the tests

```powershell
py -m unittest discover -s tests -v
```

### Continuous integration

| Workflow | Runs on | What it does |
| --- | --- | --- |
| [CI](.github/workflows/ci.yml) | Every push to `main`, pull requests, weekly | Runs the tests and audits the locked dependencies for known vulnerabilities with `pip-audit` |
| [CodeQL](.github/workflows/codeql.yml) | Every push to `main`, pull requests, weekly | Static security analysis of the Python code and the workflow files |
| [Build and Release](.github/workflows/build.yml) | Manually | Audits, tests, builds, optionally signs and attests the EXE |

[Dependabot](.github/dependabot.yml) opens weekly pull requests to update Python packages and GitHub Actions.

### Building with GitHub Actions

Open the repository's **Actions** tab, choose **Build and Release Windows EXE** and click **Run workflow**. The EXE and checksum can then be downloaded from the run's artifacts.

Updating dependencies, code-signing setup and the repository secrets it needs are described in [DISTRIBUTION.md](DISTRIBUTION.md).

## Project structure

```
├── dist/                      # Prebuilt EXE + SHA-256 checksum
├── src/widget.py              # The whole application (Tkinter + psutil + pystray)
├── tests/test_widget.py       # Unit tests
├── install_and_run.bat        # Install dependencies and launch from source
├── run_widget.bat             # Launch from source
├── requirements.in            # Runtime dependencies (edit this)
├── requirements.txt           # Hash-locked runtime dependencies (generated)
├── requirements-build.in      # Build dependencies (edit this)
├── requirements-build.txt     # Hash-locked build dependencies (generated)
├── scripts/
│   ├── build_release.bat      # Test, then build the EXE + SHA-256 checksum
│   ├── build_exe.bat          # Alias for build_release.bat
│   ├── sign_release.ps1       # Authenticode-sign the EXE
│   └── uninstall.bat          # Remove the startup entry and settings
├── screenshots/
├── .github/
│   ├── workflows/             # CI, CodeQL, and Build and Release
│   └── dependabot.yml
├── CHANGELOG.md
├── DISTRIBUTION.md
└── SECURITY.md
```

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `run_widget.bat` says dependencies are not installed | Run `install_and_run.bat` once. |
| `'py' is not recognized` | Install Python from [python.org](https://www.python.org/downloads/windows/) with the **py launcher** option ticked. |
| The widget is off-screen or hidden | Right-click the tray icon → **Bring to front**, then right-click the widget → **Reset position to taskbar**. If it is still off-screen, delete `settings.json`. |
| Speed always shows 0 | Choose **Network interface → All interfaces**, or pick the adapter you actually use. |
| Launching again does nothing | Only one copy runs at a time. The widget is already running, so look for its tray icon. |
| It doesn't start with Windows | Make sure **Start with Windows** is ticked, then launch the widget once from its current location. |
| `install_and_run.bat` fails with a hash mismatch | A download was corrupted or tampered with. Delete the `.venv` folder and try again on a trusted network. |

## License

[MIT](LICENSE) © 2026 Iqbal Mahmud
