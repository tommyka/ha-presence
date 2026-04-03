param(
    [string]$WorkingDir = $PSScriptRoot ? (Split-Path $PSScriptRoot -Parent) : (Get-Location).Path
)

$exe = "$WorkingDir\.venv\Scripts\ha-presence.exe"

if (-not (Test-Path $exe)) {
    Write-Error "ha-presence not found at $exe."
    exit 1
}

Write-Host "Stopping and removing Windows service..."
Stop-Service -Name "HAPresenceService" -ErrorAction SilentlyContinue
& $exe uninstall-service

if ($LASTEXITCODE -ne 0) {
    Write-Error "Service removal failed."
    exit $LASTEXITCODE
}

Write-Host "Done. The install directory was left in place — remove it manually if needed."
