# KNOWLEDGE Research Backlog — 2026-09-13

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `P0_P1_COMPLETE / NOOB_ANIMA_PRACTICAL_SOURCE_SYNTHESIS_COMPLETE / CONTROLLED_TESTS_NEXT_ON_DEMAND`

This file is a planning/backlog layer only. It does **not** override `CLAIM_REGISTRY.csv`, create product requirements, or promote HOLD/CANDIDATE claims.

## Current conclusion

The beginner-facing P0/P1 gap is complete at source/knowledge level.
The practical-generation readiness audit then found a second imbalance: failure diagnosis was stronger than daily finished-image workflow.

The first practical-generation enrichment pass is now complete for the two priority families:

1. **NoobAI XL**
2. **Anima**

Durable practical entry:
`PRACTICAL_GENERATION_NOOB_ANIMA.md`

Research:
- `../research/BATCH_L_NOOB_ANIMA_PRACTICAL_GENERATION_DEEP_DIVE_20260913.md`
- `../research/BATCH_M_JAPANESE_PRACTICAL_SOURCE_AUDIT_NOOB_ANIMA_20260913.md`

## P0 — COMPLETE

Existing-Prompt surface classification, semantic-role decomposition, Japanese explanation, Danbooru category/relation/unknown handling.

Research:
- `../research/BATCH_E_EXISTING_PROMPT_SURFACE_CLASSIFICATION_20260913.md`
- `../research/BATCH_F_PROMPT_SEMANTIC_ROLE_DECOMPOSITION_20260913.md`
- `../research/BATCH_G_BEGINNER_SAFE_JAPANESE_EXPLANATION_20260913.md`
- `../research/BATCH_H_DANBOORU_CATEGORY_RELATION_UNKNOWN_HANDLING_20260913.md`

## P1 — COMPLETE

Model quality/rating/artist/order/Negative/freshness and existing-Prompt conflict explanation.

Research:
- `../research/BATCH_I_MODEL_PROMPT_CONVENTIONS_QUALITY_ARTIST_ORDER_NEGATIVE_FRESHNESS_20260913.md`
- `../research/BATCH_J_EXISTING_PROMPT_CONFLICT_EXPLANATION_20260913.md`
- `../research/BATCH_K_EVALUATOR_FRESHNESS_RECHECK_20260913.md`

## PRACTICAL_GENERATION — source synthesis complete for NoobAI + Anima

### PG-01 Daily generation loop — PARTIALLY CONSOLIDATED
Current operational guide now covers:
- model/profile choice
- author baseline
- exploratory vs diagnostic seed behavior
- relation/composition before finishing tools
- one-LoRA-first isolation
- finishing ladder
- regional/control escalation

Still needs local hands-on tuning for exact preferred presets.

### PG-02 Exact-model quick-start cards — COMPLETE for priority families

Covered:
- NoobAI XL 1.1 EPS
- NoobAI XL V-Pred 1.0
- Anima Base v1.0
- Anima Aesthetic v1.1
- Anima Turbo v1.1

Current exact Anima SHA-256 identities are pinned in `VERSION_FRESHNESS_LEDGER.csv`.

### PG-03 Resolution + sampler/scheduler + seed workflow — SOURCE LEVEL COMPLETE / LOCAL TUNING OPEN

Known:
- exact official Noob EPS/V-Pred baselines
- exact official Anima family sampler descriptions
- Anima normal resolution range
- Turbo settings

Still open:
- preferred local aspect-ratio presets by scene type
- final local sampler/scheduler preferences
- exact batch/X-Y-Z routine

### PG-04 LoRA practical operations — SOURCE LEVEL COMPLETE / COMPATIBILITY TESTS OPEN

Known:
- Anima is a separate LoRA family from SDXL/Illustrious/Noob
- official Anima training base = Base
- NoobAI lineage makes Illustrious LoRAs reasonable candidates
- blanket Illustrious->Noob compatibility is rejected
- context leakage/loaded-state evidence rules retained

Open:
- representative Illustrious-LoRA -> Noob reliability matrix
- Anima LoRA behavior across Base/Aesthetic/Turbo
- exact local starting-weight habits per LoRA class

### PG-05 Hires + ADetailer — SOURCE LEVEL PARTIAL

Known:
- current ADetailer Neo mechanism and detector families
- repair-vs-base-evidence boundary
- Anima native-range/high-res escalation principle
- SDXL/Noob standard Hires path availability

Open:
- exact Noob finishing preset
- exact Anima profile-specific upscale/img2img choices
- ordering interaction among Hires/ADetailer/regional in local runtime

