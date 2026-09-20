[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [int] $ProcessId,
    [Parameter(Mandatory = $true)] [string] $OutputCsv,
    [Parameter(Mandatory = $true)] [string] $RuntimeLabel,
    [Parameter(Mandatory = $true)] [string] $Scenario,
    [int] $Seconds = 60,
    [int] $IntervalMs = 1000
)

$ErrorActionPreference = 'Continue'
$output = [IO.Path]::GetFullPath($OutputCsv)
New-Item -ItemType Directory -Path (Split-Path -Parent $output) -Force | Out-Null

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class ProcessMetricNative {
    [StructLayout(LayoutKind.Sequential)]
    public struct IoCounters {
        public ulong ReadOperationCount; public ulong WriteOperationCount; public ulong OtherOperationCount;
        public ulong ReadTransferCount; public ulong WriteTransferCount; public ulong OtherTransferCount;
    }
    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool GetProcessIoCounters(IntPtr processHandle, out IoCounters counters);
    [DllImport("user32.dll")]
    public static extern uint GetGuiResources(IntPtr processHandle, uint flags);
}
'@

function Get-GpuMetric([int] $TargetProcessId, [string] $CounterName, [string] $valueKind) {
    try {
        $samples = @(Get-Counter -Counter $CounterName -ErrorAction Stop).CounterSamples
        $matching = @($samples | Where-Object { $_.Path -match "_pid_$TargetProcessId(?:_|\\)" })
        if ($matching.Count -eq 0) { return $null }
        if ($valueKind -eq 'bytes') { return (($matching | Measure-Object -Property CookedValue -Sum).Sum / 1MB) }
        return ($matching | Measure-Object -Property CookedValue -Sum).Sum
    } catch { return $null }
}

function Get-SystemCounter([string] $CounterName) {
    try { return (Get-Counter -Counter $CounterName -ErrorAction Stop).CounterSamples[0].CookedValue } catch { return $null }
}

$previousCpu = $null
$previousRead = $null
$previousWrite = $null
$previousTime = [DateTime]::UtcNow
$started = $previousTime

for ($i = 0; $i -le [math]::Ceiling(($Seconds * 1000) / $IntervalMs); $i++) {
    $now = [DateTime]::UtcNow
    $alive = $true
    $process = $null
    try { $process = Get-Process -Id $ProcessId -ErrorAction Stop; $process.Refresh() } catch { $alive = $false }
    $cpu = $read = $write = $working = $private = $threads = $handles = $gdi = $user = $null
    if ($alive) {
        try { $cpu = $process.TotalProcessorTime.TotalSeconds } catch {}
        try { $working = $process.WorkingSet64 / 1MB } catch {}
        try { $private = $process.PrivateMemorySize64 / 1MB } catch {}
        try { $threads = $process.Threads.Count } catch {}
        try { $handles = $process.HandleCount } catch {}
        try {
            $io = New-Object ProcessMetricNative+IoCounters
            if ([ProcessMetricNative]::GetProcessIoCounters($process.Handle, [ref]$io)) {
                $read = [double]$io.ReadTransferCount
                $write = [double]$io.WriteTransferCount
            }
            $gdi = [ProcessMetricNative]::GetGuiResources($process.Handle, 0)
            $user = [ProcessMetricNative]::GetGuiResources($process.Handle, 1)
        } catch {}
    }
    $elapsed = ($now - $started).TotalSeconds
    $wall = ($now - $previousTime).TotalSeconds
    $cpuPct = $null
    $readBps = $null
    $writeBps = $null
    if ($null -ne $cpu -and $null -ne $previousCpu -and $wall -gt 0) { $cpuPct = (($cpu - $previousCpu) / $wall / [Environment]::ProcessorCount) * 100 }
    if ($null -ne $read -and $null -ne $previousRead -and $wall -gt 0) { $readBps = ($read - $previousRead) / $wall }
    if ($null -ne $write -and $null -ne $previousWrite -and $wall -gt 0) { $writeBps = ($write - $previousWrite) / $wall }
    $row = [pscustomobject]@{
        Runtime = $RuntimeLabel; Scenario = $Scenario; TimestampUtc = $now.ToString('o'); ElapsedSec = [math]::Round($elapsed, 3)
        CpuPct = if ($null -eq $cpuPct) { $null } else { [math]::Round($cpuPct, 4) }
        WorkingSetMB = if ($null -eq $working) { $null } else { [math]::Round($working, 3) }
        PrivateMemoryMB = if ($null -eq $private) { $null } else { [math]::Round($private, 3) }
        ThreadCount = $threads; HandleCount = $handles
        DiskReadBytesPerSec = if ($null -eq $readBps) { $null } else { [math]::Round($readBps, 3) }
        DiskWriteBytesPerSec = if ($null -eq $writeBps) { $null } else { [math]::Round($writeBps, 3) }
        GpuEngineUtilPct = $null
        GpuDedicatedMB = $null
        GpuSharedMB = $null
        GdiObjects = $gdi; UserObjects = $user
        SystemCpuPct = $null
        SystemDiskReadBytesPerSec = $null
        SystemDiskWriteBytesPerSec = $null
        Alive = $alive
    }
    if (-not (Test-Path -LiteralPath $output)) { $row | Export-Csv -LiteralPath $output -NoTypeInformation -Encoding utf8 }
    else { $row | Export-Csv -LiteralPath $output -NoTypeInformation -Append -Encoding utf8 }
    if (-not $alive) { break }
    $previousCpu = $cpu; $previousRead = $read; $previousWrite = $write; $previousTime = $now
    Start-Sleep -Milliseconds $IntervalMs
}
