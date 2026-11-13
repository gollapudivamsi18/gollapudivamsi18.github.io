<#
.SYNOPSIS
    Restart automatic services that have stopped. Independent portfolio demo.
.DESCRIPTION
    This script CHANGES the system, so it is safe by default:
      - Supports -WhatIf; ConfirmImpact is High, so it asks before each restart
        unless you pass -Confirm:$false.
      - Only touches services listed in -AllowList (no wildcard restarts).
      - Logs every action through Write-OpsLog.
.EXAMPLE
    .\Restart-StoppedAutoService.ps1 -AllowList Spooler,W3SVC -WhatIf
.EXAMPLE
    .\Restart-StoppedAutoService.ps1 -AllowList W3SVC -Confirm:$false   # scheduled task
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)][string[]]$AllowList,
    [string]$LogPath = (Join-Path ([IO.Path]::GetTempPath()) 'service-recovery.log')
)

Import-Module (Join-Path $PSScriptRoot 'ServerOps.psm1') -Force

$candidates = Get-CimInstance Win32_Service -Filter "StartMode='Auto' AND State<>'Running'" |
    Where-Object { $_.Name -in $AllowList }

if (-not $candidates) {
    Write-OpsLog -Path $LogPath -Message 'No stopped allow-listed services.'
    return
}

foreach ($svc in $candidates) {
    if ($PSCmdlet.ShouldProcess($svc.Name, 'Start-Service')) {
        try {
            Start-Service -Name $svc.Name -ErrorAction Stop
            Write-OpsLog -Path $LogPath -Message "Started $($svc.Name)."
        }
        catch {
            Write-OpsLog -Path $LogPath -Level ERROR -Message "Failed to start $($svc.Name): $($_.Exception.Message)"
            Write-Error "Failed to start $($svc.Name): $($_.Exception.Message)"
        }
    }
}
