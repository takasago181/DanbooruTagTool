# CURRENT QUICK REFERENCE — KNOWLEDGE

Owner: Issue #44 `KNOWLEDGE:#44`  
Branch: `knowledge/generation-corpus`

> This is a quick overview only. **Current verdict source of truth = `CLAIM_REGISTRY.csv`.**

## Current product relationship

Current v1 goal:

`理解 -> 発見 -> 選択 -> 出力`

A beginner should be able to understand an existing Prompt in Japanese, discover Special/General tags through Japanese/English search or browsing, choose manually, and copy canonical English.

The old knowledge-lane wording `intent -> Special -> support -> optimized Prompt -> diagnosis` is **not the current v1 product goal**. It remains a future/advanced generation-knowledge target only.

## Team ownership

The separate PROMPT team/lane was retired on 2026-09-12.

KNOWLEDGE #44 now owns:
- knowledge corpus
- existing-Prompt understanding knowledge
- Prompt composition/support/anti-support knowledge
- model-family Prompt conventions
- practical generation knowledge
- generation-effectiveness questions
- narrow controlled validation when a concrete research/product question requires it

KNOWLEDGE does not own production/spec adoption.
Historical Issue #5 is provenance only.

---

# Practical generation focus — NoobAI + Anima

Current source-research priority:
1. **NoobAI XL 1.1 EPS** — tag-first practical workhorse
2. **Anima official family** — hybrid/relation-explicit practical family
3. NoobAI V-Pred 1.0 — separate V-Pred alternate lane
4. WAI17 — comparison/reference and existing local-test history

Operational guide:
`PRACTICAL_GENERATION_NOOB_ANIMA.md`

Deep research:
- `../research/BATCH_L_NOOB_ANIMA_PRACTICAL_GENERATION_DEEP_DIVE_20260913.md`
- `../research/BATCH_M_JAPANESE_PRACTICAL_SOURCE_AUDIT_NOOB_ANIMA_20260913.md`

## NoobAI EPS 1.1 — fast card

Author baseline:
- Euler a
- 25–30 steps
- CFG 5–6
- around SDXL 1MP
- caption structure: `count -> character -> series -> artist -> special -> general -> other`
- Danbooru + e621 native-tag training context

Practical rule:
- use for tag-centric generation and mature Illustrious/SDXL ecosystem access
- author example Negative includes `nsfw`; do not use that blindly when the intended image itself is adult-rated
- exact hard relation/body-site/count ceiling remains HOLD

## NoobAI V-Pred 1.0 — fast card

Author baseline:
- **Euler**
- 28–35 steps
- CFG 4–5
- V-Pred-aware runtime required

Do not mix with EPS inference settings or pool results.
Community reports about stronger dark/contrast rendering remain practical hypotheses until controlled local comparison.

## Anima current exact profiles

### Base v1.0
SHA-256:
`bd43b7cffe1ed1153d9c41e7beb2f18cb1273eafbaa3af3edd6a173dc90a006e`

Role:
- maximum flexibility/diversity
- official LoRA training base
- normal guidance: 30–50 steps / CFG 4–5

### Aesthetic v1.1
SHA-256:
`3c1868387a3a1ff504bbb87c33678321965ead381fcf87afbd0264daa600c082`

Role:
- stronger consistency/default quality
- quality tags unnecessary
- author recommends avoiding `score_*` in Positive and Negative

### Turbo v1.1
SHA-256:
`fba11953276b57edf59d1dc4f1857ac05aa079c56f982b4d7c20298d57d3f7eb`

Role:
- fast Prompt/seed exploration
- CFG 1 / 8–12 steps
- stronger default style/stability, reduced diversity
- ordinary Negative-conditioning workflow is not transferable unchanged

## Anima relation rule

High-value practical lane:
- explicit actor identities
- explicit visible distinguishing features when multiple actors matter
- concise factual relation wording when tags alone are ambiguous
- do not rely on tag distance for ownership
- BREAK is runtime/parser syntax, not semantic character binding

Exact tag-only vs hybrid success rate remains HOLD.

## Anima assisted-control escalation

`plain explicit Prompt -> concise hybrid -> Forge Couple Basic -> Advanced/Mask -> Anima Region/LLLite ControlNet`

Current Forge Couple officially supports Anima.
Assisted success remains distinct from plain-Prompt capability.

## LoRA family boundary

- Anima LoRA != SDXL/Illustrious/Noob LoRA family
- official Anima LoRA training base = Base
- Illustrious-family LoRAs are reasonable **candidates** on Noob, not guaranteed compatible
- always preserve adapter training base, trigger and weight

---

## Existing Prompt interpretation — current quick rules

### 1. Classify the surface before assigning meaning

A comma-separated Prompt item is **not automatically a Danbooru tag**.

First distinguish, where evidence allows:
- exact canonical Danbooru/Special identity
- approved Alias/historical surface
- runtime syntax / wrapper
- model-specific Prompt convention/trigger
- natural-language fragment
- unknown / ambiguous text

### 2. Search can be permissive; interpretation is conservative

Search/discovery may use partial/fuzzy/Semantic support.
Pasted-Prompt interpretation is exact-first.
A fuzzy candidate must never silently become asserted meaning.

