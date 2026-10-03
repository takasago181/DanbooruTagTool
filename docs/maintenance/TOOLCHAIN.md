# Current maintenance entrypoints

Choose by purpose; do not start from an old Issue script.

| Purpose | Current tool | Mutation boundary |
| --- | --- | --- |
| Accepted input/hash/schema verification | `dotnet run --project src/DanbooruTagTool.Maintenance -c Release -- verify authority/catalog/current/manifest.json` | read-only |
| Catalog compilation | same CLI: `compile <manifest> <new-empty-output>` | fresh candidate only; no install |
| Catalog structure / UserData diagnosis | `catalog_structural_health.py` / `userdata_health.py` | read-only |
| Worktree ownership/status | `workspace_health.py` | read-only; Batch A census remains baseline |
| Task worktree start/finish | `workspace_task.ps1 -Action Start\|Finish -Issue N` | guarded lifecycle, no forced cleanup |
| Workstation runtime check | `check_local_health.ps1 -ArtifactRoot <runtime>` | read-only; current semantic inputs |
| Candidate publish / smoke / promotion | `publish_portable_runtime.ps1`, `smoke_candidate_runtime.ps1`, `promote_portable_runtime.ps1` | explicit separate runtime decision; preserve UserData |
| Runtime manifest/shape/contracts | `validate_runtime_manifest.ps1`, `check_runtime_shape.ps1`, `validate_production_contract.ps1` | bounded validation |
| CSV transport / execution telemetry | `extract_compact_csv_slice.py`, `validate_execution_telemetry.py`, `audit_execution_overhead.py` | read-only/explicit report |
| Frozen evidence/script replay | `evidence_archive.py restore\|verify <external-directory>` | fresh external tree; verified hashes |

Names above under `scripts/maintenance` unless stated otherwise. Existing healthy
helpers remain shared tooling; no parallel compiler or replacement framework.
`catalog_health.py` is a historical compatibility diagnostic; use structural
health for current catalog schemas. `report_workspace_health.ps1` is the optional
disk-size report; use Batch A's `workspace_health.py` for Git ownership/lifecycle.
`scripts/performance` is opt-in investigation, not a normal build gate.

Closed-Issue scripts/Python suites, Stage/PROMPT research, old build helpers and
their workflow recipes are frozen in the archive snapshot. They are not current
maintenance commands. Reusable CI uses the current tools above; replay instructions
and archive disposition are in `research/README.md`. No script was discarded
without recovery; retained legacy/protected local data has not been cleaned.
