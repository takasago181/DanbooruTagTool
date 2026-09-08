# Issue #30 verdict routing golden-set dry run — 2026-09-08

## Purpose

Validate a conservative `A_WIN / B_WIN / REVIEW / BLOCKED` routing policy on top of the already-PASSed Forge Neo API → A/B generation → PNG metadata → WD14 raw-confidence pipeline.

This is still **non-production Stage10-prep**. Do not promote any threshold or routing rule to production from this task alone.

## Verified input

Infrastructure pipeline evidence:
- branch: `codex/issue30-automation-dry-run-20260908`
- evidence commit: `f2fc7acb15f996630c9f008284d80cf3261fb32f`
- verdict: `PASS_PIPELINE`
- Forge Neo: `neo-2.29`
- model: `waiIllustriousSDXL_v170`, hash `f116b0c78f`
- API-enabled Forge is already available
- WD14 model: `wd14-eva02.v3.large`
- prior diagnostic values demonstrate tag sensitivity but are **not winner rules**

## Hard boundaries

Do not:
- start Stage10 production A/B
- edit `CURRENT_DEV_TASK.md`
- edit Issue #35-owned files
- edit `data/**` or `validation_quarantine/**`
- weaken protected/hash validation
- update Forge Neo/extensions/dependencies
- switch model family/checkpoint
- POST `/sdapi/v1/options`
- add Agent Scheduler
- create a production scoring module
- hard-code a final global confidence threshold

Keep the existing API-enabled Forge runtime and fixed checkpoint.

## Golden-set size

Keep this intentionally small and fast:
- 4 semantic target experiments
- 2 fixed seeds per experiment
- A/B per seed
- total: 8 A/B comparisons / 16 generated images

Use seeds:
- `5072`
- `17027`

Fixed generation settings:
- Negative Prompt: `lowres, blurry, bad anatomy, text, watermark`
- Steps: 24
- CFG: 4.5
- Sampler: Euler a
- Scheduler: Automatic
- Size: 1024x1024
- Batch size/count: 1/1
- LoRA: none
- model/checkpoint unchanged

## Experiments

Each experiment has **one evaluation target tag**. A and B differ only by whether the target concept is explicitly encouraged. Alternate expected side to detect positional bias.

### G1 — pose / expected A stronger
Target tag: `standing`

A:
`1girl, solo, standing, looking at viewer, simple background`

B:
`1girl, solo, looking at viewer, simple background`

### G2 — pose / expected B stronger
Target tag: `sitting`

A:
`1girl, solo, looking at viewer, simple background`

B:
`1girl, solo, sitting, looking at viewer, simple background`

### G3 — appearance / expected A stronger
Target tag: `long_hair`

A:
`1girl, solo, long hair, portrait, looking at viewer, simple background`

B:
`1girl, solo, portrait, looking at viewer, simple background`

### G4 — expression / expected B stronger
Target tag: `smile`

A:
`1girl, solo, portrait, looking at viewer, simple background`

B:
`1girl, solo, smile, portrait, looking at viewer, simple background`

Prompt wording may be normalized only to the canonical tag form actually accepted by Forge/Danbooru prompt syntax; record the exact sent and actual PNG Prompt. Do not add other semantic modifiers.

## Phase 1 — generate and capture

For every experiment × seed × side:
1. generate via `/sdapi/v1/txt2img`
2. save PNG with stable experiment/seed/side name
3. record SHA-256
4. capture actual PNG infotext using `/sdapi/v1/png-info`
5. verify all fixed fields match and only intended positive-Prompt difference exists
6. run WD14 `wd14-eva02.v3.large`, threshold `0.0`
7. save full raw JSON
8. extract target-tag confidence for A and B

If generation or required metadata is missing, classify the comparison as infrastructure `BLOCKED` and do not infer a winner.

## Phase 2 — coverage-aware pre-routing

Before any confidence comparison:
- confirm the target tag exists in WD14 output/vocabulary for this model
- if absent/unavailable, candidate route is `REVIEW_UNSUPPORTED`, never FAIL/WIN
- do not treat a low or zero confidence as equivalent to unsupported vocabulary

Also create one synthetic coverage test record with a deliberately nonexistent target tag such as `__issue30_nonexistent_target__`. It must route to `REVIEW_UNSUPPORTED` without image-quality inference.

Create one synthetic metadata-failure fixture by omitting required traceability fields from a copied machine-readable record. It must route to `BLOCKED_METADATA` before scoring.

These two synthetic records do not require additional image generation.

## Phase 3 — human golden labels

Do **not** use Prompt intent as final truth. The generated image must be reviewed.

Prepare a compact human review sheet for the 8 real A/B comparisons. For each comparison include:
- experiment ID
- seed
- target concept
- A image path
- B image path
- A/B thumbnails or IIB-ready paths when practical
- no WD14 target confidence shown in the initial human-label field, to avoid anchoring bias
- label choices: `A`, `B`, `TIE/UNCLEAR`, `INVALID`

Preferred review path: approved Forge Neo Infinite Image Browsing side-by-side comparison.

The user should need only **8 visual decisions** for this first calibration pass.

Store labels separately from WD14 evidence so machine predictions can be evaluated against independent human labels.

If human labels are not yet available, stop Phase 4 with `WAITING_HUMAN_GOLDEN_LABELS`; do not invent labels from Prompt intent.

## Phase 4 — threshold exploration after labels exist

Do not choose a threshold before seeing the golden labels.

Evaluate a conservative grid, not one arbitrary number:
- minimum winning-side confidence candidates: 0.40, 0.50, 0.60, 0.70
- minimum A/B confidence-margin candidates: 0.15, 0.25, 0.35, 0.45

For each grid point:
- auto-decision count
- REVIEW count/rate
- agreement with human label on decided cases
- false decisive calls
- per-target breakdown

Candidate routing semantics for analysis only:
- missing required metadata/infrastructure evidence -> `BLOCKED`
- unsupported target vocabulary -> `REVIEW`
- human label `TIE/UNCLEAR` should generally remain REVIEW unless evidence for a safe alternative is established
- confidence insufficient or A/B margin below candidate threshold -> `REVIEW`
- otherwise higher-confidence side -> candidate `A_WIN` or `B_WIN`

Selection principle:
- prioritize **precision of automatic decisions over coverage**
- on this tiny initial golden set, any candidate with a false decisive call is not acceptable for promotion
- do not infer that one threshold generalizes to rare/relational Special2788 cases

## Required outputs

On the Issue #30 evidence branch, add/update evidence only. Do not merge production scoring code.

Required machine-readable output should include:
- experiment/seed/side
- PNG path/hash
- exact actual Prompt/metadata
- WD14 target coverage status
- target confidence A/B
- human label when available
- threshold-grid results when available
- candidate route
- reason code

Required human-readable report should summarize:
- generation/metadata pass rate
- WD14 target coverage rate
- human REVIEW count
- threshold-grid precision vs coverage
- any false decisive calls
- recommended next status: `ROUTING_CANDIDATE_OK`, `NEEDS_MORE_GOLDEN_DATA`, `WAITING_HUMAN_GOLDEN_LABELS`, or `BLOCKED`

## Completion boundary

This task does **not** complete Issue #30 by itself unless:
- the 8 visual labels exist
- conservative routing is evaluated against them
- unsupported target -> REVIEW is verified
- missing metadata -> BLOCKED is verified
- no unsafe forced two-way behavior is found
- the remaining limitation for rare/relational Special2788 is explicitly documented

Even then, treat the result as a Stage10-prep routing candidate, not a universal production truth.
