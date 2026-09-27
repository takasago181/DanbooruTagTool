[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$RuntimeRoot)
$ErrorActionPreference='Stop'
$root=(Resolve-Path -LiteralPath $RuntimeRoot).Path
$manifestPath=Join-Path $root 'runtime-manifest.json'; $exePath=Join-Path $root 'DanbooruTagTool.exe'; $catalogPath=Join-Path $root 'Data/catalog.db'
foreach($p in @($manifestPath,$exePath,$catalogPath)){if(-not(Test-Path -LiteralPath $p -PathType Leaf)){throw "Required runtime file missing: $p"}}
$m=Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if($m.schema_version -ne 3){throw "Unsupported runtime manifest schema: $($m.schema_version)"}
if($m.real_userdata_embedded -ne $false){throw 'Manifest must state real_userdata_embedded=false.'}
if($m.runtime_identifier -ne 'win-x64' -or -not $m.self_contained -or -not $m.single_file -or -not $m.native_libraries_self_extract -or $m.publish_trimmed -or $m.debug_symbols -or $m.pdb_present){throw 'Manifest publish shape flags are invalid.'}
if(-not $m.source_main_commit -or -not $m.build_utc -or -not $m.app_version -or $m.runtime_file_count_scope -ne 'excluding mutable UserData'){throw 'Manifest provenance or runtime-file scope metadata missing.'}
if($m.exe_sha256 -notmatch '^[A-F0-9]{64}$' -or $m.catalog_sha256 -notmatch '^[A-F0-9]{64}$'){throw 'Manifest SHA256 format is invalid.'}
$exeHash=(Get-FileHash -LiteralPath $exePath -Algorithm SHA256).Hash
$catHash=(Get-FileHash -LiteralPath $catalogPath -Algorithm SHA256).Hash
if($exeHash -ne $m.exe_sha256){throw 'Manifest EXE hash mismatch.'}
if($catHash -ne $m.catalog_sha256){throw 'Manifest catalog hash mismatch.'}
if(-not $m.structural_validator.id -or -not $m.structural_validator.version -or $m.structural_validator.sha256 -notmatch '^[A-F0-9]{64}$'){throw 'Structural validator metadata missing or invalid.'}
if(-not $m.production_contract_validator.id -or -not $m.production_contract_validator.version -or $m.production_contract_validator.sha256 -notmatch '^[A-F0-9]{64}$'){throw 'Production contract validator metadata missing or invalid.'}
if([int]$m.catalog_total -lt 1 -or [int](($m.catalog_category_counts.PSObject.Properties | Measure-Object -Property Value -Sum).Sum) -ne [int]$m.catalog_total){throw 'Manifest observed catalog counts do not sum to catalog_total.'}
if([int]$m.runtime_file_count -lt 1){throw 'Manifest runtime_file_count is invalid.'}
[pscustomobject]@{ok=$true;schema_version=$m.schema_version;exe_sha256=$exeHash;catalog_sha256=$catHash;catalog_total=$m.catalog_total;runtime_file_count=$m.runtime_file_count} | ConvertTo-Json -Compress
