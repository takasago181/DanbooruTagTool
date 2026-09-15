[CmdletBinding()]
param(
    [string] $RepositoryRoot = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)),
    [string] $ArtifactRoot = ''
)

$ErrorActionPreference = 'Stop'
$RepositoryRoot = (Resolve-Path -LiteralPath $RepositoryRoot).Path
if ([string]::IsNullOrWhiteSpace($ArtifactRoot)) { $ArtifactRoot = Join-Path $RepositoryRoot 'artifacts/current' }
$ArtifactRoot = (Resolve-Path -LiteralPath $ArtifactRoot).Path
$checks = [System.Collections.Generic.List[object]]::new()
function Add-Check([string] $Name, [string] $Result, [string] $Detail) { $checks.Add([pscustomobject]@{Name=$Name;Result=$Result;Detail=$Detail}) }
function Sha([string] $Path) { return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash }
function Run-Json([string] $FilePath, [string[]] $Arguments) { $out = & $FilePath @Arguments 2>&1; $exit = $LASTEXITCODE; return [pscustomobject]@{Output=($out -join [Environment]::NewLine);ExitCode=$exit} }

$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if ([string]::IsNullOrWhiteSpace($python)) { Add-Check 'python' 'FAIL' 'Python is required for read-only SQLite/queue checks.' }
$head = (& git -C $RepositoryRoot rev-parse --verify HEAD).Trim()
$branch = (& git -C $RepositoryRoot branch --show-current).Trim()
$status = & git -C $RepositoryRoot status --short --untracked-files=no
if ($status) { Add-Check 'git status' 'WARN' "tracked changes present on $branch" } else { Add-Check 'git status' 'PASS' "clean tracked tree on $branch" }
Add-Check 'source revision' 'PASS' "HEAD $head"

$provenancePath = Join-Path $ArtifactRoot 'build-provenance.json'
$exePath = Join-Path $ArtifactRoot 'DanbooruTagTool.exe'
if ((Test-Path -LiteralPath $provenancePath) -and (Test-Path -LiteralPath $exePath)) {
    try {
        $provenance = Get-Content -LiteralPath $provenancePath -Raw | ConvertFrom-Json
        $exeHash = Sha $exePath
        if ($provenance.sourceRevision -eq $head -and $provenance.executableSha256 -eq $exeHash) { Add-Check 'runtime provenance' 'PASS' "source $($provenance.sourceRevision), exe hash matches" } else { Add-Check 'runtime provenance' 'WARN' "recorded source=$($provenance.sourceRevision), HEAD=$head, hash_match=$($provenance.executableSha256 -eq $exeHash)" }
    } catch { Add-Check 'runtime provenance' 'FAIL' $_.Exception.Message }
} else { Add-Check 'runtime provenance' 'WARN' 'build-provenance.json or executable is missing; run refresh_current_runtime.ps1.' }

$shortcut = Join-Path $RepositoryRoot 'DanbooruTagTool.lnk'
if (Test-Path -LiteralPath $shortcut) {
    $shell = New-Object -ComObject WScript.Shell; $link = $shell.CreateShortcut($shortcut)
    $expected = [IO.Path]::GetFullPath($exePath); $actual = [IO.Path]::GetFullPath($link.TargetPath)
    if ($actual -eq $expected -and [IO.Path]::GetFullPath($link.WorkingDirectory) -eq $ArtifactRoot) { Add-Check 'root shortcut' 'PASS' $actual } else { Add-Check 'root shortcut' 'FAIL' "target=$actual working=$($link.WorkingDirectory)" }
} else { Add-Check 'root shortcut' 'WARN' 'DanbooruTagTool.lnk is not present.' }

