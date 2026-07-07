param(
    [string]$ImageName = "ifrs18-report-platform",
    [string]$Tag = "latest",
    [string]$ContainerName = "ifrs18-report-platform",
    [int]$Port = 8502
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Image = "${ImageName}:${Tag}"
$Tar = Get-ChildItem -LiteralPath $ScriptDir -Filter "${ImageName}_*.tar" -File | Select-Object -First 1

docker version | Out-Null

if ($Tar) {
    Write-Host "Loading Docker image: $($Tar.FullName)"
    docker load -i $Tar.FullName | Out-Host
}

if (-not (docker image inspect $Image 2>$null)) {
    throw "Docker image not found after load: $Image"
}

$existing = docker ps -a --filter "name=^/${ContainerName}$" --format "{{.Names}}"
if ($existing -eq $ContainerName) {
    Write-Host "Removing existing container: $ContainerName"
    docker rm -f $ContainerName | Out-Null
}

Write-Host "Starting container: $ContainerName"
docker run -d `
    --name $ContainerName `
    -p "${Port}:8502" `
    -v "${ContainerName}-output:/app/data/output" `
    $Image | Out-Host

Write-Host "IFRS 18 platform is running:"
Write-Host "  http://127.0.0.1:$Port"
