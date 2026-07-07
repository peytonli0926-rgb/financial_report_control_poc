param(
    [string]$PackageName = "ifrs18-windows-portable",
    [int]$Port = 8502
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Dist = Join-Path $Root "dist"
$PackageDir = Join-Path $Dist $PackageName
$AppDir = Join-Path $PackageDir "app"
$PythonDir = Join-Path $PackageDir "python"
$ZipPath = Join-Path $Dist "$PackageName.zip"
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $VenvPython)) {
    throw "Virtual environment Python was not found: $VenvPython"
}

$BasePrefix = & $VenvPython -c "import sys; print(sys.base_prefix)"
$VenvSitePackages = Join-Path $Root ".venv\Lib\site-packages"

if (-not (Test-Path -LiteralPath (Join-Path $BasePrefix "python.exe"))) {
    throw "Base Python runtime was not found: $BasePrefix"
}
if (-not (Test-Path -LiteralPath $VenvSitePackages)) {
    throw "Virtual environment site-packages was not found: $VenvSitePackages"
}

if (Test-Path -LiteralPath $PackageDir) {
    Remove-Item -LiteralPath $PackageDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $AppDir | Out-Null
New-Item -ItemType Directory -Force -Path $PythonDir | Out-Null

Write-Host "Copying Python runtime from: $BasePrefix"
$RuntimeItems = @(
    "DLLs",
    "Lib",
    "libs",
    "Scripts",
    "tcl",
    "python.exe",
    "pythonw.exe",
    "python3.dll",
    "python314.dll",
    "vcruntime140.dll",
    "vcruntime140_1.dll",
    "LICENSE.txt"
)
foreach ($Item in $RuntimeItems) {
    $Source = Join-Path $BasePrefix $Item
    if (Test-Path -LiteralPath $Source) {
        Copy-Item -LiteralPath $Source -Destination $PythonDir -Recurse -Force
    }
}

Write-Host "Copying Python dependencies from: $VenvSitePackages"
$TargetSitePackages = Join-Path $PythonDir "Lib\site-packages"
New-Item -ItemType Directory -Force -Path $TargetSitePackages | Out-Null
Copy-Item -Path (Join-Path $VenvSitePackages "*") -Destination $TargetSitePackages -Recurse -Force

Write-Host "Copying IFRS 18 application files"
$AppItems = @(
    ".streamlit",
    "assets",
    "config",
    "data",
    "docs",
    "engine",
    "input",
    "app.py",
    "app_recovered_full.cpython-314.pyc",
    "requirements.txt",
    "README.md"
)
foreach ($Item in $AppItems) {
    $Source = Join-Path $Root $Item
    if (Test-Path -LiteralPath $Source) {
        Copy-Item -LiteralPath $Source -Destination $AppDir -Recurse -Force
    }
}

$LogPatterns = @("*.log", "*.err.log", "*.out.log")
foreach ($Pattern in $LogPatterns) {
    Get-ChildItem -LiteralPath $AppDir -Recurse -Force -Filter $Pattern | Remove-Item -Force
}
Get-ChildItem -LiteralPath $AppDir -Recurse -Force -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

@"
@echo off
setlocal
set "ROOT=%~dp0"
set "PYTHON=%ROOT%python\python.exe"
set "APP_DIR=%ROOT%app"

if not exist "%PYTHON%" (
  echo Python runtime not found: %PYTHON%
  pause
  exit /b 1
)

cd /d "%APP_DIR%"
echo Starting IFRS 18 platform...
echo URL: http://127.0.0.1:$Port
"%PYTHON%" -m streamlit run app.py --server.address=127.0.0.1 --server.port=$Port --server.headless=true --browser.gatherUsageStats=false
pause
"@ | Set-Content -Path (Join-Path $PackageDir "start_ifrs18_windows.bat") -Encoding ASCII

@"
# IFRS 18 Windows Portable Package

## Start

Double-click:

```text
start_ifrs18_windows.bat
```

Then open:

```text
http://127.0.0.1:$Port
```

## Client machine requirements

- Windows 10/11 or Windows Server.
- Docker is not required.
- Python is not required.
- Streamlit and Python packages are not required.

## Directory layout

- `python/`: bundled Python 3.14 runtime and dependencies.
- `app/`: IFRS 18 application, configuration and data files.
- `start_ifrs18_windows.bat`: startup entry.

Keep `python/`, `app/` and `start_ifrs18_windows.bat` in the same directory.
"@ | Set-Content -Path (Join-Path $PackageDir "README_WINDOWS_PORTABLE.md") -Encoding ASCII

if (Test-Path -LiteralPath $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}

Write-Host "Compressing package: $ZipPath"
Compress-Archive -LiteralPath $PackageDir -DestinationPath $ZipPath -Force

Write-Host "Windows portable package created:"
Write-Host "  Directory: $PackageDir"
Write-Host "  Zip:       $ZipPath"
