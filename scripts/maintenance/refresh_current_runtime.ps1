[CmdletBinding()]
param([string]$SourceRevision,[string]$RepositoryRoot='',[string]$ArtifactRoot='',[switch]$SkipRestore)

throw 'Retired by Issue #210. This legacy artifacts/current refresher copied UserData and pruned outputs. Use publish_portable_runtime.ps1 to create an isolated candidate, then promote_portable_runtime.ps1 for a bounded installed update.'
