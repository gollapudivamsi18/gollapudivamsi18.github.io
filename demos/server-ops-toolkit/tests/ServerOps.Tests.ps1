# Pester 5 tests for the pure helpers in ServerOps.psm1.
#   Invoke-Pester demos/server-ops-toolkit/tests -Output Detailed
BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '..' 'windows' 'ServerOps.psm1') -Force
}

Describe 'Get-ThresholdState' {
    It 'returns <Expected> for <Value>%' -ForEach @(
        @{ Value = 10; Expected = 'OK' }
        @{ Value = 80; Expected = 'WARNING' }
        @{ Value = 89.9; Expected = 'WARNING' }
        @{ Value = 90; Expected = 'CRITICAL' }
        @{ Value = 100; Expected = 'CRITICAL' }
    ) {
        Get-ThresholdState -Value $Value -Warning 80 -Critical 90 | Should -Be $Expected
    }

    It 'rejects warning above critical' {
        { Get-ThresholdState -Value 50 -Warning 95 -Critical 90 } | Should -Throw
    }

    It 'rejects values outside 0-100' {
        { Get-ThresholdState -Value 120 } | Should -Throw
    }
}

Describe 'Get-OverallState' {
    It 'picks the worst state' {
        Get-OverallState -State 'OK', 'WARNING', 'OK' | Should -Be 'WARNING'
        Get-OverallState -State 'OK', 'CRITICAL', 'WARNING' | Should -Be 'CRITICAL'
        Get-OverallState -State 'OK' | Should -Be 'OK'
    }
}

Describe 'Get-StaleAccount' {
    BeforeAll {
        $now = [datetime]'2026-11-13'
        $accounts = @(
            [pscustomobject]@{ SamAccountName = 'active'; Enabled = $true; LastLogonDate = $now.AddDays(-5) }
            [pscustomobject]@{ SamAccountName = 'stale'; Enabled = $true; LastLogonDate = $now.AddDays(-120) }
            [pscustomobject]@{ SamAccountName = 'never'; Enabled = $true; LastLogonDate = $null }
            [pscustomobject]@{ SamAccountName = 'disabled'; Enabled = $false; LastLogonDate = $now.AddDays(-400) }
        )
    }

    It 'returns enabled accounts older than the cutoff or never used' {
        $r = Get-StaleAccount -Account $accounts -Days 90 -Now $now
        $r.SamAccountName | Should -Be @('stale', 'never')
        ($r | Where-Object SamAccountName -EQ 'stale').DaysInactive | Should -Be 120
    }

    It 'ignores disabled accounts' {
        (Get-StaleAccount -Account $accounts -Days 1 -Now $now).SamAccountName | Should -Not -Contain 'disabled'
    }
}

Describe 'Write-OpsLog' {
    It 'appends a timestamped line' {
        $log = Join-Path $TestDrive 'ops.log'
        Write-OpsLog -Path $log -Message 'hello' -Level WARN
        Get-Content $log | Should -Match '^\d{4}-\d{2}-\d{2} .*\[WARN\] hello$'
    }
}
