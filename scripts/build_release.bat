@echo off
setlocal
cd /d "%~dp0\.."
py -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto :error
py -m PyInstaller --noconfirm --clean --onefile --windowed --name Win11NetSpeedCompact src\widget.py
if errorlevel 1 goto :error
powershell -NoProfile -Command "$h=(Get-FileHash '.\dist\Win11NetSpeedCompact.exe' -Algorithm SHA256).Hash.ToLower(); Set-Content -Encoding ASCII '.\dist\Win11NetSpeedCompact.exe.sha256.txt' ($h+'  Win11NetSpeedCompact.exe')"
echo.
echo Release created:
echo   dist\Win11NetSpeedCompact.exe
echo   dist\Win11NetSpeedCompact.exe.sha256.txt
exit /b 0
:error
echo Build failed.
pause
exit /b 1
