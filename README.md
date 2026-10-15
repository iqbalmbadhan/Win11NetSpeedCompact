# Win11 Net Speed Compact v3.1

A clean compact Windows network-speed widget developed by [Iqbal Mahmud](https://iqbalmahmud.com).

## First launch

1. Extract the ZIP to a permanent folder.
2. Double-click `run_widget.bat`.
3. Start with Windows is enabled automatically on the first successful launch. It is a checked option in the right-click menu and can be disabled at any time.

The startup entry is created only for the current Windows user and does not require administrator access. If the source folder or compiled EXE is moved, launching it once refreshes the saved startup path.

## Controls

- Left-drag anywhere to move it.
- Right-click for units, adapter, font color/weight/size, background, startup and Exit.
- Ctrl + mouse wheel changes compact width and height.
- Reset position to taskbar returns it near the notification area.

## Privacy and safety

- Reads local cumulative adapter counters using `psutil`.
- Stores UI settings in `%APPDATA%\Win11NetSpeedCompact\settings.json`.
- Writes one current-user startup value under `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`.
- Makes no HTTP/API requests, sends no telemetry, collects no browsing history, and requests no administrator privileges.
- Opens the developer website only when the user selects that menu item.
- A named mutex prevents duplicate v3 instances.

## Avoid duplicate older builds

Exit older widget versions before starting v3.1. On launch, v3.1 removes the legacy `Win11NetSpeedWidgetPro` startup value created by earlier builds of this project. It does not modify unrelated startup entries.

## Build a standalone EXE

Run `scripts\build_exe.bat` on Windows. The output is `dist\Win11NetSpeedCompact.exe`. Share the EXE together with this README and LICENSE. Unsigned personal EXEs may trigger a Windows reputation warning; recipients should verify the SHA-256 checksum you publish with each release.
