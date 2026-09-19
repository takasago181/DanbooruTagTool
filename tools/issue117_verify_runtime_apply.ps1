param(
    [Parameter(Mandatory = $true)]
    [string]$BaselineJson,
    [Parameter(Mandatory = $true)]
    [string]$StagedCatalog,
    [string]$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$RuntimeRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RuntimeRoot)) {
    $RuntimeRoot = Join-Path $RepositoryRoot "artifacts/current"
}

if (-not (Test-Path -LiteralPath $BaselineJson -PathType Leaf)) {
    throw "Missing baseline JSON: $BaselineJson"
}
if (-not (Test-Path -LiteralPath $StagedCatalog -PathType Leaf)) {
    throw "Missing staged catalog: $StagedCatalog"
}

$baseline = Get-Content -LiteralPath $BaselineJson -Raw -Encoding UTF8 | ConvertFrom-Json
$checks = New-Object System.Collections.Generic.List[object]

function Add-Check {
    param([string]$Name, [bool]$Pass, [object]$Actual, [object]$Expected, [string]$Detail = "")
    $checks.Add([pscustomobject]@{
        name = $Name
        pass = $Pass
        actual = $Actual
        expected = $Expected
        detail = $Detail
    })
}

function Get-Sha256 {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

$runtimeExe = Join-Path $RuntimeRoot "DanbooruTagTool.exe"
$currentCatalog = Join-Path $RuntimeRoot "Data/catalog.db"
$currentUserDb = Join-Path $RuntimeRoot "UserData/user.db"
$shortcutPath = Join-Path $RepositoryRoot "DanbooruTagTool.lnk"

$stagedCatalogHash = Get-Sha256 $StagedCatalog
$currentCatalogHash = Get-Sha256 $currentCatalog
$currentUserHash = Get-Sha256 $currentUserDb

$baselineUser = $baseline.userDb.runtime
$baselineUserHash = $baselineUser.sha256
$baselineUserExists = [bool]$baselineUser.exists

Add-Check -Name "runtime.exe.exists" -Pass (Test-Path -LiteralPath $runtimeExe -PathType Leaf) -Actual $runtimeExe -Expected "existing file"
Add-Check -Name "runtime.catalog.exists" -Pass ($null -ne $currentCatalogHash) -Actual $currentCatalog -Expected "existing file"
Add-Check -Name "runtime.catalog.matchesStaged" -Pass ($null -ne $currentCatalogHash -and $currentCatalogHash -eq $stagedCatalogHash) -Actual $currentCatalogHash -Expected $stagedCatalogHash

if ($baselineUserExists) {
    Add-Check -Name "runtime.userDb.exists" -Pass ($null -ne $currentUserHash) -Actual $currentUserDb -Expected "existing file"
    Add-Check -Name "runtime.userDb.hashUnchanged" -Pass ($null -ne $currentUserHash -and $currentUserHash -eq $baselineUserHash) -Actual $currentUserHash -Expected $baselineUserHash
}
else {
    Add-Check -Name "runtime.userDb.baselineAbsent" -Pass ($null -eq $currentUserHash) -Actual $currentUserHash -Expected $null -Detail "Baseline had no runtime UserData/user.db; unexpected creation must be reviewed before acceptance."
}

$shortcut = [ordered]@{
    exists = (Test-Path -LiteralPath $shortcutPath -PathType Leaf)
    targetPath = $null
    error = $null
}
if ($shortcut.exists) {
    try {
        $shell = New-Object -ComObject WScript.Shell
        $link = $shell.CreateShortcut($shortcutPath)
        $shortcut.targetPath = $link.TargetPath
    }
    catch {
        $shortcut.error = $_.Exception.Message
    }
}

$expectedTarget = [System.IO.Path]::GetFullPath($runtimeExe)
$actualTarget = if ([string]::IsNullOrWhiteSpace($shortcut.targetPath)) { "" } else { [System.IO.Path]::GetFullPath($shortcut.targetPath) }
Add-Check -Name "shortcut.exists" -Pass $shortcut.exists -Actual $shortcutPath -Expected "existing .lnk"
Add-Check -Name "shortcut.target" -Pass ($shortcut.exists -and $null -eq $shortcut.error -and $actualTarget -eq $expectedTarget) -Actual $actualTarget -Expected $expectedTarget -Detail $shortcut.error

$processes = @(
    Get-Process -Name "DanbooruTagTool" -ErrorAction SilentlyContinue |
        Select-Object Id, ProcessName, StartTime, Path
)

$failed = @($checks | Where-Object { -not $_.pass })

$result = [ordered]@{
    generatedAt = (Get-Date).ToString("o")
    mode = "POST_APPLY_INTEGRITY_VALIDATION"
    repositoryRoot = $RepositoryRoot
    runtimeRoot = $RuntimeRoot
    stagedCatalog = [ordered]@{
        path = $StagedCatalog
        sha256 = $stagedCatalogHash
    }
    current = [ordered]@{
        catalogSha256 = $currentCatalogHash
        userDbSha256 = $currentUserHash
        shortcut = $shortcut
        runningProcesses = $processes
    }
    baseline = [ordered]@{
        userDbExists = $baselineUserExists
        userDbSha256 = $baselineUserHash
    }
    passed = ($failed.Count -eq 0)
    checks = $checks
    failedChecks = $failed
}

$result | ConvertTo-Json -Depth 8

if ($failed.Count -gt 0) {
    exit 1
}
exit 0
