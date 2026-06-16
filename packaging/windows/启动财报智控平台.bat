@echo off
setlocal
cd /d "%~dp0\..\.."
set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%PS%" set "PS=powershell.exe"
"%PS%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_app.ps1"
pause