$catalogPath = Join-Path $ArtifactRoot 'Data/catalog.db'; $userDbPath = Join-Path $ArtifactRoot 'UserData/user.db'
foreach($path in @($catalogPath,$userDbPath)){if(Test-Path -LiteralPath $path){Add-Check "exists $([IO.Path]::GetFileName($path))" 'PASS' "$path"}else{Add-Check "exists $([IO.Path]::GetFileName($path))" 'FAIL' "$path is missing"}}
if(-not [string]::IsNullOrWhiteSpace($python) -and (Test-Path -LiteralPath $catalogPath) -and (Test-Path -LiteralPath $userDbPath)) {
    $db = Run-Json $python @('-B',(Join-Path $RepositoryRoot 'scripts/maintenance/catalog_health.py'),'--catalog',$catalogPath,'--userdb',$userDbPath)
    if($db.ExitCode -eq 0){$parsed=$db.Output | ConvertFrom-Json; Add-Check 'SQLite/catalog semantics' 'PASS' "quick/integrity ok; total=$($parsed.catalog.total), Special=$($parsed.catalog.special), General=$($parsed.catalog.general), SpecialBrowseV2=$($parsed.catalog.special_browse_v2)"}else{Add-Check 'SQLite/catalog semantics' 'FAIL' $db.Output}
}

$inputs = @('data/source/danbooru-2026-09-02.csv','data/derived/danbooru_alias_normalized_index_VERIFIED_34417.csv','data/special2788/illustrious_tag_knowledge_base_2788.csv','data/derived/special2788_VERIFIED_LINKAGE.csv','data/derived/ruleset2/01_SPECIAL2788_JAPANESE_COMPLETE_CANDIDATE.csv','data/runtime/japanese_overlay.json','data/special2788/product_fit_verdicts.csv','docs/issue64/production_candidate/general_taxonomy.json','docs/issue64/production_candidate/effective_sidecar.csv','docs/issue64/production_candidate/manifest.json','docs/issue56/rollout/issue56_ui_genre_taxonomy_v1.json')
$missing = @($inputs | Where-Object { -not (Test-Path -LiteralPath (Join-Path $RepositoryRoot $_)) })
if($missing.Count -eq 0){Add-Check 'catalog build inputs' 'PASS' "$($inputs.Count) required paths exist"}else{Add-Check 'catalog build inputs' 'FAIL' ($missing -join ', ')}

$queue = Join-Path $RepositoryRoot 'docs/issue70/data/queue_state.json'; $queueBefore = if(Test-Path -LiteralPath $queue){Sha $queue}else{''}
if(-not [string]::IsNullOrWhiteSpace($python)){ $q = Run-Json $python @('-B',(Join-Path $RepositoryRoot 'scripts/issue70/queue_manager.py'),'status'); $queueAfter=if(Test-Path -LiteralPath $queue){Sha $queue}else{''}; if($q.ExitCode -eq 0 -and $queueBefore -eq $queueAfter){Add-Check 'Issue #70 read-only status' 'PASS' (($q.Output -replace '\s+',' ').Trim())}elseif($q.ExitCode -eq 0){Add-Check 'Issue #70 read-only status' 'FAIL' 'queue_state.json changed during status check'}else{Add-Check 'Issue #70 read-only status' 'FAIL' $q.Output}}
$retired=@('data/runtime_index','data/runtime_source','tools/legacy','translation_quarantine','archive','_handoff'); $present=@($retired | Where-Object {Test-Path -LiteralPath (Join-Path $RepositoryRoot $_)}); if($present.Count -eq 0){Add-Check 'retired dependencies' 'PASS' 'retired Python/Tk/runtime-index paths absent'}else{Add-Check 'retired dependencies' 'WARN' ($present -join ', ')}

$checks | ForEach-Object { Write-Output ("{0,-28} {1,-5} {2}" -f $_.Name,$_.Result,$_.Detail) }
$fail = @($checks | Where-Object Result -eq 'FAIL').Count; $warn = @($checks | Where-Object Result -eq 'WARN').Count
if($fail -gt 0){Write-Output "SUMMARY FAIL ($fail failures, $warn warnings)"; exit 1}
if($warn -gt 0){Write-Output "SUMMARY WARN ($warn warnings)"; exit 0}
Write-Output 'SUMMARY PASS'; exit 0
