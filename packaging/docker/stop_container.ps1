param(
    [string]$ContainerName = "ifrs18-report-platform"
)

$ErrorActionPreference = "Stop"

$existing = docker ps -a --filter "name=^/${ContainerName}$" --format "{{.Names}}"
if ($existing -eq $ContainerName) {
    docker rm -f $ContainerName | Out-Null
    Write-Host "Stopped and removed container: $ContainerName"
} else {
    Write-Host "Container not found: $ContainerName"
}
