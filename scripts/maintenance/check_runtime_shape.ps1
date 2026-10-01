[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$RuntimeRoot,
  [Parameter(Mandatory=$true)][ValidateSet('Candidate','Installed')][string]$Mode,
  [string]$UserDataBaseline
)
$ErrorActionPreference='Stop'; $root=(Get-Item -LiteralPath $RuntimeRoot).FullName
$manifest=Join-Path $root 'runtime-manifest.json'; $exe=Join-Path $root 'DanbooruTagTool.exe'; $catalog=Join-Path $root 'Data/catalog.db'; $user=Join-Path $root 'UserData'
& (Join-Path $PSScriptRoot 'validate_runtime_manifest.ps1') -RuntimeRoot $root | Out-Null
$files=@(Get-ChildItem -LiteralPath $root -File -Recurse -Force); $rootDlls=@(Get-ChildItem -LiteralPath $root -File -Filter '*.dll' -Force); $allDlls=@($files | Where-Object Extension -ieq '.dll'); $pdbs=@($files | Where-Object Extension -ieq '.pdb')
if($allDlls.Count -ne 0){throw "Unexpected runtime DLLs: $($allDlls.Count)"}; if($pdbs.Count -ne 0){throw "PDB files are forbidden: $($pdbs.Count)"}
$allowed=@('DanbooruTagTool.exe','runtime-manifest.json','Data','UserData','ForgeBridge')
$unexpected=@(Get-ChildItem -LiteralPath $root -Force | Where-Object {$allowed -notcontains $_.Name}); if($unexpected.Count){throw "Unexpected top-level runtime entries: $($unexpected.Name -join ', ')"}
foreach($required in @($exe,$manifest,$catalog,$user,(Join-Path $root 'ForgeBridge'))){if(-not(Test-Path -LiteralPath $required)){throw "Required runtime path missing: $required"}}
$dataFiles=@(Get-ChildItem -LiteralPath (Join-Path $root 'Data') -File -Recurse -Force)
if($dataFiles.Count -ne 1 -or $dataFiles[0].FullName -ne [IO.Path]::GetFullPath($catalog)){throw 'Data must contain only the external catalog.db.'}
$user=(Get-Item -LiteralPath $user).FullName
if($Mode -eq 'Candidate'){
  $userFiles=@(Get-ChildItem -LiteralPath $user -File -Recurse -Force)
  $invalid=@($userFiles | Where-Object {
    $relative=$_.FullName.Substring($user.Length).TrimStart('\\')
    $known=$relative -in @('README.txt','user.db','generation-library.db','generation-library.db-journal','generation-library.db-wal','generation-library.db-shm','lora-library.db','lora-library.db-journal','lora-library.db-wal','lora-library.db-shm')
    $migrationBackup=$relative -match '^(generation-library|lora-library)\.db\.before-migration-[a-f0-9]{32}\.bak$'
    $thumbnail=$relative -match '^Cache\\GenerationThumbnails\\[A-F0-9]{64}(\.png|\.[a-f0-9]{32}\.tmp)$'
    -not ($known -or $migrationBackup -or $thumbnail)
  })
  if($invalid.Count){$invalidRelative=@($invalid | ForEach-Object {$_.FullName.Substring($user.Length).TrimStart('\\')});throw "Candidate UserData contains files outside the documented disposable shape: $($invalidRelative -join ', ')"}
} elseif(-not $UserDataBaseline){throw 'Installed mode requires a complete UserData baseline.'}
else {
  $baseline=Get-Content -LiteralPath $UserDataBaseline -Raw | ConvertFrom-Json
  $current=@(Get-ChildItem -LiteralPath $user -File -Recurse -Force | ForEach-Object { $rel=$_.FullName.Substring($user.Length).TrimStart('\'); [pscustomobject]@{path=$rel;bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash} } | Sort-Object path)
  $expected=@($baseline.files | Sort-Object path)
  $currentSignature=@($current | ForEach-Object {"$($_.path)|$($_.bytes)|$($_.sha256)"})
  $expectedSignature=@($expected | ForEach-Object {"$($_.path)|$($_.bytes)|$($_.sha256)"})
  $difference=Compare-Object -ReferenceObject $currentSignature -DifferenceObject $expectedSignature
  if($difference){throw "Installed UserData inventory differs from protected baseline. current=$($currentSignature -join ';') expected=$($expectedSignature -join ';')"}
}
$totalBytes=($files | Measure-Object -Property Length -Sum).Sum
$m=Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
$payloadFiles=@($files | Where-Object {$_.FullName -notmatch '[\\/]UserData[\\/]'}).Count
if($payloadFiles -ne [int]$m.runtime_file_count){throw "Manifest runtime_file_count mismatch: observed=$payloadFiles manifest=$($m.runtime_file_count)."}
foreach($pair in $m.forgebridge_file_hashes.PSObject.Properties){$path=Join-Path $root ($pair.Name.Replace('/','\'));if(-not(Test-Path -LiteralPath $path -PathType Leaf)){throw "Manifest ForgeBridge file missing: $($pair.Name)"};if((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $pair.Value){throw "ForgeBridge hash mismatch: $($pair.Name)"}}
$actualForge=@(Get-ChildItem -LiteralPath (Join-Path $root 'ForgeBridge') -File -Recurse -Force).Count
if($actualForge -ne @($m.forgebridge_file_hashes.PSObject.Properties).Count){throw 'ForgeBridge contains an unmanifested file.'}
[pscustomobject]@{ok=$true;mode=$Mode;total_bytes=$totalBytes;file_count=$files.Count;runtime_payload_file_count=$payloadFiles;root_dll_count=$rootDlls.Count;pdb_count=$pdbs.Count;exe_sha256=(Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash;catalog_sha256=(Get-FileHash -LiteralPath $catalog -Algorithm SHA256).Hash} | ConvertTo-Json -Compress
