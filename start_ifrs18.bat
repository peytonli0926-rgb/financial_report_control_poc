@echo off
setlocal

cd /d "%~dp0"
set "PYTHON=.venv\Scripts\python.exe"
set "PORT=8502"

if not exist "%PYTHON%" (
  echo IFRS 18 venv Python not found:
  echo %PYTHON%
  echo.
  echo Please check .venv or install dependencies first.
  pause
  exit /b 1
)

echo Starting IFRS 18 Report Presentation Rule Switch Platform
echo Project: "%CD%"
echo URL: http://127.0.0.1:%PORT%
echo.

"%PYTHON%" -m streamlit run app.py --server.port %PORT% --server.address 127.0.0.1
pause
