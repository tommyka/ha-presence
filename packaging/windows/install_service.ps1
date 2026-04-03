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

$python = "$WorkingDir\.venv\Scripts\python.exe"
$exe    = "$WorkingDir\.venv\Scripts\ha-presence.exe"

if (-not (Test-Path $exe)) {
    Write-Error "ha-presence not found at $exe. Run 'uv sync' in $WorkingDir first."
    exit 1
}

# pywin32 requires a post-install step to copy pythonservice.exe into place.
# Without this, service registration fails with "access denied".
$postInstall = "$WorkingDir\.venv\Scripts\pywin32_postinstall.py"
if (Test-Path $postInstall) {
    Write-Host "Running pywin32 post-install..."
    & $python $postInstall -install
    if ($LASTEXITCODE -ne 0) {
        Write-Error "pywin32 post-install failed."
        exit $LASTEXITCODE
    }
}

Write-Host "Installing Windows service..."
& $exe install-service

if ($LASTEXITCODE -ne 0) {
    Write-Error "Service installation failed."
    exit $LASTEXITCODE
}

Start-Service -Name "HAPresenceService"
Write-Host "Service installed and started."
Write-Host "To uninstall: run uninstall_service.ps1"
