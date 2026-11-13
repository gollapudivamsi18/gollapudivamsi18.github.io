<#
.SYNOPSIS
    Patch status report across Windows servers. Independent portfolio demo. Read-only.
.DESCRIPTION
    For each server: last installed hotfix, days since last patch, and pending reboot.
    Flags servers whose last update is older than -MaxAgeDays.
.EXAMPLE
    .\Get-PatchReport.ps1 -ComputerName (Get-Content servers.txt) | Export-Csv patch-report.csv -NoTypeInformation
#>
[CmdletBinding()]
param(
    [string[]]$ComputerName = $env:COMPUTERNAME,
    [int]$MaxAgeDays = 35
)

foreach ($computer in $ComputerName) {
    try {
        $last = Get-HotFix -ComputerName $computer -ErrorAction Stop |
            Where-Object InstalledOn | Sort-Object InstalledOn -Descending | Select-Object -First 1
        $pending = Invoke-Command -ComputerName $computer -ErrorAction Stop -ScriptBlock {
            (Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending') -or
            (Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired')
        }
        $age = if ($last) { [int]((Get-Date) - $last.InstalledOn).TotalDays } else { $null }
        [pscustomobject]@{
            ComputerName  = $computer
            LastHotFix    = $last.HotFixID
            InstalledOn   = $last.InstalledOn
            DaysSince     = $age
            PendingReboot = $pending
            Compliant     = ($null -ne $age -and $age -le $MaxAgeDays -and -not $pending)
            Error         = $null
        }
    }
    catch {
        [pscustomobject]@{
            ComputerName = $computer; LastHotFix = $null; InstalledOn = $null; DaysSince = $null
            PendingReboot = $null; Compliant = $false; Error = $_.Exception.Message
        }
    }
}
