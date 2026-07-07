param(
    [string]$ImageName = "ifrs18-report-platform",
    [string]$Tag = "latest",
    [string]$PackageName = "ifrs18-report-platform-docker"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Dist = Join-Path $Root "dist"
$PackageDir = Join-Path $Dist $PackageName
$Image = "${ImageName}:${Tag}"
$ImageTar = Join-Path $PackageDir "${ImageName}_${Tag}.tar"
$ZipPath = Join-Path $Dist "$PackageName.zip"

if (Test-Path -LiteralPath $PackageDir) {
    Remove-Item -LiteralPath $PackageDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $PackageDir | Out-Null

Write-Host "Ensuring Docker image exists: $Image"
docker image inspect $Image | Out-Null

Write-Host "Saving Docker image to: $ImageTar"
docker save -o $ImageTar $Image

Copy-Item -LiteralPath (Join-Path $PSScriptRoot "run_loaded_image.ps1") -Destination (Join-Path $PackageDir "run_loaded_image.ps1") -Force
Copy-Item -LiteralPath (Join-Path $PSScriptRoot "stop_container.ps1") -Destination (Join-Path $PackageDir "stop_container.ps1") -Force

$ReadmePath = Join-Path $PackageDir "README_CUSTOMER.md"
@"
# IFRS 18 Docker 客户安装说明

## 前置条件

- 客户机器已安装 Docker Desktop 或 Docker Engine。
- Docker 服务已启动。

## 启动

解压交付包后，双击：

```text
start_ifrs18_docker.bat
```

或在 PowerShell 中执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_loaded_image.ps1
```

启动后访问：

```text
http://127.0.0.1:8502
```

## 停止

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\stop_container.ps1
```

## 说明

- 交付包内包含 IFRS 18 平台 Docker 镜像，不依赖客户本机 Python 环境。
- 输出数据保存在 Docker volume：`ifrs18-report-platform-output`。
"@ | Set-Content -Path $ReadmePath -Encoding UTF8

@"
@echo off
setlocal
set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%PS%" set "PS=powershell.exe"
"%PS%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_loaded_image.ps1"
pause
"@ | Set-Content -Path (Join-Path $PackageDir "start_ifrs18_docker.bat") -Encoding ASCII

if (Test-Path -LiteralPath $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}
Compress-Archive -LiteralPath $PackageDir -DestinationPath $ZipPath -Force

Write-Host "Docker delivery package created:"
Write-Host "  Directory: $PackageDir"
Write-Host "  Zip:       $ZipPath"
