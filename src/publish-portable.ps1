[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$SourceRevision,
 [Parameter(Mandatory=$true)][string]$OutputRoot,
 [Parameter(Mandatory=$true)][string]$SourceRoot,
 [Parameter(Mandatory=$true)][string]$AuthorityRoot,
 [string]$RepositoryRoot=(Split-Path -Parent $PSScriptRoot),
 [switch]$SkipRestore
)
$ErrorActionPreference='Stop'
$canonical=Join-Path $RepositoryRoot 'scripts/maintenance/publish_portable_runtime.ps1'
& $canonical -SourceRevision $SourceRevision -OutputRoot $OutputRoot -SourceRoot $SourceRoot -AuthorityRoot $AuthorityRoot -RepositoryRoot $RepositoryRoot -SkipRestore:$SkipRestore