### PG-06 img2img / inpaint — PRINCIPLE COMPLETE / PARAMETER TUNING OPEN

Known repair ladder:
- broad semantic failure -> regenerate
- local defect -> inpaint/ADetailer
- preserved structure + low resolution -> upscale/Hires
- relation/ownership failure -> semantic/regional repair first

Exact denoise bands remain local/profile-specific.

### PG-07 Forge Couple / Control — SOURCE LEVEL COMPLETE / EFFECTIVENESS TEST OPEN

Current Forge Couple official source confirms:
- Forge Neo + Anima support
- Basic / Advanced / Mask
- subject-count guidance
- checkpoint-composition limitation

Current Forge Neo confirms:
- Anima LLLite
- Anima Region ControlNet

Next value requires exact local effectiveness tests rather than more generic prose.

### PG-08 Forge Neo preset / X-Y-Z / infotext workflow — SOURCE INVENTORY COMPLETE / DAILY PRESET DESIGN OPEN

Current maintained Forge Neo documents:
- Preset rewrite
- X/Y/Z
- infotext rewrite
- current LoRA / inpaint / ControlNet paths

A project-specific daily preset can be designed after exact local runtime identity and model files are installed/pinned.

### PG-09 Local-runtime identity / performance — OPEN

Requires exact local Forge Neo remote/commit and model/checkpoint hashes.
Do not generalize performance tuning before that.

## NoobAI controlled-test backlog

Priority when user requests image tests:

### N-T01 EPS vs V-Pred rendering
- dark/contrast hypothesis
- each model uses own recommended settings
- no identical-sampler forcing

### N-T02 Hard Special progression
`unary -> body-site -> actor-target -> count/composite`

### N-T03 Alias/historical trigger
Controlled exact-surface comparison.

### N-T04 Illustrious LoRA cross-use
Small representative adapter matrix; do not attempt thousands of LoRAs.

### N-T05 Negative collision
Especially anatomy/count-changing targets.

## Anima controlled-test backlog

### A-T01 Base vs Aesthetic v1.1 vs Turbo v1.1
Use profile-correct settings and score structural predicates separately from visual preference.

### A-T02 Tag-only vs concise hybrid relation
Predetermined paired seeds; actor/target/body-site/count judging.

### A-T03 Multi-character explicit identity
Test characteristic descriptions / actor labels before assisted control.

### A-T04 Forge Couple escalation
`plain -> Basic -> Advanced/Mask`.

### A-T05 LoRA x profile
Base/Aesthetic/Turbo with the same compatible Anima adapter where possible.

### A-T06 High-resolution finishing
Native -> upscale -> low-denoise img2img/tile comparison.

## P2 — advanced hard-target research remains on-demand

The older P2 questions remain valid but now route through the priority practical families first where appropriate:
- canonical/Alias response
- body-site/binding/topology/device/tentacle/count ceilings
- support interference
- LoRA interaction
- Prompt-only -> assisted-control threshold
- evaluator calibration

Do not launch broad image testing without a concrete question.

## Japanese-source maintenance policy

High-priority recurring Japanese sources:
- としあきdiffusion Wiki — Anima
- としあきdiffusion Wiki — Illustrious-XL / NoobAI
- としあきdiffusion Wiki — LoRA / Anima LoRA
- EasyForgeNeo Japanese README

Detailed individual comparison sources are useful for hypotheses, not universal truths.

Important stale-info guards:
- current maintained Forge Neo = `Haoming02/sd-webui-forge-classic` branch `neo`
- Anima is not ComfyUI-only in the current Forge Neo environment
- generic “NoobAI” settings that collapse EPS and V-Pred are rejected
- Preview-era Anima recipes do not become current Base/Aesthetic/Turbo defaults
- Turbo LoRA and official Turbo checkpoint are distinct

## Recommended next behavior

No need for another broad web overview immediately.

Next useful work is one of:
1. install/pin exact NoobAI/Anima local files and runtime identity;
2. build current Forge Neo presets from author baselines;
3. run one controlled test from N-T01..N-T05 or A-T01..A-T06;
4. maintain Japanese/current source freshness while #64 DEV proceeds.

For each future batch:
- preserve exact source/version/date
- separate author fact / runtime fact / practical community / controlled evidence
- update Claims only for durable statements
- unresolved effects remain HOLD/CANDIDATE
- update version ledger/file map/#44 checkpoint

No new knowledge automatically changes DEV/product behavior.