### 3. Wrapper and semantic payload are separate

Example:
`(looking_at_viewer:1.2)`

Interpret separately as runtime emphasis/weight wrapper + inner semantic payload.
Runtime syntax is not canonical semantic authority.

### 4. Keep three axes separate

- Danbooru tag category
- semantic/explanation role
- generation effect

One axis does not redefine the others.

### 5. Preserve unknowns

If meaning cannot be resolved confidently:
- keep raw text
- show unknown/ambiguous
- do not invent Japanese meaning
- do not force the nearest fuzzy tag

### 6. Explain conflict; do not auto-rewrite

`detect -> explain -> preserve -> user decides`

Do not silently turn conflict detection into deletion/rewrite/failure probability.

---

## Beginner-safe Japanese explanation

Keep separate:
- short Japanese display label
- fuller Japanese explanation
- Japanese search synonyms

Canonical English identity remains visible/traceable.
Preserve actor/receiver/owner, body-site, exact count, source/destination and implication-vs-Alias distinctions.

---

## Model Prompt convention boundary

### WAI Illustrious v17
Short quality/Negative author baseline and rating surfaces are WAI17 conventions, not universal grammar.

### Illustrious early/base
Official base guidance includes quality vocabulary and composition-conflict warning. Derivatives require revalidation.

### NoobAI
Exact caption structure and quality/date conventions are model-specific. EPS and V-Pred remain separate.

### Anima
Official grouping:
`quality/meta/year/safety -> count -> character -> series -> artist -> general`

Model conventions include spaces/lowercase, `@artist`, mixed tags/NL, and profile-specific quality behavior.

---

## Negative Prompt boundary

Two layers:
1. semantic principle — Negative conditioning can suppress intended meaning
2. exact-model recipe — author baseline is model/profile/intent scoped

Never promote one model's Negative recipe to a universal default.

---

## Current source freshness

Primary model/runtime sources rechecked on 2026-09-13.

Important current facts:
- Anima Base v1.0 / Aesthetic v1.1 / Turbo v1.1 exact file hashes are pinned in `VERSION_FRESHNESS_LEDGER.csv`
- current maintained Forge Neo = `Haoming02/sd-webui-forge-classic` branch `neo`
- current Forge Neo explicitly supports Anima and updated Anima control paths
- exact local Forge Neo remote/commit is still unpinned
- CL Tagger `v2_01a` remains provisional/in-place-update risk

---

## Current empirical state

Source research now prioritizes NoobAI + Anima.

Existing local controlled evidence remains model/version-specific; do **not** pretend Noob/Anima hard-target performance is proven until exact local checkpoints/runtime are tested.

Recommended future controlled lanes:
- Noob EPS vs V-Pred
- Noob hard relation/body-site/count
- Anima Base vs Aesthetic v1.1 vs Turbo v1.1
- Anima tag-only vs concise hybrid relation
- Noob/Illustrious LoRA cross-use
- Anima LoRA x profile
- Forge Couple escalation

---

## Important ACCEPTED principles

- model family/version/profile is part of every generation claim
- canonical/Alias/implication/UI-JA/model-trigger/generation-support are separate
- search permissive != interpretation permissive
- tag category != semantic role != generation effect
- presence != relation/body-site/topology/count success
- minimum sufficient != shortest Prompt
- support can become anti-support
- Negative is an active semantic intervention
- one seed != reliability
- runtime preprocessing != model semantics
- Prompt-only / LoRA-control-assisted / postprocess-repaired are separate evidence lanes
- evaluator vocabulary/calibration/OOD must be checked before confidence is interpreted

## Important HOLD areas

- Noob canonical/Alias/trigger response
- Noob hard actor/body-site/count ceiling
- Noob EPS vs V-Pred practical delta
- Illustrious-LoRA -> Noob reliability
- Anima tag-only vs concise hybrid delta
- Anima Base/Aesthetic/Turbo hard-target delta
- Anima profile-specific LoRA behavior
- exact Prompt-only -> assisted-control threshold
- final evaluator coverage/calibration

---

## Current research backlog state

See `RESEARCH_BACKLOG_20260913.md`.
Practical Noob/Anima source synthesis is complete; next high-value additions are exact local controlled comparisons, not another broad generic web overview.

---

## Semantic / runtime / evaluator / product boundary

- semantic truth: Danbooru Wiki + active Alias/Implication
- model trigger/convention: exact model evidence / controlled tests
- runtime behavior: official runtime docs/version + pinned local identity when critical
- generation effectiveness: controlled scoped evidence
- evaluator result: measurement aid, not semantic authority
- product adoption: DEV/product routing, not automatic from KNOWLEDGE

## Legacy PROMPT labels

Old files/Registry metadata may still say `PROMPT` or `PROMPT:#5`.
Treat those as historical Prompt/generation-guidance provenance, **not an active team**. New work routes to KNOWLEDGE #44.

Restore:
`main CURRENT_STATE/PRODUCT_GOAL -> Issue #44 -> this file -> PRACTICAL_GENERATION_NOOB_ANIMA -> Claim Registry -> Version Ledger -> relevant Catalog -> evidence as needed`.
