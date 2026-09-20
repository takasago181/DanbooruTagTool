[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $ADirectory,
    [Parameter(Mandatory = $true)] [string] $BDirectory,
    [Parameter(Mandatory = $true)] [string] $OutputCsv
)

$ErrorActionPreference = 'Stop'

function Get-Number([object] $Value) {
    if ($null -eq $Value -or [string]::IsNullOrWhiteSpace([string]$Value)) { return $null }
    return [double]$Value
}

function Get-P95([double[]] $Values) {
    $sorted = @($Values | Sort-Object)
    if ($sorted.Count -eq 0) { return $null }
    $index = [math]::Min($sorted.Count - 1, [math]::Max(0, [int][math]::Ceiling($sorted.Count * .95) - 1))
    return $sorted[$index]
}

function Summarize([string] $Label, [string] $Directory) {
    $files = @(Get-ChildItem -LiteralPath $Directory -Filter '*-process.csv' | Sort-Object Name)
    foreach ($file in $files) {
        $rows = @(Import-Csv -LiteralPath $file.FullName)
        if ($rows.Count -eq 0) { continue }
        $cpu = @($rows | ForEach-Object { Get-Number $_.CpuPct } | Where-Object { $null -ne $_ })
        $private = @($rows | ForEach-Object { Get-Number $_.PrivateMemoryMB } | Where-Object { $null -ne $_ })
        $working = @($rows | ForEach-Object { Get-Number $_.WorkingSetMB } | Where-Object { $null -ne $_ })
        $threads = @($rows | ForEach-Object { [int]$_.ThreadCount })
        $handles = @($rows | ForEach-Object { [int]$_.HandleCount })
        $read = @($rows | ForEach-Object { Get-Number $_.DiskReadBytesPerSec } | Where-Object { $null -ne $_ })
        $write = @($rows | ForEach-Object { Get-Number $_.DiskWriteBytesPerSec } | Where-Object { $null -ne $_ })
        $cpuAvg = if ($cpu.Count) { ($cpu | Measure-Object -Average).Average } else { $null }
        [pscustomobject]@{
            Runtime = $Label
            Scenario = $rows[0].Scenario
            Samples = $rows.Count
            CpuAvgPct = if ($null -eq $cpuAvg) { $null } else { [math]::Round($cpuAvg, 4) }
            CpuP95Pct = if ($cpu.Count) { [math]::Round((Get-P95 $cpu), 4) } else { $null }
            CpuPeakPct = if ($cpu.Count) { [math]::Round(($cpu | Measure-Object -Maximum).Maximum, 4) } else { $null }
            PrivateFirstMB = [math]::Round($private[0], 3)
            PrivateLastMB = [math]::Round($private[-1], 3)
            PrivatePeakMB = [math]::Round(($private | Measure-Object -Maximum).Maximum, 3)
            WorkingFirstMB = [math]::Round($working[0], 3)
            WorkingLastMB = [math]::Round($working[-1], 3)
            ThreadsFirst = $threads[0]
            ThreadsLast = $threads[-1]
            ThreadsMin = ($threads | Measure-Object -Minimum).Minimum
            ThreadsMax = ($threads | Measure-Object -Maximum).Maximum
            HandlesFirst = $handles[0]
            HandlesLast = $handles[-1]
            HandlesMin = ($handles | Measure-Object -Minimum).Minimum
            HandlesMax = ($handles | Measure-Object -Maximum).Maximum
            DiskReadPeakBytesPerSec = if ($read.Count) { [math]::Round(($read | Measure-Object -Maximum).Maximum, 0) } else { 0 }
            DiskWritePeakBytesPerSec = if ($write.Count) { [math]::Round(($write | Measure-Object -Maximum).Maximum, 0) } else { 0 }
        }
    }
}

$parent = Split-Path -Parent ([IO.Path]::GetFullPath($OutputCsv))
New-Item -ItemType Directory -Path $parent -Force | Out-Null
@(Summarize 'A-SoftwareOnly' $ADirectory; Summarize 'B-AutoRender' $BDirectory) |
    Export-Csv -LiteralPath $OutputCsv -NoTypeInformation -Encoding utf8
