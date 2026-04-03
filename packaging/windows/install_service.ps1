param(
    [string]$WorkingDir = ""
)

if (-not $WorkingDir) {
    $WorkingDir = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
}

# Re-launch as Administrator if not already elevated
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Requesting Administrator privileges..."
    Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -WorkingDir `"$WorkingDir`""
    exit
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
Write-Host "To uninstall: run uninstall_service.ps1"
