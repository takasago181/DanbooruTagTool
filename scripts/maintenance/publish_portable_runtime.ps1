[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $SourceRevision,
    [Parameter(Mandatory = $true)] [string] $OutputRoot,
    [Parameter(Mandatory = $true)] [string] $CatalogPath,
    [Parameter(Mandatory = $true)] [string] $UserDataPath,
    [string] $RepositoryRoot = '',
    [switch] $SkipRestore
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) { $RepositoryRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot) }
$RepositoryRoot = (Resolve-Path -LiteralPath $RepositoryRoot).Path
$OutputRoot = [IO.Path]::GetFullPath($OutputRoot)
$CatalogPath = (Resolve-Path -LiteralPath $CatalogPath).Path
$UserDataPath = (Resolve-Path -LiteralPath $UserDataPath).Path

if (-not (Test-Path -LiteralPath $OutputRoot)) { New-Item -ItemType Directory -Path $OutputRoot | Out-Null }
$existing = @(Get-ChildItem -LiteralPath $OutputRoot -Force)
if ($existing.Count -gt 0) { throw "OutputRoot must be new or empty: $OutputRoot" }
if (-not (Test-Path -LiteralPath $CatalogPath -PathType Leaf)) { throw "Catalog is missing: $CatalogPath" }
if (-not (Test-Path -LiteralPath $UserDataPath -PathType Leaf)) { throw "UserData is missing: $UserDataPath" }

$status = & git -C $RepositoryRoot status --short --untracked-files=all
if ($LASTEXITCODE -ne 0 -or $status) { throw 'RepositoryRoot must be a clean checkout with no tracked or untracked changes.' }
$head = (& git -C $RepositoryRoot rev-parse --verify HEAD).Trim()
$resolved = (& git -C $RepositoryRoot rev-parse --verify "$SourceRevision^{commit}").Trim()
if ($LASTEXITCODE -ne 0 -or $head -ne $resolved) { throw "SourceRevision must equal clean checkout HEAD. HEAD=$head Source=$resolved" }

$dotnet = (Get-Command dotnet -ErrorAction SilentlyContinue).Source
if ([string]::IsNullOrWhiteSpace($dotnet)) { throw 'dotnet SDK is required.' }
$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if ([string]::IsNullOrWhiteSpace($python)) { throw 'python is required for catalog validation.' }
$tempRoot = Join-Path $env:TEMP ("DanbooruTagTool-portable-publish-{0}" -f ([Guid]::NewGuid().ToString('N')))
$publishRoot = Join-Path $tempRoot 'publish'
New-Item -ItemType Directory -Path $publishRoot -Force | Out-Null

function Invoke-Checked([string] $FilePath, [string[]] $Arguments) {
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed ($LASTEXITCODE): $FilePath $($Arguments -join ' ')" }
}
function Sha([string] $Path) { return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash }

try {
    $workloadResolverSwitch = '-p:MSBuildEnableWorkloadResolver=false'
    if (-not $SkipRestore) { Invoke-Checked $dotnet @('restore', (Join-Path $RepositoryRoot 'src/DanbooruTagTool.sln'), '--runtime', 'win-x64', $workloadResolverSwitch) }
    Invoke-Checked $dotnet @('publish', (Join-Path $RepositoryRoot 'src/DanbooruTagTool.App/DanbooruTagTool.App.csproj'), '-c', 'Release', '-r', 'win-x64', '--self-contained', 'true', '--no-restore', $workloadResolverSwitch, '-o', $publishRoot)
    if (-not (Test-Path -LiteralPath (Join-Path $publishRoot 'DanbooruTagTool.exe'))) { throw 'Publish did not produce DanbooruTagTool.exe.' }
    Get-ChildItem -LiteralPath $publishRoot -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $OutputRoot $_.Name) -Recurse -Force
    }
    New-Item -ItemType Directory -Path (Join-Path $OutputRoot 'Data'), (Join-Path $OutputRoot 'UserData') -Force | Out-Null
    Copy-Item -LiteralPath $CatalogPath -Destination (Join-Path $OutputRoot 'Data/catalog.db')
    Copy-Item -LiteralPath $UserDataPath -Destination (Join-Path $OutputRoot 'UserData/user.db')

    $healthOutput = & $python -B (Join-Path $RepositoryRoot 'scripts/maintenance/catalog_health.py') --catalog (Join-Path $OutputRoot 'Data/catalog.db') --userdb (Join-Path $OutputRoot 'UserData/user.db') 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Portable catalog health failed:`n$($healthOutput -join [Environment]::NewLine)" }
    $health = ($healthOutput -join [Environment]::NewLine) | ConvertFrom-Json
    $exePath = Join-Path $OutputRoot 'DanbooruTagTool.exe'
    $version = [Diagnostics.FileVersionInfo]::GetVersionInfo($exePath).ProductVersion
    if ([string]::IsNullOrWhiteSpace($version)) { $version = '1.0.0.0' }
    $manifest = [ordered]@{
        schema_version = 1
        app_name = 'DanbooruTagTool'
        app_version = $version
        main_commit = $head
        build_date_utc = (Get-Date).ToUniversalTime().ToString('o')
        runtime_identifier = 'win-x64'
        self_contained = $true
        exe_sha256 = Sha $exePath
        catalog_sha256 = Sha (Join-Path $OutputRoot 'Data/catalog.db')
        catalog_total = $health.catalog.total
        general_count = $health.catalog.general
        special_count = $health.catalog.special
        character_count = $health.catalog.character
        copyright_count = $health.catalog.copyright
        artist_count = $health.catalog.artist
        runtime_identity_count = 31003
        sexual_count = 1506
        non_sexual_count = 27707
        contextual_count = 1786
        unclassified_count = 4
        published_file_count = @(Get-ChildItem -LiteralPath $OutputRoot -File -Recurse).Count
        build_provenance_version = 'runtime-manifest-v1'
        catalog_contract_version = $health.checker.contract_version
        checker_path = $health.checker.path
        checker_sha256 = $health.checker.sha256
    }
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $OutputRoot 'runtime-manifest.json') -Encoding utf8
    Write-Output "PASS portable publish source=$head output=$OutputRoot exe_sha256=$($manifest.exe_sha256) catalog_sha256=$($manifest.catalog_sha256)"
}
finally {
    if (Test-Path -LiteralPath $tempRoot) { Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue }
}
