# Issue #30 Forge Neo A/B automation dry run — 2026-09-08

## Scope and verdict

This was a non-Stage10-production plumbing dry run from the dedicated Issue #30 worktree. No production winner/scoring rule was established and no Special2788 production verdict was emitted.

Final infrastructure verdict: **BLOCKED** (`BLOCKED_API_DISABLED`)

The existing Forge Neo UI was reachable, but the Forge generation API required by the task was not exposed. Enabling it would require a controlled restart or launch-argument change; neither was performed because the existing Forge process was active and the task forbids persistent reconfiguration or disturbing another active runtime.

## Repository/task context

- Latest fetched `origin/main`: `cc87387928265ebc2dce659f1db07d0546163aa5`
- Local `main`: fast-forwarded to `cc87387928265ebc2dce659f1db07d0546163aa5`
- Task branch: `codex/issue30-automation-dry-run-20260908`
- Worktree: `C:\Codex\DanbooruTagTool\.worktrees\issue30-automation-dry-run-20260908`
- Isolation: `CURRENT_DEV_TASK.md`, `danbooru_tag_tool/ui.py`, `tests/test_stage7a_ui.py`, `validation_quarantine/**`, and `data/**` were not edited.

## Phase 0 — runtime inventory

Observed through the already-open local Forge Neo UI and read-only local files:

- Forge Neo version: `neo-2.29`
- Forge Neo package commit: `efc42fe03739d0d8cda7de6e7bed2f8c1969a0c7` on branch `neo`
- Python: `3.13.15`
- Torch: `2.11.0+cu130`
- Gradio: `4.40.0`
- Loaded checkpoint: `sd\\waiIllustriousSDXL_v170.safetensors`
- Model identifier: `waiIllustriousSDXL_v170`
- Model hash: `f116b0c78f`
- Prompt shown in current UI: `1girl, portrait, simple background, soft lighting`
- Negative Prompt shown in current UI: `lowres, blurry, bad anatomy, text, watermark`
- Steps: `24`
- CFG: `4.5`
- Sampler: `Euler a`
- Scheduler: `Automatic`
- Size: `1024x1024`
- Batch count: `1`
- Batch size: `1`
- Seed shown in current UI: `5072`
- Optional comparison modifiers observed: Hires. fix, Refiner, ADetailer, Dynamic Prompts, Forge Couple, ControlNet, ImageStitch, Spectrum, Torch Compile, and other script slots were off/none for the visible baseline.
- Launch argument file: `webui-user.bat` contains `set COMMANDLINE_ARGS=`; no `--api` argument is present.

The package already had a pre-existing unrelated working-tree modification in `models/VAE/Put VAE here.txt`; it was not touched.

## Endpoint inventory

Base URL: `http://127.0.0.1:7860`

| Endpoint | Result | Interpretation |
|---|---:|---|
| `GET /` | HTTP 200 | Forge UI reachable |
| `GET /openapi.json` | HTTP 200 | Gradio/OpenAPI surface reachable |
| `GET /sdapi/v1/options` | HTTP 404 | Forge API route unavailable |
| `GET /sdapi/v1/samplers` | HTTP 404 | Forge API route unavailable |
| `GET /sdapi/v1/schedulers` | HTTP 404 | Forge API route unavailable |
| `POST /sdapi/v1/txt2img` | not sent | Blocked before generation because the route is unavailable |
| `GET /tagger/v1/interrogators` | HTTP 200 | WD14 endpoint reachable |
| `GET /tagger/v1/interrogate` | HTTP 405 | Interrogate route exists; method requires POST |

The OpenAPI route list contained the WD14 routes but no `/sdapi/v1/*` routes. This is the decisive API-disabled evidence.

## Phase 1 — fixed-seed A/B generation

Planned harmless pair:

- A: `1girl, solo, standing, looking at viewer, simple background`
- B: `1girl, solo, sitting, looking at viewer, simple background`
- Seed: `5072`
- Batch size: `1`
- Remaining settings: the fixed baseline inventory above

Status: **NOT RUN**. No `POST /sdapi/v1/txt2img` was issued.

Generated PNGs: none.

PNG local paths and SHA-256: none.

## Phase 2 — PNG metadata traceability

Status: **NOT RUN** because no PNG was generated through the required API path.

- Actual positive Prompt: unavailable
- Actual Negative Prompt: unavailable
- Seed / Steps / CFG / Sampler / Scheduler: unavailable from a dry-run PNG
- Size / checkpoint / Forge version / LoRA: unavailable from a dry-run PNG

The visible current UI baseline was used only as read-only inventory and is not claimed as generated evidence for the requested A/B pair.

## Phase 3 — WD14 first-pass evidence

`GET /tagger/v1/interrogators` succeeded. The available interrogator names were:

```text
wd14-vit.v1
wd14-vit.v2
wd14-convnext.v1
wd14-convnext.v2
wd14-convnextv2.v1
wd14-eva02.v3.large
wd14-swinv2-v1
wd-v1-4-moat-tagger.v2
wd-v1-4-vit-tagger.v3
wd14-vit.v3.large
wd-v1-4-convnext-tagger.v3
wd-v1-4-swinv2-tagger.v3
mld-caformer.dec-5-97527
mld-tresnetd.6-30000
Z3D-E621-Convnext
```

- Available model count: `15`
- Selected model: none (no generated image and no persistent default change)
- A interrogation: not run
- B interrogation: not run
- Raw confidence evidence: none
- REVIEW-safe path: preserved by stopping before any unsupported image-quality inference

## Manual-operation measurement

- User actions required after Forge was already open/ready for this diagnostic attempt: `0`
- Diagnostic-only UI actions: `0` (the UI was observed read-only)
- Stage10-per-experiment manual actions: not measurable because the API-disabled stop condition occurred before generation
- API/WD14 calls performed: read-only endpoint probes only

## Persistent-setting change check

- Forge settings changed: no
- `/sdapi/v1/options` POST: no
- model/checkpoint switch: no
- extension/dependency/update/install: no
- Forge restart or second Forge process: no
- repository protected paths changed: no

## Infrastructure decision and next gap

Decision: **BLOCKED**. The native Forge UI and WD14 API are present, but the required Forge generation API is disabled in the active runtime. Agent Scheduler remains **HOLD**; no custom runner/harness was justified.

Smallest next gap: provide a controlled, non-concurrent Forge Neo session launched with a temporary `--api` argument (or an already API-enabled runtime), without changing persistent settings. Then repeat only Phase 1–3 and record the A/B PNG hashes, actual metadata, and WD14 POST responses.

This result is infrastructure-only and must not be treated as Stage10 production A/B evidence.
