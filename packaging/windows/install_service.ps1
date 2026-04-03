param(
    [string]$WorkingDir = ""
)

if (-not $WorkingDir) {
    $WorkingDir = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
}

$exe = "$WorkingDir\.venv\Scripts\ha-presence.exe"

if (-not (Test-Path $exe)) {
    Write-Error "ha-presence not found at $exe. Run 'uv sync' in $WorkingDir first."
    exit 1
}

Write-Host "Installing Windows service from $exe"
& $exe install-service

if ($LASTEXITCODE -ne 0) {
    Write-Error "Service installation failed."
    exit $LASTEXITCODE
}

Start-Service -Name "HAPresenceService"
Write-Host "Service installed and started."
Write-Host "To uninstall: $exe uninstall-service"
