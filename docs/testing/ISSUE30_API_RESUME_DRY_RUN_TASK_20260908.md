# Issue #30 API-enabled resume dry run task — 2026-09-08

## Purpose

Continue the already-verified non-production Issue #30 Forge Neo A/B automation dry run after the first attempt correctly stopped at `BLOCKED_API_DISABLED`.

This task is infrastructure validation only. It is **not Stage10 production A/B**, does not establish a winner/scoring rule, and must not modify DanbooruTagTool production semantics, dictionaries, protected data, or Issue #35-owned files.

## Verified starting point

Previous remote evidence branch:
- `codex/issue30-automation-dry-run-20260908`
- verified evidence commit: `5e0a821cf23c8405c443b625a0e89849b5c10ea6`

Previous result:
- Forge Neo UI reachable on `127.0.0.1:7860`
- Forge generation API absent: `/sdapi/v1/*` returned 404
- WD14 API present: `/tagger/v1/interrogators` returned 200
- active runtime launch file had no `--api`
- no generation / no persistent setting change / no restart was performed
- verdict: `BLOCKED_API_DISABLED`

Exact local Forge source observed:
- Forge Neo `neo-2.29`
- package commit `efc42fe03739d0d8cda7de6e7bed2f8c1969a0c7`

The exact Forge source at that commit defines `--api` as a supported launch flag, and `webui.bat` forwards command-line arguments to `launch.py`. Therefore a one-shot API-enabled launch can be attempted without editing `webui-user.bat` or persistent Forge settings.

## Repository isolation / start gate

1. Fetch latest `origin/main`.
2. Continue on the existing Issue #30 branch `codex/issue30-automation-dry-run-20260908`.
3. Bring latest `origin/main` into that branch without force-push or dropping the previous evidence commit.
4. Confirm previous evidence commit `5e0a821cf23c8405c443b625a0e89849b5c10ea6` remains in history.
5. Do not edit:
   - `docs/project/CURRENT_DEV_TASK.md`
   - `danbooru_tag_tool/ui.py`
   - `tests/test_stage7a_ui.py`
   - `data/**`
   - `validation_quarantine/**`
   - protected/hash validation
6. Do not touch Issue #35 implementation state.

If branch/history isolation cannot be preserved, stop with `BLOCKED_REPO_ISOLATION`.

## Hard environment boundaries

Do **not**:
- edit `webui-user.bat`
- persist `--api` into launch settings
- update Forge Neo / Stability Matrix / extensions
- install or upgrade dependencies
- change Torch / CUDA / Python / Gradio / xformers / VRAM / attention settings
- switch checkpoint/model family through `/sdapi/v1/options`
- change the baseline checkpoint
- use Agent Scheduler
- create a custom runner/GUI
- run Stage10 production Prompt comparisons

Keep the already-working model/checkpoint fixed for the entire run.

## Controlled one-shot API launch

### A. Pre-shutdown capture

Before stopping the current Forge process:
- confirm no generation is currently running
- record the current Forge PID, process command line where available, working directory/package path, URL/port, loaded checkpoint, Seed, Steps, CFG, Sampler, Scheduler, size, batch count/size
- record SHA-256 of `webui-user.bat` and `config.json` before the test

If a generation is active, do not interrupt it. Wait until idle and re-check.

### B. Stop the existing Forge session

Prefer a normal/controlled close of the existing Forge process/window.

Do not run a concurrent second Forge model-loaded process.

If Codex cannot stop the existing session without a force-kill or ambiguous process targeting, stop and report `BLOCKED_RESTART_CONTROL` rather than killing an uncertain process.

### C. Start one-shot API-enabled Forge

From the exact verified Forge package directory, launch the same Forge package with a temporary command-line argument only:

```text
webui.bat --api
```

Do not edit `webui-user.bat` to achieve this.

If the local Stability Matrix packaging requires a different executable wrapper to preserve the verified environment, use the same verified package/environment and append only `--api`; document the exact command. Do not substitute another Forge checkout.

Wait until the UI is ready and the same checkpoint is loaded.

### D. API gate

Require all of the following before generation:
- `GET /` -> 200
- `GET /openapi.json` -> 200
- `/sdapi/v1/txt2img` route present in OpenAPI
- `GET /sdapi/v1/options` -> 200
- `GET /sdapi/v1/samplers` -> 200
- `GET /tagger/v1/interrogators` -> 200

If the Forge API is still absent, stop with `BLOCKED_API_STILL_DISABLED` and do not mutate settings.

## Phase 1 — harmless fixed-seed A/B generation

