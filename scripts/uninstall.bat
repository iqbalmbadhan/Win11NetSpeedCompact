@echo off
setlocal
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v Win11NetSpeedCompact /f >nul 2>&1
rem Guard against an unset APPDATA, which would otherwise point rmdir at the drive root.
if not defined APPDATA (
  echo APPDATA is not set, so the settings folder was left in place.
  goto :done
)
if exist "%APPDATA%\Win11NetSpeedCompact\" rmdir /s /q "%APPDATA%\Win11NetSpeedCompact"
echo Startup entry and settings removed. You can now delete this folder.
:done
pause
