@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
  echo Dependencies are not installed yet. Run install_and_run.bat first.
  pause
  exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" src\widget.py
