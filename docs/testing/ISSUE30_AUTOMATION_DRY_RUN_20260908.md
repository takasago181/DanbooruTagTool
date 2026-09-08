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

## API-enabled resume attempt — 2026-09-08

The API-resume task specification was brought in from latest `origin/main` at `6e381a30a111adb218f3236a4912e8adc6b6bcb6`. The prior evidence commit `5e0a821cf23c8405c443b625a0e89849b5c10ea6` remains in this branch's history.

### Pre-shutdown capture

- Existing Forge UI: idle; no generation was running.
- Existing Forge process: PID `20508`
- Process path: `C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Packages\Stable Diffusion WebUI Forge - Neo\venv\Scripts\python.exe`
- Process start: `2026-09-08 19:14:45`
- Main window handle: `0`; no controllable native process window was exposed.
- Package: Forge Neo `neo-2.29`, package commit `efc42fe03739d0d8cda7de6e7bed2f8c1969a0c7`
- URL/port: `http://127.0.0.1:7860`
- Loaded checkpoint: `waiIllustriousSDXL_v170`, hash `f116b0c78f`
- Fixed baseline: Seed `5072`, Steps `24`, CFG `4.5`, Euler a, Automatic, `1024x1024`, batch count/size `1/1`
- `webui-user.bat` SHA-256 before attempted resume: `F5AE1B180E7FDF72BDD6EA6DB57D529BCEE7B0B32D6A31B396D82356652D19AA`
- `config.json` SHA-256 before attempted resume: `1FCD5EACA58DABF87A62C9317A257D9A765CC5E168329453FC7C937BA319E3C4`
- Current endpoint probe: `/` 200, `/openapi.json` 200, `/sdapi/v1/options` 404, `/tagger/v1/interrogators` 200.

### Stop result

The required normal close could not be performed safely:

- `CloseMainWindow()` was attempted on the exact package PID and returned `False` because the process has no main window (`handle=0`).
- No Forge shutdown/restart endpoint was exposed; only unrelated reload/shutdown routes were present in the Gradio/OpenAPI surface.
- No force-kill, `taskkill`, concurrent second Forge process, persistent setting edit, or dependency change was performed.
- The one-shot command `webui.bat --api` was **not executed**.
- The existing normal non-API Forge session remains running; it was neither restarted nor left stopped by this attempt.
- A/B generation, PNG metadata extraction, WD14 POST, and raw confidence capture were **not executed**.

Resume-attempt infrastructure verdict: **`BLOCKED_RESTART_CONTROL`**.

The temporary API session must be retried only after the user/Forge owner provides a controllable normal-close path or confirms a safe stop mechanism for this exact process. The expected command remains `webui.bat --api` from the verified Forge package directory; it was not run in this attempt.
