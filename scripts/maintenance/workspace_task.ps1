[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][ValidateSet('Start','Finish')][string]$Action,
 [Parameter(Mandatory=$true)][int]$Issue,
 [string]$RepositoryRoot='',
 [string]$TaskPath=''
)
$ErrorActionPreference='Stop'
if(-not $RepositoryRoot){$RepositoryRoot=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)}
$RepositoryRoot=(Resolve-Path -LiteralPath $RepositoryRoot).Path
function GitChecked([string[]]$Arguments){$result=& git -C $RepositoryRoot @Arguments;if($LASTEXITCODE -ne 0){throw "Git failed: $($Arguments -join ' ')"};return $result}
$common=(GitChecked @('rev-parse','--path-format=absolute','--git-common-dir')).Trim()
$layoutPath=Join-Path $common 'workspace-layout.json'
if(-not(Test-Path -LiteralPath $layoutPath)){throw 'workspace-layout.json missing. Choose a stable clean main entry before starting tasks.'}
$layout=Get-Content -LiteralPath $layoutPath -Raw | ConvertFrom-Json
if(-not $TaskPath){$TaskPath=Join-Path $layout.task_root "issue-$Issue"}
$TaskPath=[IO.Path]::GetFullPath($TaskPath)
$taskPrefix=[IO.Path]::GetFullPath($layout.task_root).TrimEnd('\')+'\'
if(-not $TaskPath.StartsWith($taskPrefix,[StringComparison]::OrdinalIgnoreCase)){throw 'TaskPath must be under the configured task_root.'}
if($Action -eq 'Start'){
 GitChecked @('fetch','origin','--prune') | Out-Null
 $mainStatus=& git -C $layout.main_entry status --porcelain=v1 --untracked-files=all
 if($LASTEXITCODE -ne 0 -or $mainStatus){throw 'main entry must be clean; no reset/cleanup will be attempted.'}
 & git -C $layout.main_entry merge --ff-only origin/main
 if($LASTEXITCODE -ne 0){throw 'main cannot fast-forward; inspect instead of resetting.'}
 $branch="dev/issue-$Issue"
 $existing=@(GitChecked @('worktree','list','--porcelain') | Where-Object {$_ -eq "branch refs/heads/$branch"})
 if($existing.Count){throw "Issue $Issue already has a main worktree; resume it instead of creating another."}
 if(Test-Path -LiteralPath $TaskPath){throw 'TaskPath already exists; nothing overwritten.'}
 GitChecked @('worktree','add','-b',$branch,$TaskPath,'origin/main')
 & git -C $TaskPath config --worktree core.autocrlf false
 if($LASTEXITCODE -ne 0){throw 'Task checkout created but source hash configuration failed; preserve it for inspection.'}
 Write-Output "Task checkout: $TaskPath. Build/test/publish scratch belongs under TEMP or the configured artifact_root. Commit before Finish."
}else{
 $registered=@(GitChecked @('worktree','list','--porcelain') | Where-Object {$_ -eq ('worktree '+$TaskPath.Replace('\','/'))})
 if(-not $registered.Count){throw 'TaskPath is not a registered worktree.'}
 $branch=(& git -C $TaskPath symbolic-ref --short HEAD).Trim()
 if($LASTEXITCODE -ne 0 -or $branch -ne "dev/issue-$Issue"){throw 'TaskPath does not own the requested Issue branch.'}
 $dirty=@(& git -C $TaskPath status --porcelain=v1 --untracked-files=all)
 if($LASTEXITCODE -ne 0 -or $dirty.Count){throw 'Uncommitted work remains; commit/review it. No cleanup performed.'}
 $ignored=@(& git -C $TaskPath ls-files --others --ignored --exclude-standard)
 if($LASTEXITCODE -ne 0 -or $ignored.Count){throw 'Ignored/protected files remain. Preserve/review them separately; removal refused.'}
 GitChecked @('fetch','origin','--prune') | Out-Null
 & git -C $TaskPath merge-base --is-ancestor HEAD origin/main
 if($LASTEXITCODE -ne 0){throw 'HEAD is not merged into live main; removal refused (squash merges require separate recovery review).'}
 GitChecked @('worktree','remove',$TaskPath)
 Write-Output "Removed only the empty merged Issue worktree. Branch $branch retained for provenance."
}
