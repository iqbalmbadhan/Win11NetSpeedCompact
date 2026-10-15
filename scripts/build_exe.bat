@echo off
rem Kept for compatibility: builds the EXE and its checksum the same way as a release.
call "%~dp0build_release.bat"
exit /b %errorlevel%
