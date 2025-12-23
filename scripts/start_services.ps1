Param(
    [string[]]$Services = @("card-data-chroma-001"),
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ComposeArgs
)

$root = Resolve-Path (Join-Path (Split-Path -Parent $PSCommandPath) "..")
$composeFile = Join-Path $root "docker/docker-compose.yml"

if (-Not (Test-Path $composeFile)) {
    Write-Error "Compose file not found at $composeFile."
    exit 1
}

foreach ($serviceName in $Services) {
    docker compose -f $composeFile up -d $serviceName @ComposeArgs
}
