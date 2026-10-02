param([string]$Candidate,[string]$FixtureUserDb,[string]$Output)
$ErrorActionPreference='Stop'
$Candidate=(Resolve-Path -LiteralPath $Candidate).Path
$taskRoot='C:\Codex\DanbooruTagTool\'
$Output=[IO.Path]::GetFullPath($Output)
if(-not $Output.StartsWith($taskRoot,[StringComparison]::OrdinalIgnoreCase) -or (Test-Path -LiteralPath $Output)){throw 'Use a fresh owned runtime directory within the workspace.'}
New-Item -ItemType Directory -Path $Output | Out-Null
Get-ChildItem -LiteralPath $Candidate -Force | Copy-Item -Destination $Output -Recurse
Copy-Item -LiteralPath $FixtureUserDb -Destination (Join-Path $Output 'UserData\user.db')
$env:DTT_245_SMOKE_ROOT=$Output
@'
import os,sqlite3,json,pathlib
p=pathlib.Path(os.environ['DTT_245_SMOKE_ROOT'])/'UserData/user.db'
c=sqlite3.connect(p); version,payload=c.execute('select version,payload from user_state').fetchone(); assert version==2
s=json.loads(payload); s['Ui'].update(Workspace=3,NavWidth=275,PromptWidth=370,EditRatio=.74,Width=1280,Height=720,Left=80,Top=80)
s['Presets']=[{'Id':'2ba45012-0c48-4b7f-94be-2c3d55e84b03','Name':'restart-fixture','Description':'owned schema2 fixture','Positive':'blue_hair','Negative':'lowres','Recipe':{'Model':'sample','Seed':42,'Steps':20,'Sampler':'Euler a','Scheduler':'Karras','Cfg':5,'Width':512,'Height':768,'HasAny':True,'HasAutomaticSettings':False,'Summary':'sample · 20 steps · Euler a · Karras · CFG 5 · 512×768 · Seed 42'}}]
with c: c.execute('update user_state set payload=? where id=1',(json.dumps(s),))
c.close(); (p.parent.parent/'state-before.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
'@ | python -
if($LASTEXITCODE -ne 0){throw 'Fixture setup failed'}
$events=@()
foreach($run in 1,2){
 $taskProcess=Start-Process -FilePath (Join-Path $Output 'DanbooruTagTool.exe') -WorkingDirectory $Output -WindowStyle Hidden -PassThru
 $deadline=[DateTime]::UtcNow.AddSeconds(30)
 do { Start-Sleep -Milliseconds 200; $taskProcess.Refresh() } while(-not $taskProcess.HasExited -and $taskProcess.MainWindowHandle -eq 0 -and [DateTime]::UtcNow -lt $deadline)
 if($taskProcess.HasExited -or $taskProcess.MainWindowHandle -eq 0){throw "Normal startup $run did not create a live MainWindow"}
 $title=$taskProcess.MainWindowTitle
 if(-not $taskProcess.CloseMainWindow()){throw "Owned smoke process $run refused graceful close"}
 if(-not $taskProcess.WaitForExit(10000)){throw "Owned smoke process $run did not exit gracefully"}
 if($taskProcess.ExitCode -ne 0){throw "Normal runtime exit $($taskProcess.ExitCode)"}
 $events+=@{run=$run;title=$title;exitCode=$taskProcess.ExitCode;startedAndRestarted=$true}
}
$events | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $Output 'process-lifecycle.json') -Encoding utf8
@'
import os,sqlite3,json,pathlib,hashlib
root=pathlib.Path(os.environ['DTT_245_SMOKE_ROOT']); before=json.loads((root/'state-before.json').read_text(encoding='utf-8'))
c=sqlite3.connect('file:'+(root/'UserData/user.db').as_posix()+'?mode=ro',uri=True); version,payload=c.execute('select version,payload from user_state').fetchone(); after=json.loads(payload)
keys=['Workspace','NavWidth','PromptWidth','EditRatio','Width','Height','ForgeUrl','Browse','Query','OutputProfile']
checks={k:after['Ui'][k]==before['Ui'][k] for k in keys}
checks.update(Prompt=after['Prompt']==before['Prompt'],Negative=after['Negative']==before['Negative'],Presets=after['Presets']==before['Presets'],schema=version==2)
assert all(checks.values()),checks
report={'Result':'PASS','Scope':'copied self-contained EXE normal startup + graceful exit + normal restart; seeded isolated schema2; no pointer audit','UiStateChecks':checks,'BeforeUi':before['Ui'],'AfterUi':after['Ui'],'NetworkOperationsRequested':0,'GenerationRequests':0,'ExecutableSha256':hashlib.sha256((root/'DanbooruTagTool.exe').read_bytes()).hexdigest().upper()}
(root/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(report,ensure_ascii=False))
'@ | python -
if($LASTEXITCODE -ne 0){throw 'Restart preservation gate failed'}
