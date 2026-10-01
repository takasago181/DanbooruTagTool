[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$CandidateRoot,[string]$ProductionRoot='C:\Codex\DanbooruTagTool-App')
$ErrorActionPreference='Stop'
$candidate=(Resolve-Path -LiteralPath $CandidateRoot).Path; $production=[IO.Path]::GetFullPath($ProductionRoot)
if(-not(Test-Path -LiteralPath $production -PathType Container)){throw "Production runtime missing: $production"}
$shape=Join-Path $PSScriptRoot 'check_runtime_shape.ps1'
& $shape -RuntimeRoot $candidate -Mode Candidate | Out-Null
$prodExe=Join-Path $production 'DanbooruTagTool.exe'; if(-not(Test-Path -LiteralPath $prodExe)){throw 'Installed production EXE missing.'}
$temp=Join-Path $env:TEMP ('DTT-promotion-'+[guid]::NewGuid().ToString('N')); $rollback=Join-Path $temp 'rollback'; New-Item -ItemType Directory -Path $rollback -Force | Out-Null
$userRoot=Join-Path $production 'UserData'; $beforeFiles=@(Get-ChildItem -LiteralPath $userRoot -File -Recurse -Force | ForEach-Object {$rel=$_.FullName.Substring($userRoot.Length).TrimStart('\');[pscustomobject]@{path=$rel;bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}} | Sort-Object path)
$baseline=[ordered]@{files=$beforeFiles}; $baselinePath=Join-Path $temp 'userdata-before.json'; $baseline | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $baselinePath -Encoding utf8
$inventory=[ordered]@{captured_utc=[DateTime]::UtcNow.ToString('o');root=$production;files=@(Get-ChildItem -LiteralPath $production -File -Recurse -Force | ForEach-Object {$rel=$_.FullName.Substring($production.Length).TrimStart('\');[pscustomobject]@{path=$rel;bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}});userdata=$beforeFiles}
$inventory | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $temp 'production-before.json') -Encoding utf8
function Compare-UserData {
 $now=@(Get-ChildItem -LiteralPath $userRoot -File -Recurse -Force | ForEach-Object {$rel=$_.FullName.Substring($userRoot.Length).TrimStart('\');[pscustomobject]@{path=$rel;bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}} | Sort-Object path)
 if((ConvertTo-Json -InputObject $now -Depth 4 -Compress) -cne (ConvertTo-Json -InputObject $beforeFiles -Depth 4 -Compress)){throw 'UserData inventory/hash changed; promotion is fail-closed.'}
}
function Stop-InstalledApp {
 $named=@(Get-Process -Name 'DanbooruTagTool' -ErrorAction SilentlyContinue)
 foreach($process in $named){try{$path=[IO.Path]::GetFullPath($process.Path)}catch{throw 'Could not identify a running DanbooruTagTool process safely.'};if($path -eq [IO.Path]::GetFullPath($prodExe)){if(-not $process.CloseMainWindow()){throw 'Unable to close installed app gracefully.'};if(-not $process.WaitForExit(15000)){throw 'Installed app did not close safely.'}}}
}
function Smoke-Installed {
 $p=Start-Process -FilePath $prodExe -WorkingDirectory $production -WindowStyle Hidden -PassThru
 try{$title='';for($i=0;$i -lt 40;$i++){Start-Sleep -Milliseconds 250;$p.Refresh();if($p.HasExited){throw "Installed WPF process exited with code $($p.ExitCode)."};$title=$p.MainWindowTitle;if($title){break}};if($title -ne 'DanbooruTagTool v1'){throw "Installed WPF smoke title mismatch: '$title'."}}
 finally{if(-not $p.HasExited){[void]$p.CloseMainWindow();if(-not $p.WaitForExit(10000)){Stop-Process -Id $p.Id -Force}}}
}
$managed=@(Get-ChildItem -LiteralPath $candidate -File -Recurse -Force | Where-Object {$_.FullName -notmatch '[\\/]UserData[\\/]'} | ForEach-Object {$_.FullName.Substring($candidate.Length+1).Replace('\','/')})
if($managed -contains 'UserData/user.db' -or $managed -contains 'UserData/README.txt'){throw 'Internal error: candidate UserData entered the promotion file list.'}
try {
 Stop-InstalledApp; Compare-UserData
 $beforeDll=@(Get-ChildItem -LiteralPath $production -File -Filter '*.dll' -Recurse -Force); $beforePdb=@(Get-ChildItem -LiteralPath $production -File -Filter '*.pdb' -Recurse -Force)
 if($beforeDll.Count -or $beforePdb.Count){throw 'Installed runtime is not lean single-file; promotion refuses to clean existing files implicitly.'}
 foreach($p in @((Join-Path $production 'Data/catalog.db'),(Join-Path $production 'runtime-manifest.json'),(Join-Path $production 'ForgeBridge'))){if(-not(Test-Path -LiteralPath $p)){throw "Installed runtime component missing: $p"}}
 $python=(Get-Command python -ErrorAction Stop).Source
 & $python -B (Join-Path $PSScriptRoot 'catalog_structural_health.py') --catalog (Join-Path $production 'Data/catalog.db') | Out-Null
 if($LASTEXITCODE -ne 0){throw 'Installed catalog structural preflight failed.'}
 $existing=@(Get-ChildItem -LiteralPath $production -File -Recurse -Force | Where-Object {$_.FullName -notmatch '[\\/]UserData[\\/]'} | ForEach-Object {$_.FullName.Substring($production.Length+1).Replace('\','/')})
 if(Compare-Object ($managed | Sort-Object) ($existing | Sort-Object)){throw 'Installed runtime payload paths differ from candidate; bounded promotion refuses implicit add/delete.'}
 foreach($relative in $managed){$source=Join-Path $candidate ($relative.Replace('/','\'));$destination=Join-Path $production ($relative.Replace('/','\'));$saved=Join-Path $rollback ($relative.Replace('/','\'));New-Item -ItemType Directory -Path (Split-Path -Parent $saved) -Force | Out-Null;Copy-Item -LiteralPath $destination -Destination $saved -Force}
 foreach($relative in $managed){$source=Join-Path $candidate ($relative.Replace('/','\'));$destination=Join-Path $production ($relative.Replace('/','\'));Copy-Item -LiteralPath $source -Destination $destination -Force}
 & $shape -RuntimeRoot $production -Mode Installed -UserDataBaseline $baselinePath | Out-Null
 Smoke-Installed; Compare-UserData
 $exeHash=(Get-FileHash -LiteralPath $prodExe -Algorithm SHA256).Hash; $catalogHash=(Get-FileHash -LiteralPath (Join-Path $production 'Data/catalog.db') -Algorithm SHA256).Hash; $manifestHash=(Get-FileHash -LiteralPath (Join-Path $production 'runtime-manifest.json') -Algorithm SHA256).Hash
 $tempBase=[IO.Path]::GetFullPath($env:TEMP).TrimEnd('\')+'\';$resolvedTemp=[IO.Path]::GetFullPath($temp)
 if(-not $resolvedTemp.StartsWith($tempBase+'DTT-promotion-',[StringComparison]::OrdinalIgnoreCase)){throw "Refusing to remove unexpected rollback temp path: $resolvedTemp"}
 Remove-Item -LiteralPath $resolvedTemp -Recurse -Force
 [pscustomobject]@{ok=$true;production_root=$production;exe_sha256=$exeHash;catalog_sha256=$catalogHash;manifest_sha256=$manifestHash;userdata_byte_identical=$true;managed_paths=$managed} | ConvertTo-Json -Depth 5 -Compress
} catch {
 if(Test-Path -LiteralPath $rollback){foreach($relative in $managed){$saved=Join-Path $rollback ($relative.Replace('/','\'));$destination=Join-Path $production ($relative.Replace('/','\'));if(Test-Path -LiteralPath $saved){Copy-Item -LiteralPath $saved -Destination $destination -Force}}}
 Write-Error "Promotion failed; managed runtime rollback attempted. Rollback evidence retained at $temp. $($_.Exception.Message)"; throw
}
