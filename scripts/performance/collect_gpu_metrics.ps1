[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [Alias('ProcessId')] [int] $TargetProcessId,
    [Parameter(Mandatory = $true)] [string] $OutputCsv,
    [Parameter(Mandatory = $true)] [string] $RuntimeLabel,
    [Parameter(Mandatory = $true)] [string] $Scenario,
    [int] $Seconds = 60,
    [int] $IntervalSeconds = 5
)

$ErrorActionPreference = 'Continue'
$output = [IO.Path]::GetFullPath($OutputCsv)
New-Item -ItemType Directory -Path (Split-Path -Parent $output) -Force | Out-Null
$started = [DateTime]::UtcNow
$end = $started.AddSeconds($Seconds)

function Sum-GpuCounter([string] $CounterPath, [string] $Kind) {
    try {
        $samples = @(Get-Counter -Counter $CounterPath -ErrorAction Stop).CounterSamples
        # Counter paths are instance-qualified and vary slightly by Windows/NVIDIA
        # driver version.  Match the stable pid_<id>_ token instead of assuming
        # the exact separator after the PID.
        $pidToken = "pid_{0}_" -f $TargetProcessId
        $matching = @($samples | Where-Object { $_.Path -like "*${pidToken}*" })
        if ($matching.Count -eq 0) { return $null }
        $sum = ($matching | Measure-Object -Property CookedValue -Sum).Sum
        if ($Kind -eq 'MB') { return [math]::Round($sum / 1MB, 3) }
        return [math]::Round($sum, 3)
    } catch { return $null }
}

function Total-GpuSnapshot {
    try {
        $gpu = & nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits 2>$null
        $rows = @($gpu | ForEach-Object {
            $parts = $_ -split ','
            if ($parts.Count -ge 2) { [pscustomobject]@{ Util=[double]$parts[0].Trim(); Memory=[double]$parts[1].Trim() } }
        })
        if ($rows.Count -eq 0) { return $null }
        return [pscustomobject]@{ Util=(($rows | Measure-Object Util -Maximum).Maximum); Memory=(($rows | Measure-Object Memory -Sum).Sum) }
    } catch { return $null }
}

while ([DateTime]::UtcNow -lt $end) {
    $now = [DateTime]::UtcNow
    $total = Total-GpuSnapshot
    $row = [pscustomobject]@{
        Runtime = $RuntimeLabel; Scenario = $Scenario; TimestampUtc = $now.ToString('o'); ElapsedSec = [math]::Round(($now - $started).TotalSeconds, 3)
        ProcessGpuEngineUtilPct = Sum-GpuCounter '\GPU Engine(*)\Utilization Percentage' 'Pct'
        ProcessGpuDedicatedMB = Sum-GpuCounter '\GPU Process Memory(*)\Dedicated Usage' 'MB'
        ProcessGpuSharedMB = Sum-GpuCounter '\GPU Process Memory(*)\Shared Usage' 'MB'
        TotalGpuUtilPct = if ($null -eq $total) { $null } else { $total.Util }
        TotalGpuMemoryMB = if ($null -eq $total) { $null } else { $total.Memory }
    }
    if (-not (Test-Path -LiteralPath $output)) { $row | Export-Csv -LiteralPath $output -NoTypeInformation -Encoding utf8 }
    else { $row | Export-Csv -LiteralPath $output -NoTypeInformation -Append -Encoding utf8 }
    Start-Sleep -Seconds $IntervalSeconds
}
