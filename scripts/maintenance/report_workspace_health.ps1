[CmdletBinding()]
param(
  [string]$RepositoryRoot = ''
)

# Read-only workspace inventory. This script never removes files or changes Git state.
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) {
  $RepositoryRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}
$root = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $RepositoryRoot).Path)
$sizes = [System.Collections.Generic.Dictionary[string, long]]::new([StringComparer]::OrdinalIgnoreCase)
$fileCounts = [System.Collections.Generic.Dictionary[string, long]]::new([StringComparer]::OrdinalIgnoreCase)
$dirCounts = [System.Collections.Generic.Dictionary[string, long]]::new([StringComparer]::OrdinalIgnoreCase)
$errors = [System.Collections.Generic.List[string]]::new()
$stack = [System.Collections.Generic.Stack[object]]::new()
$stack.Push([pscustomobject]@{ Path=$root; Visited=$false })

while ($stack.Count -gt 0) {
  $item = $stack.Pop()
  $path = [string]$item.Path
  if (-not $item.Visited) {
    if (-not $sizes.ContainsKey($path)) { $sizes[$path]=0; $fileCounts[$path]=0; $dirCounts[$path]=1 }
    $stack.Push([pscustomobject]@{ Path=$path; Visited=$true })
    try {
      foreach ($entry in Get-ChildItem -LiteralPath $path -Force -ErrorAction Stop) {
        if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
        if ($entry.PSIsContainer) {
          $stack.Push([pscustomobject]@{ Path=$entry.FullName; Visited=$false })
        } else {
          if (-not $sizes.ContainsKey($path)) { $sizes[$path]=0; $fileCounts[$path]=0; $dirCounts[$path]=1 }
          $sizes[$path] += [long]$entry.Length
          $fileCounts[$path] += 1
        }
      }
    } catch { $errors.Add("$path : $($_.Exception.Message)") }
  } else {
    if (-not $sizes.ContainsKey($path)) { $sizes[$path]=0; $fileCounts[$path]=0; $dirCounts[$path]=1 }
    $parent = Split-Path -Parent $path
    if ($parent -and $path -ne $root -and $sizes.ContainsKey($parent)) {
      $sizes[$parent] += $sizes[$path]
      $fileCounts[$parent] += $fileCounts[$path]
      $dirCounts[$parent] += $dirCounts[$path]
    }
  }
}

$categoryBytes = [ordered]@{ bin=0L; obj=0L; audit=0L; artifacts=0L; staging=0L; backups=0L }
foreach ($path in $sizes.Keys) {
  $leaf = Split-Path -Leaf $path
  switch -Regex ($leaf) {
    '^bin$' { $categoryBytes.bin += $sizes[$path]; break }
    '^obj$' { $categoryBytes.obj += $sizes[$path]; break }
    '^\.audit$' { $categoryBytes.audit += $sizes[$path]; break }
    '^artifacts$' { $categoryBytes.artifacts += $sizes[$path]; break }
  }
  if ($leaf -match '(?i)staging') { $categoryBytes.staging += $sizes[$path] }
  if ($leaf -match '(?i)backup') { $categoryBytes.backups += $sizes[$path] }
}

$gitPath = Join-Path $root '.git'
$gitBytes = if ($sizes.ContainsKey($gitPath)) { $sizes[$gitPath] } else { 0L }
$git = (Get-Command git -ErrorAction Stop).Source
$worktreeOutput = @(& $git -C $root worktree list --porcelain 2>&1)
if ($LASTEXITCODE -ne 0) { throw "git worktree list failed: $($worktreeOutput -join ' ')" }
$worktrees = [System.Collections.Generic.List[object]]::new()
$current = @{}
foreach ($line in $worktreeOutput) {
  if ([string]::IsNullOrWhiteSpace($line)) {
    if ($current.path) {
      $status = @(& $git -C $current.path status --porcelain --untracked-files=normal 2>$null)
      $current.clean = ($status.Count -eq 0)
      $current.status_entries = $status.Count
      $worktrees.Add([pscustomobject]$current)
    }
    $current = @{}
  } elseif ($line -match '^worktree (.+)$') { $current.path=$Matches[1] }
  elseif ($line -match '^HEAD (.+)$') { $current.head=$Matches[1] }
  elseif ($line -match '^branch refs/heads/(.+)$') { $current.branch=$Matches[1] }
  elseif ($line -eq 'detached') { $current.branch='(detached)' }
}
if ($current.path) {
  $status = @(& $git -C $current.path status --porcelain --untracked-files=normal 2>$null)
  $current.clean = ($status.Count -eq 0); $current.status_entries=$status.Count
  $worktrees.Add([pscustomobject]$current)
}

$largest = @($sizes.Keys | Where-Object { $_ -ne $root } | Sort-Object { $sizes[$_] } -Descending | Select-Object -First 15 | ForEach-Object {
  [pscustomobject]@{ path=$_; bytes=$sizes[$_]; files=$fileCounts[$_]; directories=$dirCounts[$_] }
})
$summary = [ordered]@{
  generated_utc=[DateTime]::UtcNow.ToString('o')
  root=$root
  total_bytes=$sizes[$root]
  file_count=$fileCounts[$root]
  directory_count=$dirCounts[$root]
  git_bytes=$gitBytes
  generated_category_bytes=$categoryBytes
  registered_worktree_count=$worktrees.Count
  largest_directories=$largest
  worktrees=@($worktrees)
  scan_errors=@($errors)
}
$summary | ConvertTo-Json -Depth 6
