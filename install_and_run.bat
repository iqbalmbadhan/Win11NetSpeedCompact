@echo off
setlocal
cd /d "%~dp0"
rem Install hash-verified dependencies into a private virtual environment
rem instead of the global Python installation.
if not exist ".venv\Scripts\pythonw.exe" (
  py -3 -m venv .venv
  if errorlevel 1 goto :error
)
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check --require-hashes --no-deps -r requirements.txt
if errorlevel 1 goto :error
start "" ".venv\Scripts\pythonw.exe" src\widget.py
exit /b 0
:error
echo Setup failed.
pause
exit /b 1
