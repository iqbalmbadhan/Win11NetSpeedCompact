@echo off
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v Win11NetSpeedCompact /f >nul 2>&1
rmdir /s /q "%APPDATA%\Win11NetSpeedCompact" 2>nul
echo Startup entry and settings removed. You can now delete this folder.
pause
