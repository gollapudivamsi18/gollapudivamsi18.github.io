<#
.SYNOPSIS
    Read-only health report for Windows Server. Independent portfolio demo.
.DESCRIPTION
    Checks CPU, memory, fixed-disk usage, automatic services that are stopped, and
    error/critical System events from the last N hours. Makes no changes.
    Exit code: 0 OK, 1 WARNING, 2 CRITICAL.
.EXAMPLE
    .\Get-ServerHealth.ps1
.EXAMPLE
    .\Get-ServerHealth.ps1 -ComputerName SRV01,SRV02 -AsJson | Out-File health.json
#>
[CmdletBinding()]
param(
    [string[]]$ComputerName = $env:COMPUTERNAME,
    [int]$DiskWarning = 80,
    [int]$DiskCritical = 90,
    [int]$MemoryWarning = 90,
    [int]$EventHours = 24,
    [string[]]$IgnoreService = @('gupdate', 'sppsvc', 'RemoteRegistry', 'MapsBroker'),
    [switch]$AsJson
)

$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'ServerOps.psm1') -Force

$results = foreach ($computer in $ComputerName) {
    $checks = [System.Collections.Generic.List[object]]::new()
    try {
        $session = New-CimSession -ComputerName $computer

        $cpu = (Get-CimInstance -CimSession $session Win32_Processor |
            Measure-Object -Property LoadPercentage -Average).Average
        $checks.Add([pscustomobject]@{ Check = 'CPU'; State = (Get-ThresholdState -Value $cpu -Warning 85 -Critical 95); Detail = "$cpu% load" })

        $os = Get-CimInstance -CimSession $session Win32_OperatingSystem
        $memPct = [math]::Round(100 * (1 - $os.FreePhysicalMemory / $os.TotalVisibleMemorySize), 1)
        $checks.Add([pscustomobject]@{ Check = 'Memory'; State = (Get-ThresholdState -Value $memPct -Warning $MemoryWarning -Critical 98); Detail = "$memPct% used" })

        Get-CimInstance -CimSession $session Win32_LogicalDisk -Filter 'DriveType=3' | ForEach-Object {
            $used = [math]::Round(100 * (1 - $_.FreeSpace / $_.Size), 1)
            $checks.Add([pscustomobject]@{
                    Check  = "Disk $($_.DeviceID)"
                    State  = (Get-ThresholdState -Value $used -Warning $DiskWarning -Critical $DiskCritical)
                    Detail = "$used% used, $([math]::Round($_.FreeSpace / 1GB, 1)) GB free"
                })
        }

        $stopped = Get-CimInstance -CimSession $session Win32_Service -Filter "StartMode='Auto' AND State<>'Running'" |
            Where-Object { $_.Name -notin $IgnoreService }
        $checks.Add([pscustomobject]@{
                Check  = 'Auto services'
                State  = if ($stopped) { 'WARNING' } else { 'OK' }
                Detail = if ($stopped) { 'Stopped: ' + ($stopped.Name -join ', ') } else { 'all running' }
            })

        $events = @(Get-WinEvent -ComputerName $computer -FilterHashtable @{
                LogName = 'System'; Level = 1, 2; StartTime = (Get-Date).AddHours(-$EventHours)
            } -ErrorAction SilentlyContinue)
        $checks.Add([pscustomobject]@{
                Check  = 'System events'
                State  = if ($events.Count -gt 20) { 'WARNING' } else { 'OK' }
                Detail = "$($events.Count) error/critical in last $EventHours h" + $(if ($events) { '; top source: ' + ($events | Group-Object ProviderName | Sort-Object Count -Descending | Select-Object -First 1).Name } else { '' })
            })
        Remove-CimSession $session
    }
    catch {
        $checks.Add([pscustomobject]@{ Check = 'Connection'; State = 'CRITICAL'; Detail = $_.Exception.Message })
    }

    [pscustomobject]@{
        ComputerName = $computer
        State        = Get-OverallState -State $checks.State
        Checks       = $checks
        CheckedAt    = (Get-Date).ToString('u')
    }
}

if ($AsJson) { $results | ConvertTo-Json -Depth 4 }
else {
    foreach ($r in $results) {
        Write-Output "$($r.ComputerName): $($r.State)"
        $r.Checks | Format-Table Check, State, Detail -AutoSize | Out-String | Write-Output
    }
}

$worst = Get-OverallState -State $results.State
exit @{ OK = 0; WARNING = 1; CRITICAL = 2 }[$worst]
