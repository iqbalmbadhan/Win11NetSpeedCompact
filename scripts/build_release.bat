@echo off
setlocal
cd /d "%~dp0\.."
rem Build inside an isolated virtual environment from hash-locked dependencies,
rem so nothing unverified from PyPI or the global Python ends up in the EXE.
if not exist ".venv-build\Scripts\python.exe" (
  py -3 -m venv .venv-build
  if errorlevel 1 goto :error
)
set "PY=.venv-build\Scripts\python.exe"
"%PY%" -m pip install --disable-pip-version-check --require-hashes --no-deps -r requirements-build.txt
if errorlevel 1 goto :error
"%PY%" -m unittest discover -s tests
if errorlevel 1 goto :error
"%PY%" -m PyInstaller --noconfirm --clean --onefile --windowed --noupx --name Win11NetSpeedCompact src\widget.py
if errorlevel 1 goto :error
powershell -NoProfile -Command "$h=(Get-FileHash '.\dist\Win11NetSpeedCompact.exe' -Algorithm SHA256).Hash.ToLower(); Set-Content -Encoding ASCII '.\dist\Win11NetSpeedCompact.exe.sha256.txt' ($h+'  Win11NetSpeedCompact.exe')"
if errorlevel 1 goto :error
echo.
echo Release created:
echo   dist\Win11NetSpeedCompact.exe
echo   dist\Win11NetSpeedCompact.exe.sha256.txt
exit /b 0
:error
echo Build failed.
pause
exit /b 1
