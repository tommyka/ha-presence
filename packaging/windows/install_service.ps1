param(
    [string]$ServiceName = "HAPresenceService",
    [string]$UvExe = "uv",
    [string]$WorkingDir = "C:\\ha-presence"
)

$binaryPath = "$UvExe run --no-sync --directory `"$WorkingDir`" ha-presence run"

if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
    Write-Host "Service $ServiceName already exists"
    exit 0
}

New-Service -Name $ServiceName -BinaryPathName $binaryPath -DisplayName "HA Presence Service" -StartupType Automatic
Start-Service -Name $ServiceName
Write-Host "Service installed and started"
