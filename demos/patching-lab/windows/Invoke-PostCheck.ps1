<#
.SYNOPSIS
    Post-patch checks for Windows Server lab machines. Independent portfolio demo.
.DESCRIPTION
    Compares the current state with the pre-check snapshot and appends a line to
    results.csv for the compliance report.
.EXAMPLE
    .\Invoke-PostCheck.ps1 -OutputPath C:\PatchLab
#>
[CmdletBinding()]
param(
    [string]$OutputPath = 'C:\PatchLab'
)

$ErrorActionPreference = 'Stop'
$preFile = Join-Path $OutputPath "pre-$($env:COMPUTERNAME).json"
if (-not (Test-Path $preFile)) { Write-Error "No pre-check snapshot at $preFile" }
$pre = Get-Content -Path $preFile -Raw | ConvertFrom-Json

$os = Get-CimInstance -ClassName Win32_OperatingSystem
$issues = New-Object System.Collections.Generic.List[string]

foreach ($svc in $pre.AutoRunning) {
    $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if (-not $s -or $s.Status -ne 'Running') { $issues.Add("Service not running: $svc") }
}

$since = [datetime]$pre.TakenAt
$critical = Get-WinEvent -FilterHashtable @{ LogName = 'System'; Level = 1; StartTime = $since } -ErrorAction SilentlyContinue
if ($critical) { $issues.Add("$(@($critical).Count) critical System events since pre-check") }

$lastHotfix = Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1
$result = if ($issues.Count -eq 0) { 'compliant' } else { 'needs-attention' }

$issues | ForEach-Object { Write-Warning $_ }
Write-Output "Build: $($pre.Build) -> $($os.BuildNumber); last hotfix: $($lastHotfix.HotFixID); result: $result"

$line = '{0},{1},{2},{3},{4},{5}' -f $env:COMPUTERNAME, (Get-Date -Format 'yyyy-MM-dd'), $os.Caption, $pre.Build, $os.BuildNumber, $result
Add-Content -Path (Join-Path $OutputPath 'results.csv') -Value $line

if ($issues.Count -gt 0) { exit 1 }
