IFRS 18 Report Presentation Rule Switch Platform - Windows local package

How to run:
1. Double-click start_ifrs18_platform.bat in the package root, or run packaging\windows\start_app.ps1.
2. On first run, the script creates .venv and installs dependencies from requirements.txt.
3. The browser opens http://127.0.0.1:8502 automatically.
4. If it does not open automatically, open the URL manually.

Prerequisites:
- Windows 10/11.
- Python 3.14.x available on PATH. This build loads app_recovered_full.cpython-314.pyc, so older Python versions may fail.
- First dependency installation needs access to a Python package index.

Data folders:
- Uploaded files: data/upload
- Generated reports: data/output
- Access control config: config/access_control.json

Stop service:
- Close the startup window, or press Ctrl+C in the window.
