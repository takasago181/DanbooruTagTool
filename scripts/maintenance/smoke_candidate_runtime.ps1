[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$RuntimeRoot)
$ErrorActionPreference='Stop';$root=(Resolve-Path -LiteralPath $RuntimeRoot).Path;$exe=Join-Path $root 'DanbooruTagTool.exe'
& (Join-Path $PSScriptRoot 'check_runtime_shape.ps1') -RuntimeRoot $root -Mode Candidate | Out-Null
$p=Start-Process -FilePath $exe -WorkingDirectory $root -PassThru
try{for($i=0;$i -lt 40;$i++){Start-Sleep -Milliseconds 250;$p.Refresh();if($p.HasExited){throw "Candidate app exited $($p.ExitCode)."};if($p.MainWindowTitle){break}};if($p.MainWindowTitle -ne 'DanbooruTagTool v1'){throw "Candidate WPF title mismatch: $($p.MainWindowTitle)"}}
finally{if(-not $p.HasExited){[void]$p.CloseMainWindow();if(-not $p.WaitForExit(10000)){Stop-Process -Id $p.Id -Force}}}
$userdb=Join-Path $root 'UserData/user.db';if(-not(Test-Path -LiteralPath $userdb)){throw 'First launch did not create disposable UserData/user.db.'}
$python=(Get-Command python -ErrorAction Stop).Source
& $python -B (Join-Path $PSScriptRoot 'userdata_health.py') --userdb $userdb
if($LASTEXITCODE -ne 0){throw 'Disposable UserData health failed.'}
& (Join-Path $PSScriptRoot 'check_runtime_shape.ps1') -RuntimeRoot $root -Mode Candidate | Out-Null
Write-Output 'PASS isolated WPF launch, catalog startup path, disposable UserData creation, candidate shape'
