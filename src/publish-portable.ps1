[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Catalog,
    [string]$Output = (Join-Path $PSScriptRoot 'artifacts/portable'),
    [string]$Dotnet = 'dotnet'
)
$ErrorActionPreference = 'Stop'
$catalogPath=(Resolve-Path -LiteralPath $Catalog).Path
$publishPath=[IO.Path]::GetFullPath($Output)
if (Test-Path -LiteralPath $publishPath) { throw 'Output already exists. Choose a new folder to protect existing data.' }
$revision=(& git -C $PSScriptRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Could not identify source revision.' }
& (Join-Path $PSScriptRoot '../scripts/maintenance/publish_portable_runtime.ps1') -SourceRevision $revision -OutputRoot $publishPath -CatalogPath $catalogPath -RepositoryRoot $PSScriptRoot -DotnetPath $Dotnet
if ($LASTEXITCODE -ne 0) { throw 'Portable publish failed.' }
Write-Output $publishPath
