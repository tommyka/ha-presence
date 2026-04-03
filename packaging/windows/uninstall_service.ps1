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

Write-Host "Done. The install directory was left in place remove it manually if needed."
