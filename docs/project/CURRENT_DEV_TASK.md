# CURRENT DEV TASK — POST-#131 RUNTIME / PERFORMANCE AUDIT

最終同期: 2026-09-20

## Routing status

- Live main authority is the post-sync main containing this block; the optimization merge before sync was `eebccbf7feafff6f86546c4624841d5978953dd6`.
- PR #133 `[MAINT] Post-#131 runtime and portable production hardening` is merged.
- PR #135 post-#131 performance/runtime optimization is merged and production-validated.
- Post-#131 production/runtime integration is complete.
- #117/#118 implementation and the former local-runtime gate are no longer the current DEV task.
- #131 UI refinement is complete and already represented in the current runtime.
- Performance / Runtime Load Audit and the safe post-audit optimization lane are complete. The adopted change defers unused `Related` projection while preserving compatibility; no further optimization candidate is adopted without new measurement evidence.
- #70 Character/Copyright/Artist work and taxonomy-usability/classification audit are independent lanes. Do not mix their branches, commits, data, or decisions into this task.

## Current production runtime authority

User-facing workstation runtime:

`C:\Codex\DanbooruTagTool-App`

Current runtime contract:

- self-contained `win-x64`;
- shortcut target: `C:\Codex\DanbooruTagTool-App\DanbooruTagTool.exe`;
- shortcut working directory: `C:\Codex\DanbooruTagTool-App`;
- `runtime-manifest.json` records build/main provenance and runtime hashes;
- current catalog SHA-256:
  `DFDC93581F2E8E3041FBC497F9A1C5CFD458977EF57462E05902F27D29B97CF9`;
- the final production EXE and manifest hashes are recorded in the fresh post-sync runtime promotion report;
- current catalog totals:
  - Total 33,688
  - General 30,629
  - Special 3,059
  - Character/Copyright/Artist 0 / 0 / 0
  - runtime identities 31,003
  - SEXUAL 1,506
  - NON_SEXUAL 27,707
  - CONTEXTUAL 1,786
  - UNCLASSIFIED 4.

The older local `artifacts/current/` runtime is retained as a fallback/reference artifact but is **not the current user-facing launch target**.

## UserData authority

`UserData` is user-owned state, not a deploy artifact.

The validated portable promotion copied the existing user database byte-for-byte and verified source/destination SHA equality before and after runtime launch.

Permanent operational rule:

- never delete, overwrite, reset, mirror-delete, or silently replace real `UserData`;
- runtime publishing is code/catalog/runtime -> target only;
- UserData preservation is a separate explicit step and must be hash-checked when a runtime is promoted;
- do not use `git clean -fdx`, `git clean -fdX`, `robocopy /MIR`, or broad runtime-directory replacement against protected local state.

## Rendering authority

PR #133 removed the explicit:

`RenderOptions.ProcessRenderMode = RenderMode.SoftwareOnly`

Current main therefore uses normal WPF/Windows automatic render selection.

The A/B rendering audit is complete. Automatic WPF render selection remains the
baseline: idle CPU/disk settled to approximately zero and no clear total-load
win justified restoring SoftwareOnly.

## Performance audit boundaries

Measure before optimizing.

Required categories include:

- startup;
- settled idle;
- dictionary scrolling;
- Japanese / English / mixed search;
- route/facet/content/DeepOnly switching;
- Prompt add/remove/edit/order/category operations;
- resize;
- post-operation idle;
- CPU / GPU / Working Set / Private memory / threads / handles / disk read-write;
- leak/drift checks.

Do not change production behavior merely because code looks suspicious.

Any optimization after the SoftwareOnly A/B must be:

`baseline -> measurement -> candidate -> same-condition measurement -> regression -> adopt/reject`.

## Protected boundaries

This current task does not own:

- #70 Character/Copyright/Artist data;
- taxonomy-usability/classification audit;
- General/Special semantic membership;
- #118 content-intent semantics;
- PromptToken/search semantics;
- canonical identity;
- real UserData;
- ForgeBridge behavior.

Do not merge those lanes into the performance audit.

## Stop rule

Performance audit may add isolated measurement scripts/docs on its own branch.

Additional optimizations require new measurement evidence and must not cross the
#70, taxonomy, classification, canonical, PromptToken, ForgeBridge, catalog, or
real UserData boundaries.

Historical #117/#118 implementation details remain available from their Issues, commits, and Git history; they are no longer the routing task represented by this file.
