# 07 — WAI17 Local Test Profile

Status: `CURRENT_FIRST_TEST_PROFILE`

## Purpose

現在のあなたの実環境で、まず WAI Illustrious v17 を使って知識を実証するための最短入口。

詳細原本:
`../research/WAI17_LOCAL_ENV_TEST_BASELINE_20260909.md`

## Exact author baseline

- UI: Forge Neo recommended
- Sampler: Euler a
- Steps: 15–30
- CFG: 5–7
- VAE integrated
- original area larger than 1024×1024 recommended; examples 1024×1344
- minimal quality: `masterpiece, best quality, amazing quality`
- minimal Negative: `bad quality, worst quality, worst detail, sketch, censor`
- too many quality/aesthetic tags and overly long Negative can reduce quality/blur
- Hires may repair limbs/hands/feet; therefore base and Hires are separate evidence states

## Current local test baseline

- Forge Neo
- WAI Illustrious v17
- Euler a
- Steps 25
- CFG 5
- portrait: 1024×1344 first candidate when appropriate
- fixed paired seeds
- Hires OFF
- ADetailer OFF
- LoRA OFF
- ControlNet / regional / Forge Couple OFF

The goal of this baseline is not maximum prettiness. It is to isolate Prompt/Special behavior.

## First test order

1. target Special minimal
2. minimum actor/count identity if needed
3. one visibility support if judging target is impossible
4. one geometry/binding support if relation is wrong
5. canonical vs known Alias/alternate surface only as a controlled comparison
6. broad+specific as a separate A/B
7. anatomy/count Negative OFF/ON when overlap is plausible
8. predetermined multi-seed repeatability
9. only then add a second hard Special
10. assisted-control lane only after bounded Prompt-only attempts

## What counts as separate evidence

- base Prompt-only result
- Hires result
- ADetailer/inpaint result
- LoRA-assisted result
- Control/regional-assisted result

Do not collapse these into one `success` state.

## WAI17 current HOLD

- canonical vs Alias activation
- rare Special exposure
- broad+specific benefit/harm
- actor-target/body-site relation ceiling
- restraint topology
- machine/device functional relation
- tentacle source/ownership
- exact count / simultaneous-Special ceiling
- visibility support effect
- unusual anatomy/count Negative ON/OFF
- LoRA × Special/support interaction
- Prompt-only -> assisted-control threshold

## Related catalog

- `01_MODEL_FAMILIES.md`
- `02_PROMPT_SUPPORT_AND_COMPOSITION.md`
- `03_FAILURE_TESTING_AND_EVALUATION.md`
- `04_TOOLS_POSTPROCESS_AND_LORA.md`
- `05_HARD_NICHE_ADULT_GENERATION.md`
- `09_OPEN_QUESTIONS_AND_HOLD.md`