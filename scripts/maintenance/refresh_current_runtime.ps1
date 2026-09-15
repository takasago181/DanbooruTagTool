[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $SourceRevision,
    [string] $RepositoryRoot = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)),
    [string] $ArtifactRoot = '',
    [switch] $SkipRestore
)

$ErrorActionPreference = 'Stop'
$RepositoryRoot = (Resolve-Path -LiteralPath $RepositoryRoot).Path
if ([string]::IsNullOrWhiteSpace($ArtifactRoot)) { $ArtifactRoot = Join-Path $RepositoryRoot 'artifacts/current' }
$ArtifactRoot = (Resolve-Path -LiteralPath $ArtifactRoot).Path
$catalogPath = Join-Path $ArtifactRoot 'Data/catalog.db'
$userDbPath = Join-Path $ArtifactRoot 'UserData/user.db'
$trackedStatus = & git -C $RepositoryRoot status --short --untracked-files=no
if ($LASTEXITCODE -ne 0) { throw 'Unable to read git status.' }
if ($trackedStatus) {
    & git -C $RepositoryRoot diff --ignore-space-at-eol --quiet --exit-code
    if ($LASTEXITCODE -ne 0) { throw 'Source checkout has semantic tracked changes; commit or stash them before runtime refresh.' }
}
$head = (& git -C $RepositoryRoot rev-parse --verify HEAD).Trim()
$resolvedRevision = (& git -C $RepositoryRoot rev-parse --verify "$SourceRevision^{commit}").Trim()
if ($LASTEXITCODE -ne 0 -or $resolvedRevision -ne $head) {
    throw "SourceRevision must resolve to the clean checkout HEAD. HEAD=$head SourceRevision=$SourceRevision Resolved=$resolvedRevision"
}
if (-not (Test-Path -LiteralPath $catalogPath) -or -not (Test-Path -LiteralPath $userDbPath)) { throw 'Protected production DBs are missing.' }

$catalogBefore = (Get-FileHash -LiteralPath $catalogPath -Algorithm SHA256).Hash
$userBefore = (Get-FileHash -LiteralPath $userDbPath -Algorithm SHA256).Hash
$stamp = [Guid]::NewGuid().ToString('N')
$tempRoot = Join-Path $env:TEMP "DanbooruTagTool-issue91-refresh-$stamp"
$publishRoot = Join-Path $tempRoot 'publish'
$validationRoot = Join-Path $tempRoot 'validation'
$buildRoot = Join-Path $tempRoot 'build-catalog'
$postBuildRoot = Join-Path $tempRoot 'post-build-catalog'
$dotnet = Join-Path $RepositoryRoot '.tools/dotnet/sdk/dotnet.exe'
if (-not (Test-Path -LiteralPath $dotnet)) { $dotnet = (Get-Command dotnet -ErrorAction SilentlyContinue).Source }
if ([string]::IsNullOrWhiteSpace($dotnet) -or -not (Test-Path -LiteralPath $dotnet)) { throw 'No .NET SDK was found.' }
$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if ([string]::IsNullOrWhiteSpace($python)) { throw 'Python is required for read-only SQLite semantic validation.' }

