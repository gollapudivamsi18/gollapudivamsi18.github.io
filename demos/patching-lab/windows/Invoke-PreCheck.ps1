<#
.SYNOPSIS
    Pre-patch checks for Windows Server lab machines. Independent portfolio demo.
.DESCRIPTION
    Captures a JSON snapshot (OS build, free space, automatic services that are
    running, pending reboot, last hotfix) that Invoke-PostCheck.ps1 compares against.
.EXAMPLE
    .\Invoke-PreCheck.ps1 -OutputPath C:\PatchLab
#>
[CmdletBinding()]
param(
    [string]$OutputPath = 'C:\PatchLab',
    [int]$MinFreeGB = 10
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

function Test-PendingReboot {
    $keys = @(
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending',
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired'
    )
    foreach ($k in $keys) { if (Test-Path $k) { return $true } }
    return $false
}

$os = Get-CimInstance -ClassName Win32_OperatingSystem
$disk = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DeviceID='C:'"
$freeGB = [math]::Round($disk.FreeSpace / 1GB, 1)
$autoRunning = Get-CimInstance -ClassName Win32_Service -Filter "StartMode='Auto' AND State='Running'" |
    Select-Object -ExpandProperty Name
$lastHotfix = Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1

$snapshot = [ordered]@{
    Host              = $env:COMPUTERNAME
    TakenAt           = (Get-Date).ToUniversalTime().ToString('s') + 'Z'
    OS                = $os.Caption
    Build             = $os.BuildNumber
    FreeGB_C          = $freeGB
    PendingReboot     = Test-PendingReboot
    AutoRunning       = @($autoRunning)
    LastHotfix        = $lastHotfix.HotFixID
    LastHotfixDate    = if ($lastHotfix.InstalledOn) { $lastHotfix.InstalledOn.ToString('yyyy-MM-dd') } else { $null }
}

$file = Join-Path $OutputPath "pre-$($env:COMPUTERNAME).json"
$snapshot | ConvertTo-Json -Depth 3 | Set-Content -Path $file -Encoding UTF8
Write-Output "Snapshot written to $file"

$failed = $false
if ($freeGB -lt $MinFreeGB) { Write-Warning "Only $freeGB GB free on C: (minimum $MinFreeGB GB)"; $failed = $true }
if ($snapshot.PendingReboot) { Write-Warning 'A reboot is already pending. Reboot before patching.'; $failed = $true }

if ($failed) { exit 1 } else { Write-Output 'Pre-checks passed.' }
