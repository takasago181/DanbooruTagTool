# Portable runtime maintenance pipeline

This is the canonical path for clean Release publish and bounded production promotion. It replaces legacy loose-DLL publish instructions and never accepts real UserData as a build input.

## Authorities

1. `catalog_structural_health.py`: generic full-catalog SQLite/schema/identity/payload checks; observed counts are reported, not hardcoded.
2. `validate_production_contract.ps1`: accepted source integrity and production coverage contract against protected `SourceRoot` / `AuthorityRoot`.
3. `userdata_health.py`: independent read-only UserData SQLite/hash health.
4. `publish_portable_runtime.ps1`: the only catalog rebuild and clean Release win-x64 publisher.
5. `validate_runtime_manifest.ps1`: schema-v3 provenance, hashes, and publish-flag validation.
6. `check_runtime_shape.ps1`: candidate or installed file-layout guard; installed mode requires a complete UserData hash baseline.
7. `promote_portable_runtime.ps1`: explicit managed-file list with bounded rollback and before/after UserData identity check.

`src/publish-portable.ps1` is a compatibility wrapper only. `refresh_current_runtime.ps1` is retired and fails safely.

## Candidate

Start from freshly fetched live main in a clean checkout. Use protected source and accepted-authority roots; select a new, empty output directory outside the checkout:

```powershell
$source = (git rev-parse HEAD).Trim()
& scripts/maintenance/publish_portable_runtime.ps1 `
  -SourceRevision $source `
  -OutputRoot "$env:TEMP\DTT-candidate-$source" `
  -SourceRoot 'C:\Codex\DanbooruTagTool' `
  -AuthorityRoot (Get-Location).Path `
  -RepositoryRoot (Get-Location).Path
```

The publisher enforces clean exact-HEAD provenance, Release/self-contained `win-x64`, single-file, native self-extraction, trimming off, no PDB, full accepted catalog rebuild, structural validation, and production source-integrity tests. Candidate UserData is disposable; never point it at installed `UserData`.

Before promotion, run `smoke_candidate_runtime.ps1`, `check_runtime_shape.ps1 -Mode Candidate`, manifest validation, the applicable Release suite with the candidate catalog, and production-size scenario/performance gates.

## Installed promotion

Use `promote_portable_runtime.ps1 -CandidateRoot <validated-candidate> -ProductionRoot C:\Codex\DanbooruTagTool-App`. The script snapshots all real UserData file paths/sizes/SHA256, validates existing installed catalog/runtime, refuses implicit path additions/deletions or DLL/PDB sprawl, copies only the explicit managed list, starts the installed WPF app for smoke, verifies UserData identity, and removes only its uniquely named temporary rollback runtime after success. A pre/post UserData mismatch fails closed and retains rollback evidence. Never use `robocopy /MIR` or broad deletion.

Record final provenance in `docs/project/LAST_KNOWN_GOOD.json` and update its human summary. LKG values are snapshots, not future catalog validators.

For storage/worktree diagnosis, run `scripts/maintenance/report_workspace_health.ps1 -RepositoryRoot <repo>`. It reports workspace bytes/files/directories, `.git`, generated build/audit/artifact categories, registered worktree status, and largest directories. It is read-only and has no cleanup mode.
