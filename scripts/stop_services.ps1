Param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ComposeArgs
)

$root = Resolve-Path (Join-Path (Split-Path -Parent $PSCommandPath) "..")
$composeFile = Join-Path $root "docker/docker-compose.yml"
$serviceName = "card-data-chroma-001"

if (-Not (Test-Path $composeFile)) {
    Write-Error "Compose file not found at $composeFile."
    exit 1
}

docker compose -f $composeFile stop $serviceName @ComposeArgs
