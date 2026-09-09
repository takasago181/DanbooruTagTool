[CmdletBinding()]
param(
    [ValidateSet('Auto', 'Pilot', 'Full')]
    [string]$Mode = 'Auto',
    [string]$RunRoot,
    [string]$CodexBin = 'codex'
)

$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$python = (Get-Command python -ErrorAction Stop).Source
$args = @((Join-Path $PSScriptRoot 'orchestrator.py'), '--mode', $Mode.ToLowerInvariant(), '--repo', $repo, '--codex-bin', $CodexBin)
if ($RunRoot) { $args += @('--run-root', $RunRoot) }
& $python @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
