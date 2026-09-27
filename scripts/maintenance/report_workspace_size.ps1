[CmdletBinding()]
param(
    [string] $RepositoryRoot = '',
    [int] $LargestDirectoryCount = 20,
    [string] $ReportPath = ''
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) { $RepositoryRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot) }
$root = (Resolve-Path -LiteralPath $RepositoryRoot).Path.TrimEnd('\')
function Get-TreeStats([string] $Path) {
    $bytes = [long]0; $fileCount = 0; $dirCount = 0; $errors = [Collections.Generic.List[string]]::new()
    $pending = [Collections.Generic.Stack[string]]::new(); $pending.Push($Path)
    while ($pending.Count -gt 0) {
        $current = $pending.Pop()
        try {
            foreach ($entry in [IO.Directory]::EnumerateFileSystemEntries($current)) {
                try {
                    $attributes = [IO.File]::GetAttributes($entry)
                    if (($attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { continue }
                    if (($attributes -band [IO.FileAttributes]::Directory) -ne 0) { $dirCount++; $pending.Push($entry) }
                    else { $bytes += (Get-Item -LiteralPath $entry -Force).Length; $fileCount++ }
                } catch { $errors.Add($_.Exception.Message) }
            }
        } catch { $errors.Add($_.Exception.Message) }
    }
    [pscustomobject]@{ path=$Path; bytes=$bytes; files=$fileCount; directories=$dirCount; errors=$errors.Count }
}

$rootStats = Get-TreeStats $root
$topStats = @(Get-ChildItem -LiteralPath $root -Force | ForEach-Object { if ($_.PSIsContainer) { Get-TreeStats $_.FullName } else { [pscustomobject]@{path=$_.FullName;bytes=$_.Length;files=1;directories=0;errors=0} } } | Sort-Object bytes -Descending)
$focusNames = @('.git','bin','obj','.audit','artifacts')
$focus = foreach ($name in $focusNames) {
    $found = @(Get-ChildItem -LiteralPath $root -Directory -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq $name })
    foreach ($dir in $found) { Get-TreeStats $dir.FullName }
}
$worktreeLines = @(& git -C $root worktree list --porcelain)
if ($LASTEXITCODE -ne 0) { throw 'git worktree list failed.' }
$worktreePaths = @(); $current = $null
foreach ($line in $worktreeLines) {
    if ($line -match '^worktree (.+)$') { if ($current) { $worktreePaths += $current }; $current = [ordered]@{path=$Matches[1];head='';branch='';status='';ahead_origin_main=$null} }
    elseif ($current -and $line -match '^HEAD (.+)$') { $current.head=$Matches[1] }
    elseif ($current -and $line -match '^branch refs/heads/(.+)$') { $current.branch=$Matches[1] }
}
if ($current) { $worktreePaths += $current }
$worktrees = foreach ($wt in $worktreePaths) {
    if (Test-Path -LiteralPath $wt.path) {
        $head = (& git -C $wt.path rev-parse HEAD 2>$null).Trim()
        $status = @(& git -C $wt.path status --short --untracked-files=all 2>$null)
        $wt.head = $head; $wt.status = if ($status.Count) { "dirty:$($status.Count)" } else { 'clean' }
        if ($wt.branch) {
            $ahead = & git -C $wt.path rev-list --count 'origin/main..HEAD' 2>$null
            if ($LASTEXITCODE -eq 0) { $wt.ahead_origin_main = [int]$ahead }
        }
        [pscustomobject]$wt
    }
}
$report = [ordered]@{
    created_at_utc=(Get-Date).ToUniversalTime().ToString('o')
    repository_root=$root
    workspace=$rootStats
    top_level=$topStats
    focus_directories=@($focus)
    worktree_count=@($worktrees).Count
    worktrees=@($worktrees)
    largest_directories=@($focus | Sort-Object bytes -Descending | Select-Object -First $LargestDirectoryCount)
    policy='report-only; no files or worktrees are removed'
}
$json=$report | ConvertTo-Json -Depth 8
if ($ReportPath) { $json | Set-Content -LiteralPath $ReportPath -Encoding utf8 }
Write-Output $json
