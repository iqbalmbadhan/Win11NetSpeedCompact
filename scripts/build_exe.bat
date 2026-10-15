@echo off
cd /d "%~dp0\.."
py -m pip install -r requirements.txt pyinstaller
py -m PyInstaller --noconfirm --clean --onefile --windowed --name Win11NetSpeedCompact src\widget.py
echo Built dist\Win11NetSpeedCompact.exe
pause
