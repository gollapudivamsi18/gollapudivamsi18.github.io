<#
.SYNOPSIS
    Shared helpers for the Windows Server ops scripts. Independent portfolio demo.
.DESCRIPTION
    Pure functions (no system calls) so they can be unit-tested with Pester on any
    platform, including the Linux CI runner.
#>

function Get-ThresholdState {
    <#
    .SYNOPSIS  Map a percentage to OK / WARNING / CRITICAL.
    .EXAMPLE   Get-ThresholdState -Value 91 -Warning 80 -Critical 90   # CRITICAL
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param(
        [Parameter(Mandatory)][ValidateRange(0, 100)][double]$Value,
        [ValidateRange(0, 100)][double]$Warning = 80,
        [ValidateRange(0, 100)][double]$Critical = 90
    )
    if ($Warning -gt $Critical) { throw 'Warning threshold must not be above Critical.' }
    if ($Value -ge $Critical) { return 'CRITICAL' }
    if ($Value -ge $Warning) { return 'WARNING' }
    return 'OK'
}

function Get-OverallState {
    <#
    .SYNOPSIS  Worst state across a set of check results.
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param([Parameter(Mandatory)][AllowEmptyCollection()][string[]]$State)
    if ($State -contains 'CRITICAL') { return 'CRITICAL' }
    if ($State -contains 'WARNING') { return 'WARNING' }
    return 'OK'
}

function Get-StaleAccount {
    <#
    .SYNOPSIS  Filter account objects whose last logon is older than N days.
    .DESCRIPTION
        Accepts any objects with SamAccountName, Enabled and LastLogonDate
        properties (for example from Get-ADUser), so it can be tested with fakes.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][AllowEmptyCollection()][object[]]$Account,
        [int]$Days = 90,
        [datetime]$Now = (Get-Date)
    )
    $cutoff = $Now.AddDays(-$Days)
    $Account | Where-Object {
        $_.Enabled -and ((-not $_.LastLogonDate) -or ($_.LastLogonDate -lt $cutoff))
    } | ForEach-Object {
        [pscustomobject]@{
            SamAccountName = $_.SamAccountName
            LastLogonDate  = $_.LastLogonDate
            DaysInactive   = if ($_.LastLogonDate) { [int]($Now - $_.LastLogonDate).TotalDays } else { $null }
        }
    }
}

function Write-OpsLog {
    <#
    .SYNOPSIS  Append a timestamped line to a log file (and verbose stream).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Message,
        [string]$Path = (Join-Path ([IO.Path]::GetTempPath()) 'server-ops.log'),
        [ValidateSet('INFO', 'WARN', 'ERROR')][string]$Level = 'INFO'
    )
    $line = '{0:u} [{1}] {2}' -f (Get-Date), $Level, $Message
    Add-Content -Path $Path -Value $line
    Write-Verbose $line
}

Export-ModuleMember -Function Get-ThresholdState, Get-OverallState, Get-StaleAccount, Write-OpsLog