Use the already-fixed non-production pair:

A:
```text
1girl, solo, standing, looking at viewer, simple background
```

B:
```text
1girl, solo, sitting, looking at viewer, simple background
```

Fixed settings:
- checkpoint/model: keep currently loaded `waiIllustriousSDXL_v170`
- Negative Prompt: `lowres, blurry, bad anatomy, text, watermark`
- Seed: `5072`
- Steps: `24`
- CFG: `4.5`
- Sampler: `Euler a`
- Scheduler: `Automatic`
- Size: `1024x1024`
- Batch size: `1`
- Batch count: `1`
- LoRA: none

Use `/sdapi/v1/txt2img` for A and B. Do not POST `/sdapi/v1/options` and do not switch models through API.

Save each returned/generated PNG into a clearly isolated non-production evidence directory and record:
- exact local path
- SHA-256
- A/B condition
- API request payload excluding redundant/default fields
- API response generation info

## Phase 2 — metadata traceability

For both A and B, verify actual generation metadata using the returned info and/or `/sdapi/v1/png-info` / PNG infotext.

Record at minimum:
- actual positive Prompt
- actual Negative Prompt
- Seed
- Steps
- CFG
- Sampler
- Scheduler when available
- width/height
- checkpoint/model + hash when available
- Forge version
- LoRA state

Pass only if the two images can be unambiguously mapped to their A/B condition and the actual used Prompt/settings are traceable.

## Phase 3 — WD14 API evidence

Use the already-installed WD14 Tagger API.

1. Confirm `GET /tagger/v1/interrogators` remains 200.
2. Use model `wd14-eva02.v3.large` if present; otherwise stop and report the available model list without substituting a different model silently.
3. POST each generated image to `/tagger/v1/interrogate`.
4. Use threshold `0.0` for this plumbing validation so raw available confidences are preserved.
5. Save machine-readable WD14 response for A and B.

Do **not** create an A/B winner rule yet.
Do **not** equate missing tags with image failure.
This phase only proves that image -> WD14 confidence data can be automated.

## Phase 4 — infrastructure verdict and manual-operation measurement

Allowed infrastructure verdicts:
- `PASS_PIPELINE`
- `BLOCKED_API_STILL_DISABLED`
- `BLOCKED_RESTART_CONTROL`
- `BLOCKED_GENERATION`
- `BLOCKED_METADATA`
- `BLOCKED_WD14`
- `BLOCKED_REPO_ISOLATION`

`PASS_PIPELINE` requires:
- API-enabled Forge launch succeeded without persistent launch-setting edits
- A and B both generated at Seed 5072 with the fixed baseline
- PNG paths and SHA-256 recorded
- actual Prompt/settings metadata traceable for both
- WD14 POST succeeded for both and raw machine-readable confidences were saved
- no model switching, dependency update, or protected-path modification occurred

Measure separately:
- user manual operations required after Codex task start
- Codex UI/console operations
- HTTP/API calls
- any unavoidable one-time restart action

Do not claim a Stage10-per-experiment automation count yet beyond what this plumbing run demonstrates.

## Restore / finish

After evidence is complete:
- stop the temporary API-enabled Forge session using a controlled close
- verify `webui-user.bat` and `config.json` SHA-256 still match the pre-test hashes
- do not persist `--api`
- if safe/available, restore the normal non-API Forge launch state; otherwise leave Forge stopped and state that explicitly rather than changing persistent settings

## Evidence files

Update/append the existing Issue #30 evidence rather than erasing the first blocked attempt. Preserve the historical `BLOCKED_API_DISABLED` attempt and add a clearly dated/resume section.

At minimum update:
- `docs/testing/ISSUE30_AUTOMATION_DRY_RUN_20260908.md`
- `docs/testing/ISSUE30_AUTOMATION_DRY_RUN_20260908.json`

The JSON should retain the first attempt and add a second-attempt/resume record rather than pretending the original blocker never happened.

## Required completion report

Return:
- remote branch
- final commit SHA
- latest `origin/main` used
- exact one-shot Forge launch command
- whether normal launch was restored or Forge was left stopped
- A/B PNG paths + SHA-256
- API generation result summary
- metadata traceability result
- WD14 model + raw-response evidence paths/summary
- manual operation counts
- changed repository files
- explicit confirmation forbidden/protected paths unchanged
- final infrastructure verdict
- remaining gap before `A_WIN / B_WIN / REVIEW / BLOCKED` logic can be dry-run

Do not call Issue #30 complete solely from `PASS_PIPELINE`; automatic verdict routing/golden-set validation remains a separate next step.