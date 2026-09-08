# Issue #30 — Forge Neo A/B automation dry-run task

## Purpose

Run the smallest decisive **non-Stage10-production** end-to-end dry run for Issue #30 using the already-validated Issue #6 Forge Neo comparison environment.

This task validates the automation plumbing only:

`fixed A/B request -> Forge Neo API -> saved PNG -> PNG metadata -> WD14 API -> machine-readable evidence -> REVIEW-safe summary`

Do **not** establish production winner/scoring rules in this task.

## Ownership / isolation

- Owner: Issue #30 `[Stage10-PREP][TEMP] Forge Neo A/B automation & external-tool integration`.
- Use a separate worktree/task context from Issue #35 and dictionary validation work.
- Suggested branch if repository evidence must be committed: `temp/issue30-ab-dry-run`.
- Do **not** edit `docs/project/CURRENT_DEV_TASK.md`; it remains owned by active DEV Issue #35.
- Do **not** edit `danbooru_tag_tool/ui.py`, `tests/test_stage7a_ui.py`, `validation_quarantine/**`, or `data/**`.
- Do not merge concurrently with another branch. Evidence may be pushed to a TEMP branch for review.

## Preconditions inherited from completed Issue #6

Treat these as verified baseline facts unless current runtime contradicts them:

- Issue #6 = `PASS_WITH_NOTE / completed`.
- WAI Illustrious SDXL v170 baseline generation works.
- Built-in X/Y/Z fixed-seed comparison works.
- Multi Prompt Slots is installed at fixed SHA `b3f45b17e5a24a20b4fa04edac74e6a4fec23dfe`.
- Forge Neo Infinite Image Browsing is installed at fixed SHA `ced039479c2e1463c9bdb136d355e01b3dfc9279`.
- PNG metadata can trace actual Prompt / Negative / Seed / Steps / CFG / Sampler / Size / Model / Version.
- Existing WD14 Tagger is installed.
- Codex Windows UI helper is known-good with `[windows] sandbox = "unelevated"`.

## Hard boundaries

- Do not update Forge Neo, Stability Matrix, Python, Torch, CUDA, Gradio, or any extension.
- Do not install Agent Scheduler or any new comparison extension.
- Do not POST global model/settings changes through `/sdapi/v1/options`.
- Do not API-switch checkpoint/model family in this dry run.
- Keep one already-working model family/checkpoint loaded for the entire run.
- Do not change persistent Forge Neo settings merely to make the test pass.
- Do not start Stage10 production A/B or use Special2788 production verdicts.
- Do not add a custom runner/GUI/harness before proving a concrete gap.
- One-off PowerShell/Python commands for API calls and evidence extraction are allowed; do not commit them as production code unless a gap is proven.

## Phase 0 — read-only runtime inventory

Record without changing settings:

1. Current Forge Neo version/commit if observable.
2. Current launch args and whether API endpoints are already reachable.
3. Current loaded checkpoint/model family; keep it fixed.
4. Current known-good generation settings from the latest Issue #6 baseline PNG or current UI metadata:
   - Negative Prompt
   - Steps
   - CFG
   - Sampler / Scheduler
   - width / height
   - batch size = 1
   - any LoRA actually present in the baseline
5. Confirm existing endpoints when API is reachable:
   - `GET /sdapi/v1/options` — read only
   - `GET /sdapi/v1/samplers`
   - `GET /sdapi/v1/schedulers`
   - `GET /tagger/v1/interrogators`

If the Forge API is not reachable and enabling it would require a persistent configuration change, stop with `BLOCKED_API_DISABLED` and report exactly what is required. A temporary one-session launch argument is acceptable only if it does not alter persistent settings and does not disturb another active Forge process.

## Phase 1 — harmless fixed-seed A/B generation

Use a deliberately simple non-production pair whose only intended difference is pose:

- Prompt A: `1girl, solo, standing, looking at viewer, simple background`
- Prompt B: `1girl, solo, sitting, looking at viewer, simple background`

Use:

- Seed: `5072`
- Batch size: `1`
- Same loaded checkpoint/model for A and B
- Same Negative Prompt / Steps / CFG / Sampler / Scheduler / size / LoRA state as the known-good baseline
- No highres fix, random prompt expansion, Dynamic Prompts variation, ADetailer, Forge Couple, or other optional script unless it was explicitly part of the known-good baseline; prefer OFF for comparison modifiers

Call `POST /sdapi/v1/txt2img` once for A and once for B.

