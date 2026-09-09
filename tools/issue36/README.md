# Issue #46 orchestration lane

This is development-time quarantine tooling only. It does not modify production
`data/**`, the runtime Japanese overlay, canonical English data, #32/#35/#41
artifacts, `CURRENT_DEV_TASK.md`, `main`, or Stage10 production state.

The one-command entry point is:

```powershell
./tools/issue36/run_final_orchestration.ps1
```

`Auto` first prepares and executes the mixed pilot. Only a pilot `PILOT_PASS`
allows the same launcher to continue to the full V3.1 lane. The first
implementation verification should use:

```powershell
./tools/issue36/run_final_orchestration.ps1 -Mode Pilot
```

Each semantic role is a separate `codex -a never exec --ephemeral --json`
child process. The launcher records the child `thread.started` identifier,
process metadata, contract SHA, input hash, output hash, and status. Child
responses are captured with `--output-schema` and `--output-last-message`; the
Python layer only materializes inputs, checks schemas/completeness/blinding,
merges frozen external decisions, and validates deterministic boundaries.

Pilot output is under `translation_quarantine/orchestration/issue46_pilot/`.
Full output is under `translation_quarantine/orchestration/issue36_v31/`.
Existing successful batches are skipped only when the input hash and output
hash still match. Failed or stale artifacts fail closed and remain resumable
from the last valid manifest entry; no automatic destructive reset is done.
