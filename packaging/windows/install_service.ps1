param(
    [string]$ServiceName = "HAPresenceService",
    [string]$PythonExe = "python",
    [string]$WorkingDir = "C:\\ha-presence"
)

$binaryPath = "$PythonExe -m ha_presence.main run"

if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
    Write-Host "Service $ServiceName already exists"
    exit 0
}

New-Service -Name $ServiceName -BinaryPathName $binaryPath -DisplayName "HA Presence Service" -StartupType Automatic
Set-Location $WorkingDir
Start-Service -Name $ServiceName
Write-Host "Service installed and started"
