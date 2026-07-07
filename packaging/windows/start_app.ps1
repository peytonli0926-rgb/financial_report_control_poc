param(
    [int]$Port = 8502,
    [switch]$NoBrowser,
    [switch]$SkipInstall,
    [switch]$InstallOnly
)

$ErrorActionPreference = "Stop"

$AppRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
$VenvPython = Join-Path $AppRoot ".venv\Scripts\python.exe"
$AppFile = Join-Path $AppRoot "app.py"
$Requirements = Join-Path $AppRoot "requirements.txt"

if (-not (Test-Path -LiteralPath $AppFile)) {
    throw "app.py not found: $AppFile"
}

function Find-Python {
    if (Test-Path -LiteralPath $VenvPython) {
        return $VenvPython
    }

    $candidates = @("python", "py")
    foreach ($candidate in $candidates) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($command) {
            return $command.Source
        }
    }

    throw "Python not found. Install Python 3.14.x or create .venv under the package root."
}

$Python = Find-Python

if (-not (Test-Path -LiteralPath $VenvPython)) {
    Write-Host "Creating local virtual environment: $VenvPython"
    & $Python -m venv (Join-Path $AppRoot ".venv")
    $Python = $VenvPython
}

if (-not $SkipInstall) {
    Write-Host "Checking/installing dependencies..."
    & $Python -m pip install --upgrade pip
    & $Python -m pip install -r $Requirements
}

if ($InstallOnly) {
    Write-Host "Dependency installation completed."
    exit 0
}

$Url = "http://127.0.0.1:$Port"
Write-Host "Starting IFRS 18 Report Presentation Rule Switch Platform: $Url"

if (-not $NoBrowser) {
    Start-Job -ScriptBlock {
        param($TargetUrl)
        Start-Sleep -Seconds 3
        Start-Process $TargetUrl
    } -ArgumentList $Url | Out-Null
}

& $Python -m streamlit run $AppFile `
    --server.address 127.0.0.1 `
    --server.port $Port `
    --server.headless true `
    --browser.gatherUsageStats false
