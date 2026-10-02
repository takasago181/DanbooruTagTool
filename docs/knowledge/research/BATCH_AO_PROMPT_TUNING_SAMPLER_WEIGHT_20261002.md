# BATCH_AO — Prompt tuning / sampler / weight / seed practical rules — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: author-guidance + practical diagnostic synthesis
Scope: day-to-day prompt tuning for Anima / NoobAI / WAI

## 1. Decide whether the failure is semantic or stochastic

Before changing Prompt:

Generate a small seed set.

If the same failure repeats across seeds:
- wrong count
- wrong identity
- wrong relation
- wrong camera
- missing concept

then change the semantic/control representation.

If semantics are consistently correct and only:
- composition balance
- expression nuance
- small pose variation
- background arrangement
change, explore seeds first.

This reduces the common failure mode of making prompts increasingly rigid to fix one unlucky seed.

Promoted:
- K-PRACTICAL-012
- K-PRACTICAL-014.

## 2. Anima sampler choice changes rendering behavior

Author:
https://huggingface.co/circlestone-labs/Anima

Documented:
- `er_sde`: neutral, flat colors, sharp lines; reasonable default
- `euler_a`: softer/thinner lines; can lean more 2.5D; tolerates somewhat higher CFG
- `dpmpp_2m_sde_gpu`: similar family but more varied/creative; can get wild
- `euler`: basic/creative; useful with more stable Turbo/Aesthetic profiles
- beta57 scheduler can help painterly/realistic texture by emphasizing low-noise timesteps

Practical order:
1. establish subject/scene
2. choose sampler for rendering character
3. then tune CFG/steps

Do not swap sampler while also rewriting Prompt and LoRA weights.

Promoted:
- K-PRACTICAL-010.

## 3. Prompt weighting

Anima author note:
- weights work;
- stronger values than typical SDXL may be required;
- example `(chibi:2)`.

Community fixed-seed transfer test:
https://note.com/ai_on_desk/n/n72f6f4e58dfe

Reported:
- modest SDXL-like weights could have little target effect;
- stronger weight eventually changed the target;
- other image content also moved.

Practical procedure:
1. verify the trigger itself
2. delete synonyms/contradictions
3. same-seed low/medium/high sweep
4. inspect spillover
5. keep minimum sufficient weight

Do not compensate for unknown tags by arbitrarily increasing weight.

Promoted:
- K-PRACTICAL-013.

## 4. Negative prompt minimalism

### WAI v17

Author:
https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md

Explicit warning:
too many quality/aesthetic tags and overly long Negative prompts can reduce quality and make images blurrier.

Practical rule:
start from model-author baseline.
Add targeted Negative terms only for an observed recurring failure.

### Anima

Base author Negative is short.
Aesthetic guidance specifically discourages score_* pressure in positive/negative because the profile is already quality-focused.

### NoobAI

Author baseline exists, but its SFW-oriented content controls need intent-specific handling in adult tests.

Promoted:
- K-PRACTICAL-011.

## 5. Resolution/aspect ratio

NoobAI official:
- target area around 1024×1024
- provides tested portrait/landscape options.

Anima official:
- documented working area from 512² through 1536².

Practical rule:
resolution is not cosmetic:
- portrait gives more vertical room for full-body/two-person stacking
- landscape gives more lateral room for multi-subject separation
- square is useful as a neutral diagnostic condition.

Do not change aspect ratio mid-debug without recording it.

Promoted:
- K-PRACTICAL-015.

## 6. A practical tuning order

When the base image is close but not correct:

1. seed set
2. simplify Prompt conflicts
3. check exact tag/trigger
4. relation/camera wording
5. model-appropriate weight
6. LoRA strength
7. sampler
8. CFG
9. steps
10. structural control
11. finishing

The order is not mathematically mandatory.
Its purpose is to avoid changing many interacting axes before diagnosing the actual failure.

## 7. When to stop adding tags

Stop if:
- target semantics already appear;
- new tags only change unrelated content;
- identity becomes less stable;
- composition gets crowded;
- quality/style becomes muddy.

At that point:
- seed exploration
- control
- regional separation
- reference/inpaint
may be better than longer Prompt.

## 8. Diagnostic seed set vs production seed

### Diagnostic
Fixed small seed set.
Used for:
- A/B
- LoRA sweep
- sampler comparison
- Prompt changes.

### Production
Broader seed search after configuration is accepted.
Used for:
- aesthetic composition selection.

Do not select one beautiful production seed and call it evidence of reliability.

## 9. Practical profile cards

### Anima Base
Start:
- er_sde
- CFG 4–5
- 30–50
Then vary sampler by desired rendering.

### Anima Aesthetic
Quality tags are less necessary.
Avoid unnecessary score-tag pressure.

### Anima Turbo
CFG1 / 8–12
Fast exploration; lower diversity.

### NoobAI EPS
Euler a / CFG5–6 / 25–30 / ~1MP.

### WAI17
Euler a / CFG5–7 / 15–30 / >1024² source area.
Keep quality/Negative compact.

These are author baselines, not cross-model universal settings.

## Promotion result

New ACCEPTED:
- K-PRACTICAL-010..015
