[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$CatalogPath,
 [Parameter(Mandatory=$true)][string]$SourceRoot,
 [Parameter(Mandatory=$true)][string]$AuthorityRoot,
 [Parameter(Mandatory=$true)][string]$ReportPath,
 [string]$RepositoryRoot=''
)
$ErrorActionPreference='Stop'
if(-not $RepositoryRoot){$RepositoryRoot=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)}
$RepositoryRoot=(Resolve-Path -LiteralPath $RepositoryRoot).Path
foreach($p in @($CatalogPath,$SourceRoot,$AuthorityRoot)){if(-not(Test-Path -LiteralPath $p)){throw "Production contract input missing: $p"}}
$dotnet=(Get-Command dotnet -ErrorAction Stop).Source
$old=@{DTT_PRODUCTION_CATALOG=$env:DTT_PRODUCTION_CATALOG;DTT_SOURCE_ROOT=$env:DTT_SOURCE_ROOT;DTT_AUTHORITY_ROOT=$env:DTT_AUTHORITY_ROOT}
try {
 $env:DTT_PRODUCTION_CATALOG=(Resolve-Path -LiteralPath $CatalogPath).Path
 $env:DTT_SOURCE_ROOT=(Resolve-Path -LiteralPath $SourceRoot).Path
 $env:DTT_AUTHORITY_ROOT=(Resolve-Path -LiteralPath $AuthorityRoot).Path
 & $dotnet test (Join-Path $RepositoryRoot 'src/DanbooruTagTool.Tests/DanbooruTagTool.Tests.csproj') -c Release --filter 'FullyQualifiedName~ProductionCatalogCoverageEligibilitySearchAndSourceIntegrity' -p:MSBuildEnableWorkloadResolver=false
 if($LASTEXITCODE -ne 0){throw "Current production source-integrity/coverage test failed ($LASTEXITCODE)."}
 $report=Join-Path (Split-Path -Parent (Resolve-Path -LiteralPath $CatalogPath).Path) 'import-report.json'
 if(-not(Test-Path -LiteralPath $report)){throw 'Catalog import-report.json missing; source provenance cannot be verified.'}
 $json=Get-Content -LiteralPath $report -Raw | ConvertFrom-Json
 if(-not $json.Sources -or -not $json.Profile -or $json.Profile -ne 'full'){throw 'Catalog report is not a full accepted-source build report.'}
 $entry=[ordered]@{ok=$true;validator_id='dtt.production-source-contract';validator_version='2.0.0';catalog_sha256=(Get-FileHash -LiteralPath $CatalogPath -Algorithm SHA256).Hash;source_report_sha256=(Get-FileHash -LiteralPath $report -Algorithm SHA256).Hash;source_count=@($json.Sources.PSObject.Properties).Count;contract_test='ProductionCatalogCoverageEligibilitySearchAndSourceIntegrity';validated_utc=[DateTime]::UtcNow.ToString('o')}
 $entry | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ReportPath -Encoding utf8
 $entry | ConvertTo-Json -Compress
} finally { foreach($name in $old.Keys){if($null -eq $old[$name]){Remove-Item -Path "Env:$name" -ErrorAction SilentlyContinue}else{Set-Item -Path "Env:$name" -Value $old[$name]}} }
