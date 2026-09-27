[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$SourceRevision,
 [Parameter(Mandatory=$true)][string]$OutputRoot,
 [Parameter(Mandatory=$true)][string]$SourceRoot,
 [Parameter(Mandatory=$true)][string]$AuthorityRoot,
 [string]$RepositoryRoot='',
 [switch]$SkipRestore
)
$ErrorActionPreference='Stop'
if(-not $RepositoryRoot){$RepositoryRoot=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)}
$RepositoryRoot=(Resolve-Path -LiteralPath $RepositoryRoot).Path
$OutputRoot=[IO.Path]::GetFullPath($OutputRoot)
$SourceRoot=(Resolve-Path -LiteralPath $SourceRoot).Path; $AuthorityRoot=(Resolve-Path -LiteralPath $AuthorityRoot).Path
$rootPrefix=$RepositoryRoot.TrimEnd('\')+'\'
if($OutputRoot.StartsWith($rootPrefix,[StringComparison]::OrdinalIgnoreCase)){throw 'OutputRoot must be outside the source checkout.'}
if(Test-Path -LiteralPath $OutputRoot){if(@(Get-ChildItem -LiteralPath $OutputRoot -Force).Count){throw "OutputRoot must be fresh and empty: $OutputRoot"}}else{New-Item -ItemType Directory -Path $OutputRoot | Out-Null}
$status=& git -C $RepositoryRoot status --porcelain=v1 --untracked-files=all
if($LASTEXITCODE -ne 0 -or $status){throw 'Publish requires a completely clean checkout.'}
$head=(& git -C $RepositoryRoot rev-parse --verify HEAD).Trim(); $resolved=(& git -C $RepositoryRoot rev-parse --verify "$SourceRevision^{commit}").Trim()
if($LASTEXITCODE -ne 0 -or $head -ne $resolved){throw "SourceRevision must resolve exactly to clean HEAD. HEAD=$head requested=$resolved"}
$dotnet=(Get-Command dotnet -ErrorAction Stop).Source; $python=(Get-Command python -ErrorAction Stop).Source
$work=Join-Path $env:TEMP ('DTT-publish-'+[guid]::NewGuid().ToString('N')); $publish=Join-Path $work 'publish'; $built=Join-Path $work 'accepted-catalog'; $contract=Join-Path $work 'contract.json'
New-Item -ItemType Directory -Path $publish,$built | Out-Null
function Invoke-Checked([string]$exe,[string[]]$arguments){& $exe @arguments; if($LASTEXITCODE -ne 0){throw "Command failed ($LASTEXITCODE): $exe $($arguments -join ' ')"}}
function Sha([string]$path){(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash}
function Invoke-CatalogBuild([string]$exe,[string[]]$arguments){
 $start=New-Object Diagnostics.ProcessStartInfo; $start.FileName=$exe; $start.WorkingDirectory=$RepositoryRoot; $start.UseShellExecute=$false
 foreach($argument in $arguments){[void]$start.ArgumentList.Add($argument)}
 $process=[Diagnostics.Process]::Start($start); $process.WaitForExit()
 if($process.ExitCode -ne 0){$errorPath=Join-Path $publish 'catalog-build-error.txt';$detail=if(Test-Path -LiteralPath $errorPath){Get-Content -LiteralPath $errorPath -Raw}else{''};throw "Catalog builder failed ($($process.ExitCode)). $detail"}
}
try {
 $appProject=Join-Path $RepositoryRoot 'src/DanbooruTagTool.App/DanbooruTagTool.App.csproj'
 $solution=Join-Path $RepositoryRoot 'src/DanbooruTagTool.sln'
 if(-not $SkipRestore){Invoke-Checked $dotnet @('restore',$solution,'--runtime','win-x64','-p:MSBuildEnableWorkloadResolver=false')}
 Invoke-Checked $dotnet @('publish',$appProject,'-c','Release','-r','win-x64','--self-contained','true','--no-restore','-p:PublishSingleFile=true','-p:IncludeNativeLibrariesForSelfExtract=true','-p:PublishTrimmed=false','-p:DebugSymbols=false','-p:DebugType=None','-p:MSBuildEnableWorkloadResolver=false','-o',$publish)
 $exe=Join-Path $publish 'DanbooruTagTool.exe'; if(-not(Test-Path -LiteralPath $exe)){throw 'Publish did not create DanbooruTagTool.exe.'}
 if(@(Get-ChildItem -LiteralPath $publish -File -Filter '*.dll' -Recurse).Count -or @(Get-ChildItem -LiteralPath $publish -File -Filter '*.pdb' -Recurse).Count){throw 'Publish produced loose DLL or PDB files.'}
 Invoke-CatalogBuild $exe @('--build-catalog',$SourceRoot,$AuthorityRoot,$built)
 $catalog=Join-Path $built 'catalog.db'; if(-not(Test-Path -LiteralPath $catalog)){throw 'Accepted full catalog build did not produce catalog.db.'}
 $structuralRaw=& $python -B (Join-Path $RepositoryRoot 'scripts/maintenance/catalog_structural_health.py') --catalog $catalog
 if($LASTEXITCODE -ne 0){throw "Structural catalog validation failed: $structuralRaw"}; $structural=$structuralRaw | ConvertFrom-Json
 & (Join-Path $RepositoryRoot 'scripts/maintenance/validate_production_contract.ps1') -CatalogPath $catalog -SourceRoot $SourceRoot -AuthorityRoot $AuthorityRoot -ReportPath $contract -RepositoryRoot $RepositoryRoot | Out-Null
 $contractResult=Get-Content -LiteralPath $contract -Raw | ConvertFrom-Json
 if($contractResult.catalog_sha256 -ne $structural.catalog_sha256){throw 'Production contract report does not describe the structurally checked catalog.'}
 $sourceReport=Get-Content -LiteralPath (Join-Path $built 'import-report.json') -Raw | ConvertFrom-Json
 Get-ChildItem -LiteralPath $publish -Force | ForEach-Object {Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $OutputRoot $_.Name) -Recurse -Force}
 New-Item -ItemType Directory -Path (Join-Path $OutputRoot 'Data'),(Join-Path $OutputRoot 'UserData') -Force | Out-Null
 Copy-Item -LiteralPath $catalog -Destination (Join-Path $OutputRoot 'Data/catalog.db')
 Set-Content -LiteralPath (Join-Path $OutputRoot 'UserData/README.txt') -Value 'Disposable UserData only. First launch creates this candidate runtime user.db.' -Encoding utf8
 $exePath=Join-Path $OutputRoot 'DanbooruTagTool.exe'; $catalogPath=Join-Path $OutputRoot 'Data/catalog.db'
 $appVersion=[Diagnostics.FileVersionInfo]::GetVersionInfo($exePath).ProductVersion; if([string]::IsNullOrWhiteSpace($appVersion)){$appVersion='1.0.0'}
 $fileCount=@(Get-ChildItem -LiteralPath $OutputRoot -File -Recurse | Where-Object {$_.FullName -notmatch '[\\/]UserData[\\/]'}).Count+1
 $forge=@{}; $forgeRoot=Join-Path $OutputRoot 'ForgeBridge'
 if(Test-Path -LiteralPath $forgeRoot){foreach($f in Get-ChildItem -LiteralPath $forgeRoot -File -Recurse){$relative=$f.FullName.Substring($OutputRoot.Length+1).Replace('\','/');$forge[$relative]=Sha $f.FullName}}
 $manifest=[ordered]@{
   schema_version=3; app_name='DanbooruTagTool'; app_version=$appVersion
   source_main_commit=$head; build_utc=[DateTime]::UtcNow.ToString('o'); runtime_identifier='win-x64'
   self_contained=$true; single_file=$true; native_libraries_self_extract=$true; publish_trimmed=$false; debug_symbols=$false; pdb_present=$false
   exe_sha256=(Sha $exePath); catalog_sha256=(Sha $catalogPath); catalog_total=[int]$structural.total; catalog_category_counts=$structural.category_counts
   structural_validator=$structural.validator; production_contract_validator=@{id=$contractResult.validator_id;version=$contractResult.validator_version;sha256=(Sha (Join-Path $RepositoryRoot 'scripts/maintenance/validate_production_contract.ps1'))}
   production_contract=@{contract_test=$contractResult.contract_test;source_count=$contractResult.source_count;source_report_sha256=$contractResult.source_report_sha256;source_hashes=$sourceReport.Sources}
   runtime_file_count=$fileCount; runtime_file_count_scope='excluding mutable UserData'; real_userdata_embedded=$false; forgebridge_file_hashes=$forge
 }
 $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $OutputRoot 'runtime-manifest.json') -Encoding utf8
 & (Join-Path $RepositoryRoot 'scripts/maintenance/validate_runtime_manifest.ps1') -RuntimeRoot $OutputRoot | Out-Null
 & (Join-Path $RepositoryRoot 'scripts/maintenance/check_runtime_shape.ps1') -RuntimeRoot $OutputRoot -Mode Candidate | Out-Null
 Write-Output "PASS canonical publish source=$head catalog=$($manifest.catalog_total) files=$fileCount exe_sha256=$($manifest.exe_sha256) catalog_sha256=$($manifest.catalog_sha256)"
} finally {if(Test-Path -LiteralPath $work){$tempBase=[IO.Path]::GetFullPath($env:TEMP).TrimEnd('\')+'\';$resolvedWork=[IO.Path]::GetFullPath($work);if(-not $resolvedWork.StartsWith($tempBase+'DTT-publish-',[StringComparison]::OrdinalIgnoreCase)){Write-Warning "Keeping unexpected publish temp path for review: $resolvedWork"}else{$removed=$false;for($i=0;$i -lt 5;$i++){try{Remove-Item -LiteralPath $resolvedWork -Recurse -Force -ErrorAction Stop;$removed=$true;break}catch{Start-Sleep -Milliseconds 500}};if(-not $removed){Write-Warning "Could not remove only the generated publish scratch path: $resolvedWork"}}}}