function Invoke-Checked([string] $FilePath, [string[]] $Arguments) {
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed ($LASTEXITCODE): $FilePath $($Arguments -join ' ')" }
}
function Relative([string] $Base, [string] $Path) { return $Path.Substring($Base.Length + 1).Replace('\', '/') }

try {
    New-Item -ItemType Directory -Path $publishRoot, "$validationRoot/Data", "$validationRoot/UserData", $buildRoot, $postBuildRoot -Force | Out-Null
    if (-not $SkipRestore) { Invoke-Checked $dotnet @('restore', (Join-Path $RepositoryRoot 'src/DanbooruTagTool.sln'), '--runtime', 'win-x64') }
    Invoke-Checked $dotnet @('publish', (Join-Path $RepositoryRoot 'src/DanbooruTagTool.App/DanbooruTagTool.App.csproj'), '-c', 'Release', '-r', 'win-x64', '--self-contained', 'true', '--no-restore', '-o', $publishRoot)
    $publishedExe = Join-Path $publishRoot 'DanbooruTagTool.exe'
    if (-not (Test-Path -LiteralPath $publishedExe)) { throw 'Publish did not produce DanbooruTagTool.exe.' }

    Copy-Item -LiteralPath $catalogPath -Destination "$validationRoot/Data/catalog.db"
    Copy-Item -LiteralPath $userDbPath -Destination "$validationRoot/UserData/user.db"
    Invoke-Checked $publishedExe @('--build-catalog', $RepositoryRoot, $RepositoryRoot, $buildRoot)
    Invoke-Checked $python @('-B', (Join-Path $RepositoryRoot 'scripts/maintenance/catalog_health.py'), '--catalog', (Join-Path $buildRoot 'catalog.db'), '--userdb', (Join-Path $validationRoot 'UserData/user.db'))
    $process = Start-Process -FilePath $publishedExe -WorkingDirectory $validationRoot -PassThru
    try {
        $title = ''
        for ($i = 0; $i -lt 30; $i++) { Start-Sleep -Milliseconds 500; $process.Refresh(); $title = $process.MainWindowTitle; if ($title) { break } }
        if ($title -ne 'DanbooruTagTool v1') { throw "WPF launch did not expose expected title (actual '$title')." }
    } finally {
        if (-not $process.HasExited) { [void]$process.CloseMainWindow(); if (-not $process.WaitForExit(5000)) { Stop-Process -Id $process.Id -Force } }
    }

    $newFiles = @{}
    Get-ChildItem -LiteralPath $publishRoot -File -Recurse | ForEach-Object { $newFiles[(Relative $publishRoot $_.FullName)] = $_.FullName }
    $oldFiles = @{}
    Get-ChildItem -LiteralPath $ArtifactRoot -File -Recurse | Where-Object { (Relative $ArtifactRoot $_.FullName) -notmatch '^(Data|UserData)/' } | ForEach-Object { $oldFiles[(Relative $ArtifactRoot $_.FullName)] = $_.FullName }
    foreach ($rel in @($oldFiles.Keys | Where-Object { -not $newFiles.ContainsKey($_) })) { Remove-Item -LiteralPath $oldFiles[$rel] -Force }
    foreach ($rel in $newFiles.Keys) {
        if ($rel -match '^(Data|UserData)/') { throw "Publish unexpectedly contains protected path: $rel" }
        $destination = Join-Path $ArtifactRoot ($rel.Replace('/', '\'))
        New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
        Copy-Item -LiteralPath $newFiles[$rel] -Destination $destination -Force
    }
    Get-ChildItem -LiteralPath $ArtifactRoot -Directory -Recurse | Sort-Object FullName -Descending | Where-Object { $_.FullName -notmatch '\(Data|UserData)(\\|$)' } | ForEach-Object { if (-not (Get-ChildItem -LiteralPath $_.FullName -Force)) { Remove-Item -LiteralPath $_.FullName -Force } }

    Invoke-Checked (Join-Path $ArtifactRoot 'DanbooruTagTool.exe') @('--build-catalog', $RepositoryRoot, $RepositoryRoot, $postBuildRoot)
    Invoke-Checked $python @('-B', (Join-Path $RepositoryRoot 'scripts/maintenance/catalog_health.py'), '--catalog', (Join-Path $postBuildRoot 'catalog.db'), '--userdb', $userDbPath)
    $shortcut = Join-Path $RepositoryRoot 'DanbooruTagTool.lnk'
    if (Test-Path -LiteralPath $shortcut) {
        $shell = New-Object -ComObject WScript.Shell
        $link = $shell.CreateShortcut($shortcut)
        if ([IO.Path]::GetFullPath($link.TargetPath) -ne [IO.Path]::GetFullPath((Join-Path $ArtifactRoot 'DanbooruTagTool.exe')) -or [IO.Path]::GetFullPath($link.WorkingDirectory) -ne [IO.Path]::GetFullPath($ArtifactRoot)) { throw 'Root shortcut target or working directory is incorrect.' }
    }
    $catalogAfter = (Get-FileHash -LiteralPath $catalogPath -Algorithm SHA256).Hash
    $userAfter = (Get-FileHash -LiteralPath $userDbPath -Algorithm SHA256).Hash
    if ($catalogBefore -ne $catalogAfter -or $userBefore -ne $userAfter) { throw 'Protected DB hash changed during runtime refresh.' }
    $exeHash = (Get-FileHash -LiteralPath (Join-Path $ArtifactRoot 'DanbooruTagTool.exe') -Algorithm SHA256).Hash
    $provenance = [ordered]@{ format = 'danbooru-tag-tool-runtime-provenance-v1'; generatedUtc = (Get-Date).ToUniversalTime().ToString('o'); sourceRevision = $resolvedRevision; sourceSelector = $SourceRevision; executable = 'DanbooruTagTool.exe'; executableSha256 = $exeHash; publishedFileCount = $newFiles.Count; catalogSha256 = $catalogAfter; userDbSha256 = $userAfter; maintenanceScript = 'scripts/maintenance/refresh_current_runtime.ps1' }
    $provenance | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $ArtifactRoot 'build-provenance.json') -Encoding utf8
    Write-Output "PASS runtime refresh source=$resolvedRevision files=$($newFiles.Count) exe_sha256=$exeHash catalog_sha256=$catalogAfter userdb_sha256=$userAfter"
} finally {
    if (Test-Path -LiteralPath $tempRoot) { Remove-Item -LiteralPath $tempRoot -Recurse -Force }
}
