[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $RuntimeRoot,
    [string] $ReportPath = '',
    [string] $UserDataBaselinePath = '',
    [switch] $RequireSingleFile
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath $RuntimeRoot).Path.TrimEnd('\')
if ($ReportPath -and [IO.Path]::GetFullPath($ReportPath).StartsWith($root + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'ReportPath must be outside RuntimeRoot.' }
$expectedDirs = @('Data', 'UserData', 'ForgeBridge')
$top = @(Get-ChildItem -LiteralPath $root -Force)
$files = @(Get-ChildItem -LiteralPath $root -File -Recurse -Force)
$dlls = @(Get-ChildItem -LiteralPath $root -File -Filter '*.dll' -Force)
$pdbs = @(Get-ChildItem -LiteralPath $root -File -Filter '*.pdb' -Recurse -Force)
$unexpectedDirs = @($top | Where-Object { $_.PSIsContainer -and $_.Name -notin $expectedDirs } | ForEach-Object Name)
$unexpectedFiles = @($top | Where-Object { -not $_.PSIsContainer -and $_.Name -notin @('DanbooruTagTool.exe','runtime-manifest.json') } | ForEach-Object Name)
$exe = Join-Path $root 'DanbooruTagTool.exe'
$catalog = Join-Path $root 'Data/catalog.db'
$manifestPath = Join-Path $root 'runtime-manifest.json'
function HashOrNull([string] $Path) { if (Test-Path -LiteralPath $Path -PathType Leaf) { return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash }; return $null }
$userFiles = @(Get-ChildItem -LiteralPath (Join-Path $root 'UserData') -File -Recurse -Force -ErrorAction SilentlyContinue | Sort-Object FullName | ForEach-Object {
    [ordered]@{ path = $_.FullName.Substring($root.Length + 1).Replace('\','/'); bytes = $_.Length; sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash }
})
$userBytes = [long]0
foreach ($file in $userFiles) { $userBytes += [long]$file.bytes }
$manifest = $null
if (Test-Path -LiteralPath $manifestPath -PathType Leaf) { $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json }
$record = [ordered]@{
    checked_at_utc = (Get-Date).ToUniversalTime().ToString('o')
    runtime_root = $root
    total_bytes = [long](($files | Measure-Object -Property Length -Sum).Sum)
    total_files = $files.Count
    root_dll_count = $dlls.Count
    pdb_count = $pdbs.Count
    unexpected_top_level_dirs = $unexpectedDirs
    unexpected_top_level_files = $unexpectedFiles
    top_level = @($top | ForEach-Object { if ($_.PSIsContainer) { [ordered]@{ name=$_.Name; type='directory' } } else { [ordered]@{ name=$_.Name; type='file'; bytes=$_.Length } } })
    single_file_expected = $true
    exe_sha256 = HashOrNull $exe
    catalog_sha256 = HashOrNull $catalog
    runtime_manifest_sha256 = HashOrNull $manifestPath
    user_data_bytes = $userBytes
    user_data_file_count = $userFiles.Count
    user_data_files = $userFiles
    manifest = $manifest
    userdata_baseline_matches = $null
}
if ($UserDataBaselinePath) {
    $baseline = Get-Content -LiteralPath $UserDataBaselinePath -Raw | ConvertFrom-Json
    $baselineFiles = @($baseline.user_data_files | Sort-Object path | ForEach-Object { "{0}|{1}|{2}" -f $_.path,$_.bytes,$_.sha256 })
    $actualFiles = @($userFiles | Sort-Object path | ForEach-Object { "{0}|{1}|{2}" -f $_.path,$_.bytes,$_.sha256 })
    $record.userdata_baseline_matches = (($baselineFiles -join "`n") -ceq ($actualFiles -join "`n"))
}
$validShape = ($record.root_dll_count -eq 0 -and $record.pdb_count -eq 0 -and $unexpectedDirs.Count -eq 0 -and $unexpectedFiles.Count -eq 0 -and
    (Test-Path -LiteralPath $exe -PathType Leaf) -and (Test-Path -LiteralPath $catalog -PathType Leaf) -and
    $manifest -and $manifest.single_file -eq $true -and $manifest.self_contained -eq $true -and $manifest.include_native_libraries_for_self_extract -eq $true -and
    $manifest.trimming_enabled -eq $false -and $manifest.pdb_included -eq $false -and
    $manifest.exe_sha256 -eq $record.exe_sha256 -and $manifest.catalog_sha256 -eq $record.catalog_sha256)
$record.single_file_shape_pass = [bool]$validShape
$json = $record | ConvertTo-Json -Depth 10
if ($ReportPath) { $json | Set-Content -LiteralPath $ReportPath -Encoding utf8 }
Write-Output $json
if ($RequireSingleFile -and -not $validShape) { throw 'Runtime does not meet the lean single-file contract.' }
if ($RequireSingleFile -and $record.userdata_baseline_matches -eq $false) { throw 'UserData differs from the supplied baseline.' }
