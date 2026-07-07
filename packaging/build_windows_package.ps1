param(
    [string]$PackageName = "ifrs18_report_presentation_rule_switch_platform",
    [switch]$IncludeRuntimeData,
    [switch]$Zip
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$DistRoot = Join-Path $Root "dist"
$PackageRoot = Join-Path $DistRoot $PackageName

if (Test-Path -LiteralPath $PackageRoot) {
    Remove-Item -LiteralPath $PackageRoot -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $PackageRoot | Out-Null

$items = @(
    "app.py",
    "app_recovered_full.cpython-314.pyc",
    "requirements.txt",
    "README.md",
    "INSTALLATION_MANUAL.md",
    "DELIVERY_FILE_LIST.md",
    "assets",
    "config",
    "engine",
    "packaging\windows"
)

foreach ($item in $items) {
    $source = Join-Path $Root $item
    if (-not (Test-Path -LiteralPath $source)) {
        Write-Warning "跳过不存在的路径：$source"
        continue
    }
    $target = Join-Path $PackageRoot $item
    $targetParent = Split-Path -Parent $target
    New-Item -ItemType Directory -Force -Path $targetParent | Out-Null
    Copy-Item -LiteralPath $source -Destination $target -Recurse -Force
}

$dataRoot = Join-Path $PackageRoot "data"
New-Item -ItemType Directory -Force -Path (Join-Path $dataRoot "upload") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $dataRoot "output") | Out-Null

$deliveryInputPrefixes = @("1-1-", "1-2-", "1-3-", "1-4-", "1-5-")
foreach ($prefix in $deliveryInputPrefixes) {
    $matches = Get-ChildItem -LiteralPath (Join-Path $Root "data\upload") -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name.StartsWith($prefix) }
    foreach ($match in $matches) {
        Copy-Item -LiteralPath $match.FullName -Destination (Join-Path $dataRoot "upload") -Force
    }
}

$deliveryOutputFiles = @(
    "资产负债表生成版.xlsx",
    "利润表生成版.xlsx",
    "合并股东权益变动表生成版.xlsx"
)
foreach ($fileName in $deliveryOutputFiles) {
    $source = Join-Path $Root (Join-Path "data\output" $fileName)
    if (Test-Path -LiteralPath $source) {
        Copy-Item -LiteralPath $source -Destination (Join-Path $dataRoot "output") -Force
    } else {
        Write-Warning "Delivery output file not found: $source"
    }
}

$templateSource = Join-Path $Root "data\upload\report_templates"
if (Test-Path -LiteralPath $templateSource) {
    New-Item -ItemType Directory -Force -Path (Join-Path $dataRoot "upload") | Out-Null
    Copy-Item -LiteralPath $templateSource -Destination (Join-Path $dataRoot "upload\report_templates") -Recurse -Force
}

if ($IncludeRuntimeData) {
    $uploadSource = Join-Path $Root "data\upload"
    $outputSource = Join-Path $Root "data\output"
    if (Test-Path -LiteralPath $uploadSource) {
        Copy-Item -Path (Join-Path $uploadSource "*") -Destination (Join-Path $dataRoot "upload") -Recurse -Force
    }
    if (Test-Path -LiteralPath $outputSource) {
        Copy-Item -Path (Join-Path $outputSource "*") -Destination (Join-Path $dataRoot "output") -Recurse -Force
    }
}

$launcher = Join-Path $PackageRoot "start_ifrs18_platform.bat"
@"
@echo off
setlocal
cd /d "%~dp0"
set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%PS%" set "PS=powershell.exe"
"%PS%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0packaging\windows\start_app.ps1"
pause
"@ | Set-Content -Path $launcher -Encoding OEM
Copy-Item -LiteralPath (Join-Path $Root "packaging\windows\README_install_run.txt") -Destination (Join-Path $PackageRoot "README_install_run.txt") -Force

if ($Zip) {
    $zipPath = Join-Path $DistRoot "$PackageName.zip"
    if (Test-Path -LiteralPath $zipPath) {
        Remove-Item -LiteralPath $zipPath -Force
    }
    Compress-Archive -LiteralPath $PackageRoot -DestinationPath $zipPath -Force
    Write-Host "Package zip created: $zipPath"
} else {
    Write-Host "Package directory created: $PackageRoot"
}
