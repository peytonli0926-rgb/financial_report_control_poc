param(
    [string]$ImageName = "ifrs18-report-platform",
    [string]$Tag = "latest"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Image = "${ImageName}:${Tag}"

Write-Host "Building Docker image: $Image"
Write-Host "Project root: $Root"

docker version | Out-Null
docker build -t $Image $Root

Write-Host "Docker image built: $Image"