Save the returned images into an isolated local TEMP evidence directory, **not GitHub**. Record:

- absolute local path
- SHA-256 of each PNG
- API request parameters used
- API response success/failure
- elapsed time if easily available

Do not rely only on request JSON as the actual Prompt record; inspect the generated PNG metadata next.

## Phase 2 — actual PNG metadata traceability

For A and B, use the saved PNG and `POST /sdapi/v1/png-info` or direct PNG metadata read to extract the actual generation record.

Required fields to confirm for each image:

- actual positive Prompt
- actual Negative Prompt
- Seed
- Steps
- CFG
- Sampler
- Scheduler when available
- width / height
- Checkpoint / Model identifier
- Forge version when available
- LoRA information when present

Compare A vs B and verify that, apart from the intended prompt pose term, controlled generation settings are identical.

If a required field is missing, do not invent it. Record `METADATA_GAP` with the exact missing field.

## Phase 3 — WD14 API first-pass evidence

The installed WD14 Tagger exposes:

- `GET /tagger/v1/interrogators`
- `POST /tagger/v1/interrogate`

The interrogation request accepts base64 image, model, threshold, queue, and name. Use single-response mode (`queue=""`, `name_in_queue=""`).

1. Read available interrogator model names.
2. Use the currently configured/known-working interrogator when determinable without changing settings. If it is not determinable, use one returned model for this dry run and record the exact name; do not persist a default change.
3. Interrogate A and B.
4. For this plumbing test, collect raw confidence evidence; no production winner logic.
5. At minimum record confidences when available for pose-related or obviously relevant tags such as `standing`, `sitting`, `solo`, `1girl`, and any top returned tags.
6. If an expected tag is absent, record absence only. **Do not equate absence with image failure.**

Because WD14 vocabulary/coverage is incomplete for rare Special concepts, this task must preserve a `REVIEW` path by design.

## Phase 4 — verdict for the dry-run infrastructure only

This is **not** a Stage10 image-quality verdict.

Produce one infrastructure verdict:

- `PASS` — A and B generated through API, saved, actual metadata traced, WD14 response obtained, controlled settings matched, and no forbidden persistent changes occurred.
- `PASS_WITH_NOTE` — the full path worked but a non-blocking metadata/tagger limitation was observed.
- `BLOCKED` — API/Tagger/runtime could not complete without prohibited changes.
- `FAIL` — the path ran but controlled settings or image/metadata correspondence was wrong.

Do not emit `A_WIN` or `B_WIN` as a production decision in this first dry run. If pose evidence obviously favors one prompt, record it only as diagnostic evidence, not a Stage10 winner.

## Evidence to write to repository

Create after execution:

1. `docs/testing/ISSUE30_AUTOMATION_DRY_RUN_20260908.md`
   - environment/runtime inventory
   - exact A/B parameters
   - endpoint results
   - PNG hashes and local paths
   - metadata comparison
   - WD14 interrogator name and selected confidences
   - manual operations count
   - persistent-setting change check
   - final infrastructure verdict
   - limitations / next gap

2. `docs/testing/ISSUE30_AUTOMATION_DRY_RUN_20260908.json`
   - machine-readable equivalent
   - no embedded PNG/base64 blobs
   - local image paths + SHA-256 only

If raw API responses are large, keep them local and record their local paths + hashes rather than committing huge payloads.

## Manual-operations measurement

Count how many user actions were required after Forge Neo was already open/ready. Separate:

- actions required only because this is a diagnostic run
- actions that Stage10 would require every experiment

The goal is to identify the remaining automation gap, not to justify custom code prematurely.

## Stop conditions

Stop and report before changing anything further if:

- API is unavailable and only persistent reconfiguration would enable it
- current loaded model/checkpoint differs unexpectedly and restoring it is ambiguous
- generation would require updating dependencies/extensions
- WD14 endpoint is missing/broken and fixing it requires update/reinstall
- another active task owns the external Forge runtime
- any step would modify protected/data dictionary assets

## Completion / next decision

After the dry run:

- If native Forge API + WD14 API already cover generation, metadata, and first-pass evidence, keep Agent Scheduler `HOLD` and identify only the smallest missing orchestration glue.
- If queue/history/result retrieval is a demonstrated blocker, document that exact gap before re-reviewing Agent Scheduler.
- If no code gap is demonstrated, do not create a custom runner.
- Return results to Issue #30 and then hand the stable operating constraints to Issue #5 for formal Stage10 Prompt handoff.
