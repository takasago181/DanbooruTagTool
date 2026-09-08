# Issue #6 Forge Neo preflight execution checkpoint (2026-09-08)

## Scope

This resumes only the previously unverified GUI-dependent checks after the Windows UI helper was resolved under `[windows] sandbox = "unelevated"`. The run used the existing Forge Neo installation and the existing Japanese UI. No extension install/update, model install/change, Forge setting change, or source/protected-data modification was performed. The Luna boundary was preserved; no model-family prompt grammar was generalized.

Source checkpoints read:

- `docs/testing/ISSUE6_UI_HELPER_UNELEVATED_SMOKE_20260908.md`
- `docs/testing/ISSUE6_PREFLIGHT_RESUME_20260908.md`
- `docs/testing/ISSUE6_PNG_METADATA_RECHECK_20260908.md`
- `docs/stages/STAGE_10_PREP.md`

## Forge Neo environment

- URL: `http://127.0.0.1:7860/`
- UI language: Japanese (`日本語`)
- checkpoint: `sd\\waiIllustriousSDXL_v170.safetensors`
- Forge Neo footer: `neo-2.29`; Python `3.13.15`; torch `2.11.0+cu130`; Gradio `4.40.0`

## Existing five-extension baseline

The five extensions named by the prior checkpoint were present and checked/enabled in the installed-extension UI during this run:

1. `ADetailer-Neo` — `67e973e1`
2. `sd-dynamic-prompts` — `3e624527`
3. `sd-forge-couple` — `c7884e81`
4. `sd-webui-tagcomplete-neo` — `21ed5859`
5. `stable-diffusion-webui-wd14-tagger` — `ce1b3e31`

An additional pre-existing checked extension, `sd-webui-language-diffusion` (`00cde72e`), was also observed. Nothing was enabled, disabled, installed, or updated by this run.

## Normal txt2img generation (one image)

The Japanese txt2img UI generated one image successfully with the existing checkpoint and the following fixed inputs:

- positive: `1girl, portrait, simple background, soft lighting`
- negative: `lowres, blurry, bad anatomy, text, watermark`
- seed: `5072`
- steps: `24`
- sampler/schedule: `Euler a` / `Automatic`
- CFG: `4.5`
- size/batch: `1024x1024`, batch count `1`, batch size `1`
- UI-reported time: `15.6 sec`
- UI metadata: model `waiIllustriousSDXL_v170`, model hash `f116b0c78f`, RNG `CPU`, version `neo-2.29`

Output: `C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Images\Text2Img\2026-09-08\00001-5072.png`\
SHA-256: `254DF727AE21E9A90BFDD94CED46C41569ECFC6B7E69EDDCE5333595E3FC11DE`\
PNG: `1024x1024`, `1,265,780` bytes. The `parameters` metadata contains the prompt, negative prompt, fixed seed, sampler, steps, CFG, size, model, and version.

## Fixed-seed X/Y/Z operation

The built-in `X/Y/Z plot` script was selected and executed through the UI with:

- base Seed `5072`;
- X type `CFG Scale`;
- X values `4.5,5.0`;
- Y type `Nothing`;
- Z type `Nothing`.

The UI gallery exposed only the selected thumbnail, but the actual saved outputs prove the plot executed. Two CFG variants were written per run; a second identical smoke invocation produced a duplicate pair:

| File | CFG metadata | Seed | SHA-256 |
|---|---:|---:|---|
| `00002-5072.png` | 4.5 | 5072 | `4CE95A2C61182A2BC9B18F736EF8189EE349CB771BA74D84C65A33DDB8B63819` |
| `00003-5072.png` | 5.0 | 5072 | `3B1F56ACF542970A46B4218421AD42C2D175B5F706DF33A42CFC1F7D00433EF4` |
| `00004-5072.png` | 4.5 | 5072 | `4CE95A2C61182A2BC9B18F736EF8189EE349CB771BA74D84C65A33DDB8B63819` |
| `00005-5072.png` | 5.0 | 5072 | `3B1F56ACF542970A46B4218421AD42C2D175B5F706DF33A42CFC1F7D00433EF4` |

Latest PNG: `C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Images\Text2Img\2026-09-08\00005-5072.png`\
Last write: `2026-09-08T19:04:22.9711946+09:00` (+09:00)\
Size: `1,255,889` bytes\
SHA-256: `3B1F56ACF542970A46B4218421AD42C2D175B5F706DF33A42CFC1F7D00433EF4`\
Metadata: `1girl, portrait, simple background, soft lighting`; negative prompt as above; `Steps: 24`; `Sampler: Euler a`; `CFG scale: 5.0`; `Seed: 5072`; `Size: 1024x1024`; model `waiIllustriousSDXL_v170`; hash `f116b0c78f`; `Version: neo-2.29`.

## Observed warnings

The browser console reported an existing extension-side JavaScript error:

```text
TypeError: Assignment to constant variable.
at .../extensions/sd-dynamic-prompts/javascript/dynamic_prompting_hints.js:4:8
```

It also reported repeated frontend warnings `Too many arguments provided for the endpoint.` and hidden-tab selection warnings. Despite those warnings, the normal generation and X/Y/Z output files were successfully written with complete metadata. No extension was modified to address the warnings.

## Remaining completion boundary

**Confirmed in this checkpoint:** Japanese Forge Neo UI, checkpoint loading/inference, one-image normal generation, five named existing extensions present and checked, fixed-seed traceability, latest PNG metadata, and built-in X/Y/Z actual output.

**Still not confirmed:** Multi Prompt Slots and Forge Neo Infinite Image Browsing. Neither name was present in the existing extension directory list or Forge Neo package search. Installing or updating them is explicitly out of scope, so these two Issue #6 comparison-environment checks remain HOLD.

## Verdict

Issue #6 is **partially complete / not yet completion-gated**. The requested baseline, metadata, fixed Seed, and X/Y/Z checks pass. The overall Issue #6 completion condition cannot be declared complete because Multi Prompt Slots and Infinite Image Browsing remain unavailable/unverified under the no-install/update boundary.

