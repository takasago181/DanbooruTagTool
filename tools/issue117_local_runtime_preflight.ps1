param(
    [string]$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$RuntimeRoot = "",
    [string]$ProtectedSourceRoot = "",
    [string]$AuthorityRoot = "",
    [string]$OutputPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RuntimeRoot)) {
    $RuntimeRoot = Join-Path $RepositoryRoot "artifacts/current"
}
if ([string]::IsNullOrWhiteSpace($ProtectedSourceRoot)) {
    $ProtectedSourceRoot = $RepositoryRoot
}
if ([string]::IsNullOrWhiteSpace($AuthorityRoot)) {
    $AuthorityRoot = $RepositoryRoot
}

function Get-FileSnapshot {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [ordered]@{
            path = $Path
            exists = $false
            size = $null
            sha256 = $null
            error = $null
        }
    }

    $item = Get-Item -LiteralPath $Path
    $hash = $null
    $hashError = $null
    try {
        $hash = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    catch {
        $hashError = $_.Exception.Message
    }

    return [ordered]@{
        path = $item.FullName
        exists = $true
        size = $item.Length
        sha256 = $hash
        error = $hashError
    }
}

function Invoke-GitText {
    param([string[]]$Arguments)

    try {
        $output = & git -C $RepositoryRoot @Arguments 2>&1
        return [ordered]@{
            ok = ($LASTEXITCODE -eq 0)
            exitCode = $LASTEXITCODE
            text = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine)
        }
    }
    catch {
        return [ordered]@{
            ok = $false
            exitCode = $null
            text = $_.Exception.Message
        }
    }
}

$runtimeExists = Test-Path -LiteralPath $RuntimeRoot -PathType Container
$runtimeInventory = [ordered]@{
    path = $RuntimeRoot
    exists = $runtimeExists
    fileCount = 0
    totalBytes = 0
    topLevel = @()
}

if ($runtimeExists) {
    $allFiles = @(Get-ChildItem -LiteralPath $RuntimeRoot -File -Recurse -Force -ErrorAction SilentlyContinue)
    $runtimeInventory.fileCount = $allFiles.Count
    $runtimeInventory.totalBytes = ($allFiles | Measure-Object -Property Length -Sum).Sum
    if ($null -eq $runtimeInventory.totalBytes) { $runtimeInventory.totalBytes = 0 }
    $runtimeInventory.topLevel = @(
        Get-ChildItem -LiteralPath $RuntimeRoot -Force -ErrorAction SilentlyContinue |
            Sort-Object PSIsContainer, Name |
            Select-Object Name, PSIsContainer, Length, LastWriteTime
    )
}

$processes = @(
    Get-Process -Name "DanbooruTagTool" -ErrorAction SilentlyContinue |
        Select-Object Id, ProcessName, StartTime, Path
)

$shortcutPath = Join-Path $RepositoryRoot "DanbooruTagTool.lnk"
$shortcut = [ordered]@{
    path = $shortcutPath
    exists = (Test-Path -LiteralPath $shortcutPath -PathType Leaf)
    targetPath = $null
    arguments = $null
    workingDirectory = $null
    error = $null
}
if ($shortcut.exists) {
    try {
        $shell = New-Object -ComObject WScript.Shell
        $link = $shell.CreateShortcut($shortcutPath)
        $shortcut.targetPath = $link.TargetPath
        $shortcut.arguments = $link.Arguments
        $shortcut.workingDirectory = $link.WorkingDirectory
    }
    catch {
        $shortcut.error = $_.Exception.Message
    }
}

$protectedRelatives = @(
    "data/source/danbooru-2026-09-02.csv",
    "data/derived/danbooru_alias_normalized_index_VERIFIED_34417.csv",
    "data/special2788/illustrious_tag_knowledge_base_2788.csv",
    "data/derived/special2788_VERIFIED_LINKAGE.csv",
    "data/derived/ruleset2/01_SPECIAL2788_JAPANESE_COMPLETE_CANDIDATE.csv",
    "data/runtime/japanese_overlay.json"
)

$protectedInputs = @(
    foreach ($relative in $protectedRelatives) {
        $path = Join-Path $ProtectedSourceRoot $relative
        $item = Get-FileSnapshot -Path $path
        [ordered]@{
            relative = $relative
            path = $item.path
            exists = $item.exists
            size = $item.size
            sha256 = $item.sha256
            error = $item.error
        }
    }
)

$authorityChecks = @(
    "docs/issue118/production_candidate/sexual_intent_v1.csv",
    "data/generation/special2788_generation_profile.csv",
    "src/DanbooruTagTool.Data/UnifiedBrowseData/special_route_overrides_v1.csv"
)
$authorityInputs = @(
    foreach ($relative in $authorityChecks) {
        $path = Join-Path $AuthorityRoot $relative
        $item = Get-FileSnapshot -Path $path
        [ordered]@{
            relative = $relative
            path = $item.path
            exists = $item.exists
            size = $item.size
            sha256 = $item.sha256
            error = $item.error
        }
    }
)

$head = Invoke-GitText -Arguments @("rev-parse", "HEAD")
$branch = Invoke-GitText -Arguments @("branch", "--show-current")
$status = Invoke-GitText -Arguments @("status", "--short", "--branch")

$runtimeExe = Get-FileSnapshot -Path (Join-Path $RuntimeRoot "DanbooruTagTool.exe")
$catalogDb = Get-FileSnapshot -Path (Join-Path $RuntimeRoot "Data/catalog.db")
$runtimeUserDb = Get-FileSnapshot -Path (Join-Path $RuntimeRoot "UserData/user.db")
$repoUserDb = Get-FileSnapshot -Path (Join-Path $RepositoryRoot "UserData/user.db")

$report = [ordered]@{
    generatedAt = (Get-Date).ToString("o")
    mode = "READ_ONLY_PREFLIGHT"
    repository = [ordered]@{
        root = $RepositoryRoot
        head = $head
        branch = $branch
        status = $status
    }
    runningProcesses = $processes
    runtime = $runtimeInventory
    runtimeExe = $runtimeExe
    catalogDb = $catalogDb
    userDb = [ordered]@{
        runtime = $runtimeUserDb
        repositoryRootCandidate = $repoUserDb
    }
    shortcut = $shortcut
    protectedSourceRoot = $ProtectedSourceRoot
    protectedInputs = $protectedInputs
    authorityRoot = $AuthorityRoot
    authorityInputs = $authorityInputs
}

$json = $report | ConvertTo-Json -Depth 8
$json

if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
    $parent = Split-Path -Parent $OutputPath
    if (-not [string]::IsNullOrWhiteSpace($parent) -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    [System.IO.File]::WriteAllText($OutputPath, $json, [System.Text.UTF8Encoding]::new($false))
}
