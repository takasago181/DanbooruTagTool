# BATCH_AO — Model profiles and comparison grids — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: practical model-profile and comparison design
Scope: Anima / NoobAI / WAI, seeds, samplers, resolution, LoRA matrices

## 1. Comparison grids instead of showcase pairs

Anima official card:
https://huggingface.co/circlestone-labs/Anima

The author provides an `anima_comparison.json` workflow where:
- columns are models;
- rows are different seeds.

This is a strong general comparison pattern.

Use the same structure for:
- model comparison
- checkpoint/profile comparison
- sampler comparison
- LoRA weight comparison
- character/style adapter combinations.

Promoted:
- K-PRACTICAL-015.

## 2. Two seed modes

### Debug seed
One fixed seed.
Purpose:
- causal A/B
- find which change caused a difference.

### Robustness seed set
A small fixed set, e.g. 4–8 seeds.
Purpose:
- judge whether the chosen configuration generalizes;
- expose cherry-pick dependence.

Do not mix the two purposes.

Promoted:
- K-PRACTICAL-018.

## 3. Anima profile presets

### Turbo — iteration
Official:
- CFG 1
- 8–12 steps
- strong default style
- reduced diversity
- recommended starting profile for fast iterations.

Use for:
- prompt exploration
- scene iteration
- quick LoRA compatibility checks.

Revalidate final work on the intended target profile.

### Aesthetic — stable production candidate
- quality-tuned;
- quality tags not required;
- avoid score_* pushing it excessively;
- default style stronger than Base.

Use for:
- consistent final illustration
- fewer prompt/style corrections.

### Base — flexibility / LoRA / research
- neutral/plain default;
- maximum flexibility/diversity/style adherence;
- official LoRA training base.

Use for:
- LoRA training
- artist/style studies
- maximum prompt/style control
- capability research.

## 4. Anima sampler profiles

Official descriptions:

### er_sde
- neutral
- flatter colors
- sharp lines
- reasonable default.

### Euler a
- softer/thinner lines
- may lean more 2.5D
- can tolerate somewhat higher CFG.

### dpmpp_2m_sde_gpu
- similar family to er_sde
- more varied/creative
- can become too wild depending on prompt.

### Euler
- somewhat more creative than er_sde
- useful with more stable Aesthetic/Turbo.

This means sampler should be chosen by desired rendering/variance, not only benchmark speed.

Promoted:
- K-PRACTICAL-016.

## 5. NoobAI EPS diagnostic profile

Official author baseline:
- Euler a
- CFG 5–6
- 25–30 steps
- ~1MP total area

Author resolution set includes:
- 768×1344
- 832×1216
- 896×1152
- 1024×1024
- 1152×896
- 1216×832
- 1344×768.

Practical rule:
Choose aspect ratio from composition intent before tuning CFG/LoRA.

Portrait subject:
start portrait.

Wide multi-subject:
start landscape.

Do not generate square and expect Hires/crop to solve composition later.

Promoted:
- K-PRACTICAL-017.

## 6. WAI v17 production profile

Author baseline:
- Forge Neo
- Euler a
- 15–30 steps
- CFG 5–7
- >1024×1024 original area
- example 1024×1344.

Author Hires example:
- 1.5×
- 20 Hires steps
- Anime6B upscaler
- denoise 0.35–0.5.

Keep these as model-scoped references.

## 7. Character/style LoRA matrix

Do not search one dimension only.

Example grid:

| Character | Style |
|---|---|
| low | low |
| low | mid |
| low | high |
| mid | low |
| mid | mid |
| mid | high |
| high | low |
| high | mid |
| high | high |

Use exact numeric values appropriate to the actual adapters; “low/mid/high” is conceptual.

For each cell score:
- identity
- style
- pose/composition freedom
- outfit/background editability
- prompt adherence
- artifacts.

Promoted:
- K-PRACTICAL-019.

## 8. Multi-adapter grid order

Do not brute-force every adapter immediately.

Stage:
1. character weight sweep
2. style weight sweep
3. 3×3 character/style matrix
4. add detail/control adapter only after a viable region is found
5. robustness seed grid

This keeps search cost bounded.

## 9. Parameter XY plots

Useful axes:
- CFG × steps
- sampler × CFG
- LoRA weight × seed
- char LoRA × style LoRA
- denoise × upscaler method
- ControlNet strength × LoRA weight.

Do not combine more than two experimental axes per grid unless the workflow is automated and scoring is explicit.

## 10. Acceptance rules

A setting becomes a practical preset only when:
- it works across the robustness seed set;
- identity/style scores are acceptable;
- no severe prompt-controllability loss;
- model/runtime identity is pinned.

Otherwise keep it as:
- recipe candidate
- not default.

## Promotion result

New ACCEPTED:
- K-PRACTICAL-015..019
