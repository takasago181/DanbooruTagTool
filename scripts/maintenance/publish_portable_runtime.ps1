[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $SourceRevision,
    [Parameter(Mandatory = $true)] [string] $OutputRoot,
    [Parameter(Mandatory = $true)] [string] $CatalogPath,
    [string] $RepositoryRoot = '',
    [string] $DotnetPath = 'dotnet',
    [switch] $SkipRestore
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) { $RepositoryRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot) }
$RepositoryRoot = (Resolve-Path -LiteralPath $RepositoryRoot).Path
$OutputRoot = [IO.Path]::GetFullPath($OutputRoot)
$CatalogPath = (Resolve-Path -LiteralPath $CatalogPath).Path
if (Test-Path -LiteralPath $OutputRoot) {
    if (@(Get-ChildItem -LiteralPath $OutputRoot -Force).Count -gt 0) { throw "OutputRoot must be new or empty: $OutputRoot" }
} else { New-Item -ItemType Directory -Path $OutputRoot | Out-Null }
if (-not (Test-Path -LiteralPath $CatalogPath -PathType Leaf)) { throw "Catalog is missing: $CatalogPath" }

$status = & git -C $RepositoryRoot status --short --untracked-files=all
if ($LASTEXITCODE -ne 0 -or $status) { throw 'RepositoryRoot must be a clean checkout with no tracked or untracked changes.' }
$head = (& git -C $RepositoryRoot rev-parse --verify HEAD).Trim()
$resolved = (& git -C $RepositoryRoot rev-parse --verify "$SourceRevision^{commit}").Trim()
if ($LASTEXITCODE -ne 0 -or $head -ne $resolved) { throw "SourceRevision must equal clean checkout HEAD. HEAD=$head Source=$resolved" }

$dotnet = (Get-Command $DotnetPath -ErrorAction SilentlyContinue).Source
if ([string]::IsNullOrWhiteSpace($dotnet)) { throw 'dotnet SDK is required.' }
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
    Invoke-Checked $dotnet @('publish', (Join-Path $RepositoryRoot 'src/DanbooruTagTool.App/DanbooruTagTool.App.csproj'), '-c', 'Release', '-r', 'win-x64', '--self-contained', 'true', '--no-restore', $workloadResolverSwitch, '-p:PublishSingleFile=true', '-p:IncludeNativeLibrariesForSelfExtract=true', '-p:PublishTrimmed=false', '-p:DebugType=None', '-p:DebugSymbols=false', '-o', $publishRoot)
    if (-not (Test-Path -LiteralPath (Join-Path $publishRoot 'DanbooruTagTool.exe'))) { throw 'Publish did not produce DanbooruTagTool.exe.' }
    Get-ChildItem -LiteralPath $publishRoot -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $OutputRoot $_.Name) -Recurse -Force
    }
    New-Item -ItemType Directory -Path (Join-Path $OutputRoot 'Data'), (Join-Path $OutputRoot 'UserData') -Force | Out-Null
    Copy-Item -LiteralPath $CatalogPath -Destination (Join-Path $OutputRoot 'Data/catalog.db')
    Set-Content -LiteralPath (Join-Path $OutputRoot 'UserData/README.txt') -Encoding utf8 -Value 'Disposable portable runtime. user.db is created on first launch. Never seed this output from a real user profile.'

    $exePath = Join-Path $OutputRoot 'DanbooruTagTool.exe'
    $catalogOutput = Join-Path $OutputRoot 'Data/catalog.db'
    $version = [Diagnostics.FileVersionInfo]::GetVersionInfo($exePath).ProductVersion
    if ([string]::IsNullOrWhiteSpace($version)) { $version = '1.0.0.0' }
    $manifest = [ordered]@{
        schema_version = 2
        app_name = 'DanbooruTagTool'
        app_version = $version
        main_commit = $head
        build_date_utc = (Get-Date).ToUniversalTime().ToString('o')
        runtime_identifier = 'win-x64'
        self_contained = $true
        single_file = $true
        include_native_libraries_for_self_extract = $true
        trimming_enabled = $false
        pdb_included = $false
        exe_sha256 = Sha $exePath
        catalog_sha256 = Sha $catalogOutput
        published_file_count = 0
        build_provenance_version = 'runtime-manifest-v2'
    }
    $manifestPath = Join-Path $OutputRoot 'runtime-manifest.json'
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding utf8
    $manifest.published_file_count = @(Get-ChildItem -LiteralPath $OutputRoot -File -Recurse).Count
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding utf8
    Write-Output "PASS portable publish source=$head output=$OutputRoot exe_sha256=$($manifest.exe_sha256) catalog_sha256=$($manifest.catalog_sha256)"
}
finally {
    if (Test-Path -LiteralPath $tempRoot) { Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue }
}
