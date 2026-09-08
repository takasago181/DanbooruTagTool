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

## API retry after user restart — 2026-09-08

The user relaunched Forge Neo from Stability Matrix with Extra Launch Arguments `--api` and no `--listen`. The API gate was rechecked before any generation:

- API-enabled Forge port `7861`: `/` 200, `/openapi.json` 200, `/sdapi/v1/options` 200, `/sdapi/v1/samplers` 200, `/sdapi/v1/txt2img` route present, `/sdapi/v1/png-info` route present, `/tagger/v1/interrogators` 200.
- Read-only `/sdapi/v1/options` confirmed checkpoint `sd\\waiIllustriousSDXL_v170.safetensors` and hash `f116b0c78ff441467b0cdc8f1936e1ed18ea31e9997c7b132b1b8db533f0bd04`.
- The original Forge port `7860` remained alive with the non-API UI and continued to return `/sdapi/v1/options` 404.
- Two same-package Forge Python processes were therefore alive concurrently: old PID `20508` on `7860`, and restarted API PID `36452` on `7861` (both `...\\Stable Diffusion WebUI Forge - Neo\\venv\\Scripts\\python.exe`).

Because the task forbids a concurrent second model-loaded Forge process, no `/sdapi/v1/txt2img` POST was sent. No `/sdapi/v1/options` POST, model switch, checkpoint change, dependency change, Agent Scheduler action, Stage10 production comparison, winner rule, or scoring action was performed.

- A/B PNG paths and SHA-256: none; generation withheld
- actual PNG metadata: not run
- WD14 POST/raw confidence: not run; interrogator GET was only a read-only gate
- user manual operations during this retry: `0`
- Codex Forge UI input operations: `0`
- HTTP/API operations: read-only GET probes only; generation and WD14 POST count `0`
- normal launch restoration: not applicable; the user's API-enabled session remains running and the old non-API session also remains running

Retry infrastructure verdict: **`BLOCKED_RESTART_CONTROL`**. The next retry requires the old `7860` session to be normally stopped so that only the API-enabled Forge process remains.

## Successful API pipeline attempt — 2026-09-08

The user explicitly authorized termination of PID `20508` only. Preconditions matched: it was the old Forge Neo package process, held port `7860`, returned `/sdapi/v1/options` 404, and its UI was idle. PID `20508` was terminated; the API Forge PID `36452` was not touched.

Post-termination checks:

- PID `20508`: gone
- port `7860`: no response (`HTTP 000`)
- PID `36452`: still running
- port `7861`: HTTP 200
- `GET /sdapi/v1/options`: HTTP 200
- same Forge package model-loaded process count: `1` (`36452`)
- checkpoint: `sd\\waiIllustriousSDXL_v170.safetensors`
- checkpoint hash: `f116b0c78ff441467b0cdc8f1936e1ed18ea31e9997c7b132b1b8db533f0bd04`

### Fixed A/B generation

API base: `http://127.0.0.1:7861`

- Prompt A: `1girl, solo, standing, looking at viewer, simple background`
- Prompt B: `1girl, solo, sitting, looking at viewer, simple background`
- Negative Prompt: `lowres, blurry, bad anatomy, text, watermark`
- Seed: `5072`
- Steps: `24`
- CFG: `4.5`
- Sampler: `Euler a`
- Scheduler: `Automatic`
- Size: `1024x1024`
- Batch count/size: `1/1`
- LoRA: none
- Checkpoint/model: `waiIllustriousSDXL_v170` / `f116b0c78f`

Local non-production evidence directory:

`C:\Users\takas\AppData\Local\Temp\issue30_api_resume_20260908_20260908_204210`

| Image | PNG path | SHA-256 | Generation time |
|---|---|---|---:|
| A | `C:\Users\takas\AppData\Local\Temp\issue30_api_resume_20260908_20260908_204210\image_A.png` | `6450E42A957D6B7AA94D7DAE61159CA6D0ADFFE53EEEDBD5ABEAA63FB9757099` | 11.113 s |
| B | `C:\Users\takas\AppData\Local\Temp\issue30_api_resume_20260908_20260908_204210\image_B.png` | `4A0FC8F6EB0120EC9F8B3287CA0CB4435AD433FEB64BC0A54CFAB31304D6AFC4` | 7.211 s |

### Actual PNG metadata

`POST /sdapi/v1/png-info` returned actual PNG infotext for both images. A/B differed only in the intended positive Prompt pose term; controlled generation fields matched.

- A metadata file: `...\\png_info_A.json`, SHA-256 `DAC57D44634F0F2B58DF7C8AB43B88D56D74FAFBB73F4581EFA5098C45862A04`
- B metadata file: `...\\png_info_B.json`, SHA-256 `7272C38FAA622CBBBC34C5BFE81E808B880EC7CCBA699ADF7D3B1BD7705C8D0B`
- A actual Prompt: `1girl, solo, standing, looking at viewer, simple background`
- B actual Prompt: `1girl, solo, sitting, looking at viewer, simple background`
- Both actual Negative Prompt: `lowres, blurry, bad anatomy, text, watermark`
- Both actual Seed/Steps/CFG: `5072 / 24 / 4.5`
- Both actual Sampler/Scheduler: `Euler a / Automatic`
- Both actual Size: `1024x1024`
- Both actual Model/Hash: `waiIllustriousSDXL_v170 / f116b0c78f`
- Both Forge version: `neo-2.29`
- LoRA metadata: none

### WD14 raw confidence

Model: `wd14-eva02.v3.large`; threshold: `0.0`; `queue=""`; `name_in_queue=""`.

- A raw response: `...\\wd14_raw_A.json`, SHA-256 `1DE4828F1DB3DE55F0105FA9BD7DC3928E04E168E276F1DB6057F3FF087992BF`; tag confidence entries `10840`.
- B raw response: `...\\wd14_raw_B.json`, SHA-256 `1B2498D260A63F27D3A7B1EB85F67BF4A303C4FD9D9F9B13D2B0125553FBEFF0`; tag confidence entries `10844`.

Selected raw values are diagnostic evidence only:

| Tag/rating | A | B |
|---|---:|---:|
| `1girl` | 0.992265761 | 0.996757150 |
| `solo` | 0.985705853 | 0.981036961 |
| `standing` | 0.803452671 | 0.009758145 |
| `sitting` | 0.001002163 | 0.930249333 |
| `looking_at_viewer` | 0.810943841 | 0.975347757 |
| `simple_background` | 0.893245935 | 0.863955498 |

No winner, scoring, or production verdict was derived from these values.

### Manual-operation measurement and verdict

- User manual operations after task start: `0`
- Forge UI input operations by Codex: `0`
- One-time authorized old-process termination: `1`
- HTTP/API generation POSTs: `2`
- PNG metadata POSTs: `2`
- WD14 POSTs: `2`
- `/sdapi/v1/options` POSTs: `0`
- API Forge stop/restart or model switch: `0`
- Persistent settings/dependencies/extensions changed: no

Final infrastructure verdict: **`PASS_PIPELINE`**.

This PASS covers the non-production plumbing only. `A_WIN`, `B_WIN`, `REVIEW`, production scoring, golden-set validation, and Stage10 production A/B remain unexecuted.
