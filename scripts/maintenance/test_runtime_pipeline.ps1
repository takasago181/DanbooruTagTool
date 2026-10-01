$ErrorActionPreference='Stop'
$root=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$temp=Join-Path $env:TEMP ('DTT-runtime-tests-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $temp | Out-Null
function Assert-Fails([scriptblock]$action,[string]$label){$failed=$false;try{& $action}catch{$failed=$true};if(-not $failed){throw "$label unexpectedly passed"}}
function Write-Manifest([string]$runtime){
 $exe=Join-Path $runtime 'DanbooruTagTool.exe';$catalog=Join-Path $runtime 'Data/catalog.db';$forge=Join-Path $runtime 'ForgeBridge/scripts/dtt_bridge.py'
 $files=@(Get-ChildItem -LiteralPath $runtime -File -Recurse | Where-Object {$_.FullName -notmatch '[\\/]UserData[\\/]' -and $_.Name -ne 'runtime-manifest.json'}).Count+1
 $manifest=[ordered]@{schema_version=3;app_version='1.0';source_main_commit=('C'*40);build_utc=[DateTime]::UtcNow.ToString('o');runtime_identifier='win-x64';self_contained=$true;single_file=$true;native_libraries_self_extract=$true;publish_trimmed=$false;debug_symbols=$false;pdb_present=$false;real_userdata_embedded=$false;exe_sha256=(Get-FileHash $exe -Algorithm SHA256).Hash;catalog_sha256=(Get-FileHash $catalog -Algorithm SHA256).Hash;catalog_total=1;catalog_category_counts=@{General=1};runtime_file_count=$files;runtime_file_count_scope='excluding mutable UserData';structural_validator=@{id='struct';version='1';sha256=('A'*64)};production_contract_validator=@{id='contract';version='1';sha256=('B'*64)};forgebridge_file_hashes=@{'ForgeBridge/scripts/dtt_bridge.py'=(Get-FileHash $forge -Algorithm SHA256).Hash}}
 $manifest|ConvertTo-Json -Depth 8|Set-Content (Join-Path $runtime 'runtime-manifest.json') -Encoding utf8
}
try {
 $parseFiles=@('validate_runtime_manifest.ps1','check_runtime_shape.ps1','validate_production_contract.ps1','publish_portable_runtime.ps1','promote_portable_runtime.ps1','smoke_candidate_runtime.ps1','test_runtime_pipeline.ps1')
 foreach($name in $parseFiles){$tokens=$null;$parseErrors=$null;[System.Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot $name),[ref]$tokens,[ref]$parseErrors)|Out-Null;if($parseErrors.Count){throw "PowerShell syntax failure in $name : $($parseErrors.Message -join '; ')"}}
 $runtime=Join-Path $temp 'runtime';New-Item -ItemType Directory -Path (Join-Path $runtime 'Data'),(Join-Path $runtime 'UserData'),(Join-Path $runtime 'ForgeBridge/scripts') -Force|Out-Null
 Set-Content (Join-Path $runtime 'DanbooruTagTool.exe') 'exe';Set-Content (Join-Path $runtime 'Data/catalog.db') 'catalog';Set-Content (Join-Path $runtime 'UserData/README.txt') 'disposable';Set-Content (Join-Path $runtime 'ForgeBridge/scripts/dtt_bridge.py') 'bridge';Write-Manifest $runtime
 & (Join-Path $PSScriptRoot 'validate_runtime_manifest.ps1') -RuntimeRoot $runtime | Out-Null
 & (Join-Path $PSScriptRoot 'check_runtime_shape.ps1') -RuntimeRoot $runtime -Mode Candidate | Out-Null
 Set-Content (Join-Path $runtime 'DanbooruTagTool.exe') 'changed'
 Assert-Fails {& (Join-Path $PSScriptRoot 'validate_runtime_manifest.ps1') -RuntimeRoot $runtime | Out-Null} 'EXE hash mismatch'
 Write-Manifest $runtime;Set-Content (Join-Path $runtime 'Data/catalog.db') 'changed'
 Assert-Fails {& (Join-Path $PSScriptRoot 'validate_runtime_manifest.ps1') -RuntimeRoot $runtime | Out-Null} 'catalog hash mismatch'
 Set-Content (Join-Path $runtime 'Data/catalog.db') 'catalog';Write-Manifest $runtime;Set-Content (Join-Path $runtime 'extra.dll') 'bad'
 Assert-Fails {& (Join-Path $PSScriptRoot 'check_runtime_shape.ps1') -RuntimeRoot $runtime -Mode Candidate | Out-Null} 'extra DLL'
 Remove-Item -LiteralPath (Join-Path $runtime 'extra.dll');Write-Manifest $runtime
 Set-Content (Join-Path $runtime 'UserData/user.db') 'disposable'
 & (Join-Path $PSScriptRoot 'check_runtime_shape.ps1') -RuntimeRoot $runtime -Mode Candidate | Out-Null
 New-Item -ItemType Directory -Path (Join-Path $runtime 'UserData/nested') -Force|Out-Null;Set-Content (Join-Path $runtime 'UserData/nested/user.db') 'wrong path'
 Assert-Fails {& (Join-Path $PSScriptRoot 'check_runtime_shape.ps1') -RuntimeRoot $runtime -Mode Candidate | Out-Null} 'nested candidate UserData rejection'
 Remove-Item -LiteralPath (Join-Path $runtime 'UserData/nested/user.db') -Force;Remove-Item -LiteralPath (Join-Path $runtime 'UserData/nested') -Force
 $baseline=Join-Path $temp 'baseline.json';$userRoot=Join-Path $runtime 'UserData';$userFile=Join-Path $userRoot 'user.db';$baselineFiles=@(Get-ChildItem -LiteralPath $userRoot -File -Recurse|ForEach-Object {[pscustomobject]@{path=$_.FullName.Substring($userRoot.Length).TrimStart('\\');bytes=$_.Length;sha256=(Get-FileHash $_.FullName -Algorithm SHA256).Hash}});@{files=$baselineFiles}|ConvertTo-Json -Depth 4|Set-Content $baseline
 & (Join-Path $PSScriptRoot 'check_runtime_shape.ps1') -RuntimeRoot $runtime -Mode Installed -UserDataBaseline $baseline | Out-Null
 Set-Content $userFile 'changed'
 Assert-Fails {& (Join-Path $PSScriptRoot 'check_runtime_shape.ps1') -RuntimeRoot $runtime -Mode Installed -UserDataBaseline $baseline | Out-Null} 'installed UserData baseline mismatch'
 $publish=Get-Content (Join-Path $PSScriptRoot 'publish_portable_runtime.ps1') -Raw
 if($publish -match 'UserDataPath|Copy-Item[^\r\n]*user\.db' -or $publish -notmatch 'PublishSingleFile=true' -or $publish -notmatch 'IncludeNativeLibrariesForSelfExtract=true' -or $publish -notmatch 'PublishTrimmed=false' -or $publish -notmatch 'DebugSymbols=false' -or $publish -notmatch 'DebugType=None'){throw 'Canonical publish authority/static flags regression.'}
 if($publish -match 'runtime_identity_count|sexual_count|non_sexual_count|contextual_count|general_count\s*=|special_count\s*='){throw 'Stale hard-coded semantic population fields remain in the manifest publisher.'}
 $wrapper=Get-Content (Join-Path $root 'src/publish-portable.ps1') -Raw
 if($wrapper -match 'dotnet publish|PublishSingleFile='){throw 'Compatibility entry point contains independent publish settings.'}
 $publisher=Join-Path $PSScriptRoot 'publish_portable_runtime.ps1';$fakeRepo=Join-Path $temp 'fake-repo';$source=Join-Path $temp 'source';$authority=Join-Path $temp 'authority';New-Item -ItemType Directory -Path $fakeRepo,$source,$authority -Force|Out-Null
 & git init -b main $fakeRepo | Out-Null;& git -C $fakeRepo config user.email 'test@example.invalid';& git -C $fakeRepo config user.name 'Pipeline Test';Set-Content (Join-Path $fakeRepo 'README.md') 'base';& git -C $fakeRepo add README.md;& git -C $fakeRepo commit -m 'test base'|Out-Null;$fakeHead=(& git -C $fakeRepo rev-parse HEAD).Trim()
 $nonEmpty=Join-Path $temp 'non-empty-output';New-Item -ItemType Directory -Path $nonEmpty|Out-Null;Set-Content (Join-Path $nonEmpty 'keep.txt') 'keep'
 Assert-Fails {& $publisher -SourceRevision $fakeHead -OutputRoot $nonEmpty -SourceRoot $source -AuthorityRoot $authority -RepositoryRoot $fakeRepo} 'non-empty output rejection'
 Assert-Fails {& $publisher -SourceRevision ('F'*40) -OutputRoot (Join-Path $temp 'wrong-revision') -SourceRoot $source -AuthorityRoot $authority -RepositoryRoot $fakeRepo 2>$null} 'wrong source revision rejection'
 Set-Content (Join-Path $fakeRepo 'dirty.txt') 'dirty'
 Assert-Fails {& $publisher -SourceRevision $fakeHead -OutputRoot (Join-Path $temp 'dirty-source') -SourceRoot $source -AuthorityRoot $authority -RepositoryRoot $fakeRepo} 'dirty source checkout rejection'
 Write-Output 'PASS manifest hash, candidate/installed shape, disposable UserData, single canonical publisher contracts'
} finally {if(Test-Path -LiteralPath $temp){$tempBase=[IO.Path]::GetFullPath($env:TEMP).TrimEnd('\')+'\';$resolvedTemp=[IO.Path]::GetFullPath($temp);if(-not $resolvedTemp.StartsWith($tempBase+'DTT-runtime-tests-',[StringComparison]::OrdinalIgnoreCase)){throw "Refusing to remove unexpected test temp path: $resolvedTemp"};Remove-Item -LiteralPath $resolvedTemp -Recurse -Force}}
