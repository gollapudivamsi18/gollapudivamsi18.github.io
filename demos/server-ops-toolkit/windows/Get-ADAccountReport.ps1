<#
.SYNOPSIS
    Active Directory hygiene report. Independent portfolio demo. Read-only.
.DESCRIPTION
    Lists enabled accounts inactive for -Days, locked-out accounts, and accounts
    with "password never expires". Requires the ActiveDirectory module (RSAT).
    It never disables or modifies accounts; act on the report through your
    normal change process.
.EXAMPLE
    .\Get-ADAccountReport.ps1 -SearchBase 'OU=Staff,DC=corp,DC=example' -Days 90
#>
[CmdletBinding()]
param(
    [string]$SearchBase,
    [int]$Days = 90,
    [string]$OutputFolder = '.'
)

$ErrorActionPreference = 'Stop'
Import-Module ActiveDirectory
Import-Module (Join-Path $PSScriptRoot 'ServerOps.psm1') -Force

$params = @{ Filter = '*'; Properties = 'LastLogonDate', 'PasswordNeverExpires', 'LockedOut' }
if ($SearchBase) { $params.SearchBase = $SearchBase }
$users = Get-ADUser @params

$stale = Get-StaleAccount -Account $users -Days $Days
$locked = $users | Where-Object LockedOut | Select-Object SamAccountName
$neverExpires = $users | Where-Object { $_.Enabled -and $_.PasswordNeverExpires } | Select-Object SamAccountName

$stamp = Get-Date -Format 'yyyyMMdd'
$stale | Export-Csv (Join-Path $OutputFolder "ad-stale-$stamp.csv") -NoTypeInformation
$locked | Export-Csv (Join-Path $OutputFolder "ad-locked-$stamp.csv") -NoTypeInformation
$neverExpires | Export-Csv (Join-Path $OutputFolder "ad-pwd-never-expires-$stamp.csv") -NoTypeInformation

[pscustomobject]@{
    UsersScanned         = @($users).Count
    InactiveOver         = "$Days days"
    Stale                = @($stale).Count
    LockedOut            = @($locked).Count
    PasswordNeverExpires = @($neverExpires).Count
    ReportFolder         = (Resolve-Path $OutputFolder).Path
}
