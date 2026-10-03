[CmdletBinding()]
param(
    [string] $RepositoryRoot = '',
    [string] $ArtifactRoot = ''
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) { $RepositoryRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot) }
$RepositoryRoot = (Resolve-Path -LiteralPath $RepositoryRoot).Path
if ([string]::IsNullOrWhiteSpace($ArtifactRoot)) { $ArtifactRoot = Join-Path $RepositoryRoot 'artifacts/current' }
$ArtifactRoot = (Resolve-Path -LiteralPath $ArtifactRoot).Path
$checks = [System.Collections.Generic.List[object]]::new()
function Add-Check([string] $Name, [string] $Result, [string] $Detail) { $checks.Add([pscustomobject]@{Name=$Name;Result=$Result;Detail=$Detail}) }
function Sha([string] $Path) { return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash }
function Run-Json([string] $FilePath, [string[]] $Arguments) { $out = & $FilePath @Arguments 2>&1; $exit = $LASTEXITCODE; return [pscustomobject]@{Output=($out -join [Environment]::NewLine);ExitCode=$exit} }

$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if ([string]::IsNullOrWhiteSpace($python)) { Add-Check 'python' 'FAIL' 'Python is required for read-only SQLite checks.' }
$head = (& git -C $RepositoryRoot rev-parse --verify HEAD).Trim()
$branch = (& git -C $RepositoryRoot branch --show-current).Trim()
$status = & git -C $RepositoryRoot status --short --untracked-files=no
if ($status) {
    & git -C $RepositoryRoot diff --ignore-space-at-eol --quiet --exit-code
    if ($LASTEXITCODE -eq 0) { Add-Check 'git status' 'PASS' "tracked status on $branch is line-ending-only; no semantic delta" }
    else { Add-Check 'git status' 'WARN' "semantic tracked changes present on $branch" }
} else { Add-Check 'git status' 'PASS' "clean tracked tree on $branch" }
Add-Check 'source revision' 'PASS' "HEAD $head"

$exePath = Join-Path $ArtifactRoot 'DanbooruTagTool.exe'
$runtimeManifest = Join-Path $ArtifactRoot 'runtime-manifest.json'
if ((Test-Path -LiteralPath $runtimeManifest) -and (Test-Path -LiteralPath $exePath)) {
    try {
        $verified = & (Join-Path $RepositoryRoot 'scripts/maintenance/validate_runtime_manifest.ps1') -RuntimeRoot $ArtifactRoot | ConvertFrom-Json
        if (-not $verified.ok) { throw 'Runtime manifest validation did not confirm success.' }
        $manifest = Get-Content -LiteralPath $runtimeManifest -Raw | ConvertFrom-Json
        Add-Check 'runtime manifest' 'PASS' "schema=$($manifest.schema_version), commit=$($manifest.source_main_commit), RID=$($manifest.runtime_identifier); hashes verified"
        if ($manifest.source_main_commit -eq $head) { Add-Check 'runtime provenance' 'PASS' "source $head" }
        else { Add-Check 'runtime provenance' 'WARN' "runtime source=$($manifest.source_main_commit), HEAD=$head; production unchanged" }
    } catch { Add-Check 'runtime manifest' 'FAIL' $_.Exception.Message }
} else { Add-Check 'runtime manifest' 'WARN' 'Current runtime manifest or executable is missing.' }

$shortcut = Join-Path $RepositoryRoot 'DanbooruTagTool.lnk'
if (Test-Path -LiteralPath $shortcut) {
    $shell = New-Object -ComObject WScript.Shell; $link = $shell.CreateShortcut($shortcut)
    $expected = [IO.Path]::GetFullPath($exePath); $actual = [IO.Path]::GetFullPath($link.TargetPath)
    if ($actual -eq $expected -and [IO.Path]::GetFullPath($link.WorkingDirectory) -eq $ArtifactRoot) { Add-Check 'root shortcut' 'PASS' $actual } else { Add-Check 'root shortcut' 'FAIL' "target=$actual working=$($link.WorkingDirectory)" }
} else { Add-Check 'root shortcut' 'WARN' 'DanbooruTagTool.lnk is not present.' }

$catalogPath = Join-Path $ArtifactRoot 'Data/catalog.db'; $userDbPath = Join-Path $ArtifactRoot 'UserData/user.db'
foreach($path in @($catalogPath,$userDbPath)){if(Test-Path -LiteralPath $path){Add-Check "exists $([IO.Path]::GetFileName($path))" 'PASS' "$path"}else{Add-Check "exists $([IO.Path]::GetFileName($path))" 'FAIL' "$path is missing"}}
if(-not [string]::IsNullOrWhiteSpace($python) -and (Test-Path -LiteralPath $catalogPath) -and (Test-Path -LiteralPath $userDbPath)) {
    $db = Run-Json $python @('-B',(Join-Path $RepositoryRoot 'scripts/maintenance/catalog_structural_health.py'),'--catalog',$catalogPath)
    if($db.ExitCode -eq 0){$parsed=$db.Output | ConvertFrom-Json;Add-Check 'catalog structural health' 'PASS' "validator=$($parsed.validator.id)/$($parsed.validator.version); rows=$($parsed.total); categories=$($parsed.category_counts | ConvertTo-Json -Compress); sha256=$($parsed.catalog_sha256)"}else{Add-Check 'catalog structural health' 'FAIL' $db.Output}
    $user = Run-Json $python @('-B',(Join-Path $RepositoryRoot 'scripts/maintenance/userdata_health.py'),'--userdb',$userDbPath)
    if($user.ExitCode -eq 0){$parsed=$user.Output | ConvertFrom-Json;Add-Check 'UserData health' 'PASS' "state_present=$($parsed.state_present); bytes=$($parsed.bytes); sha256=$($parsed.sha256)"}else{Add-Check 'UserData health' 'FAIL' $user.Output}
}

$dotnet = (Get-Command dotnet -ErrorAction SilentlyContinue).Source
if ($dotnet) {
    $authority = Run-Json $dotnet @('run','--project',(Join-Path $RepositoryRoot 'src/DanbooruTagTool.Maintenance'),'-c','Release','--','verify',(Join-Path $RepositoryRoot 'authority/catalog/current/manifest.json'))
    if ($authority.ExitCode -eq 0) { Add-Check 'accepted semantic authority' 'PASS' $authority.Output }
    else { Add-Check 'accepted semantic authority' 'FAIL' $authority.Output }
} else { Add-Check 'accepted semantic authority' 'WARN' 'dotnet SDK unavailable; run Maintenance verify in a development environment.' }

$checks | ForEach-Object { Write-Output ("{0,-28} {1,-5} {2}" -f $_.Name,$_.Result,$_.Detail) }
$fail = @($checks | Where-Object Result -eq 'FAIL').Count; $warn = @($checks | Where-Object Result -eq 'WARN').Count
if($fail -gt 0){Write-Output "SUMMARY FAIL ($fail failures, $warn warnings)"; exit 1}
if($warn -gt 0){Write-Output "SUMMARY WARN ($warn warnings)"; exit 0}
Write-Output 'SUMMARY PASS'; exit 0
