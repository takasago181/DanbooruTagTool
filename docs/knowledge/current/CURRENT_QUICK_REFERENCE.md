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
- generation-effectiveness questions
- narrow controlled validation when a concrete adopted feature/research question requires it

KNOWLEDGE does not own production/spec adoption.
Historical Issue #5 is provenance only.

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

Examples of runtime/wrapper surfaces include weighting/emphasis syntax, `BREAK`, LoRA/embedding-like syntax, and template/dynamic syntax.

### 2. Search can be permissive; interpretation is conservative

Search/discovery may use partial/fuzzy/Semantic support.

Pasted-Prompt interpretation is exact-first:
- exact canonical
- exact approved Alias
- exact known runtime/model syntax
- otherwise ambiguous/unknown

A fuzzy candidate must never silently become asserted meaning.

### 3. Wrapper and semantic payload are separate

Example:
`(looking_at_viewer:1.2)`

Interpret separately as:
- runtime emphasis/weight wrapper
- inner semantic payload `looking_at_viewer`

Runtime syntax is not canonical semantic authority.

### 4. Keep three axes separate

- **Danbooru tag category** — General / Character / Copyright / Artist / Meta
- **semantic/explanation role** — appearance / clothing / expression / pose / action / relation / camera / background / style etc.
- **generation effect** — what an exact checkpoint actually does with the surface

One axis does not redefine the others.

### 5. Preserve unknowns

If meaning cannot be resolved confidently:
- keep the raw text
- show unknown/ambiguous state
- do not fabricate a Japanese meaning
- do not force the closest fuzzy tag

### 6. Explain conflict; do not auto-rewrite

Current beginner-first rule:

`detect -> explain -> preserve -> user decides`

Useful explanation classes include:
- same-role composition tension
- count contradiction
- canonical/Alias duplicate identity
- implication / broad+specific overlap
- Positive/Negative semantic overlap
- actor/target/ownership ambiguity
- malformed/unknown runtime syntax

Do not translate those automatically into deletion, rewrite, or predicted failure probability.

## Beginner-safe Japanese explanation

Keep separate:
- short Japanese display label
- fuller Japanese explanation
- Japanese search synonyms

Canonical English identity remains visible/traceable.

Do not lose intrinsic distinctions such as:
- actor / receiver / owner
- body-site
- exact count
- object vs wearer-state vs action
- source/destination
- parent/child implication vs Alias identity

Awkward but understandable Japanese does not require endless stylistic repair; clear semantic error, role inversion, broken composition, or non-Japanese residue does.

## Model Prompt conventions — quick boundary

### WAI Illustrious v17

Current author guidance includes:
- short positive quality baseline
- short Negative quality/artifact baseline
- safety/rating-like Prompt surfaces

Treat these as **WAI17 Prompt conventions**, not universal Danbooru semantics or universal Prompt grammar.

### Illustrious early/base

Official base guidance includes:
- explicit quality-tag vocabulary
- warning about conflicting critical composition tags
- no default style in the base

Derivative behavior requires revalidation.

### NoobAI XL 1.1 EPS / V-Pred

Documented caption organization:
`count -> character -> series -> artist -> special -> general -> other`

Quality labels are documented as NoobAI project training/Prompt conventions based on popularity/recency processing, not Danbooru `score:` metadata.

EPS and V-Pred remain separate inference regimes.

### Anima

Current author guidance documents grouped ordering:
`quality/meta/year/safety -> count -> character -> series -> artist -> general`

Important exact-model conventions:
- `score_*` is a learned Prompt surface, not Danbooru `score:` metadata
- artist Prompt surface uses `@artist`
- Danbooru Artist canonical identity itself is not rewritten to `@artist`
- Anima-Aesthetic is a profile exception: quality tags are unnecessary and author guidance recommends avoiding `score_*` in Positive and Negative

Base / Aesthetic / Turbo remain separately scoped.

## Artist/style boundary

Keep separate:
1. Danbooru Artist identity — creator identity
2. model artist/style trigger — checkpoint-specific generation surface
3. generic style description
4. style LoRA/adapter

A Danbooru Artist tag does not semantically mean `apply this style`, even when a checkpoint learns that surface as a style/content trigger.

## `score:` / `rating:` / `score_*` boundary

Do not collapse:
- Danbooru post/search metadata such as `score:` / `rating:`
- Danbooru Meta tag identity
- model-learned surfaces such as `score_7`
- model safety/rating Prompt surfaces such as `safe`, `nsfw`, `explicit`

They require separate source/model evidence.

## Negative Prompt boundary

Two layers:

1. semantic principle — Negative conditioning is an active intervention and may overlap intended meaning
2. exact-model recipe — author-recommended Negative baselines are model/profile-scoped guidance

Never promote one model's Negative recipe to a universal default.

## Current source freshness note

Primary public model/Danbooru/Forge-Neo sources were rechecked on 2026-09-13.

Important evaluator update:
- CL Tagger stable `v2.00`
- current `v2_01a` is provisional
- author/model card states provisional versions may be updated in place under the same version label

Therefore promotion-critical CL Tagger evidence must preserve exact sub-version + retrieval/artifact identity.

The user's exact local Forge Neo remote/commit and installed-extension identities are still not pinned; local promotion-critical runtime claims remain gated on that capture.

## Current empirical lane — only when justified

Primary local test lane remains **WAI Illustrious v17 + Forge Neo**.

Project isolation baseline:
- Euler a
- 25 steps
- CFG 5
- 1024×1344 portrait when appropriate
- fixed paired seeds
- Hires / ADetailer / LoRA / regional / Control OFF

**25 steps is a baseline, not a proven hard-target optimum.**
Do not run broad image tests merely to complete v1.

## Important ACCEPTED knowledge

- model family/version/profile is part of every generation claim
- canonical/Alias/implication/UI-JA/model-trigger/generation-support are separate
- existing Prompt surface type must be classified before meaning is asserted
- search permissive != interpretation permissive
- tag category != semantic role != generation effect
- unknown text remains unknown rather than guessed
- conflict handling for v1 is explain/preserve/user-choice, not auto-rewrite
- presence != relation/body-site/topology/count success
- minimum sufficient != shortest Prompt
- support can become anti-support
- Negative is an active semantic intervention
- author Negative recipes are exact-model guidance, not universal defaults
- one seed != reliability
- fixed seed alone != exact cross-environment reproducibility
- runtime preprocessing != Danbooru semantics or checkpoint behavior
- Prompt-only / LoRA-control-assisted / postprocess-repaired are separate evidence lanes
- evaluator vocabulary/calibration/OOD must be checked before interpreting confidence

## Important CANDIDATE/HOLD areas

CANDIDATE examples:
- Anima natural-language/mixed prompting may help some relation expression but does not solve binding generally
- exact quality/meta effectiveness beyond documented author conventions
- Kagami/CL broad vocabulary usefulness for this project's final calibration

HOLD examples:
- WAI17 canonical vs Alias/trigger response
- rare Special activation
- broad+specific effect
- actor-target/body-site/topology/device/tentacle relation ceilings
- simultaneous Special/count breakpoints
- unusual anatomy/count Negative ON/OFF
- LoRA interaction
- Prompt-only -> assisted-control threshold
- NoobAI exact camera/relation/trigger behavior
- Anima tag-only vs concise-hybrid delta
- final WD EVA02/Kagami/CL coverage/calibration

See `HOLD_CONFLICT_REGISTER.md`.

## Current research backlog state

`RESEARCH_BACKLOG_20260913.md` status:

`P0_P1_COMPLETE / P2_ON_DEMAND`

Do not automatically start broad P2 image testing.
Pull one unresolved generation question only when:
- the user explicitly wants it, or
- a concrete adopted feature needs the evidence.

## Semantic / runtime / evaluator / product boundary

- semantic truth: Danbooru Wiki + active Alias/Implication
- model trigger/convention: exact model evidence / controlled tests
- runtime behavior: official runtime docs/version + pinned local identity when critical
- generation effectiveness: controlled scoped evidence
- evaluator result: measurement aid, not semantic authority
- product adoption: DEV/product routing, not automatic from KNOWLEDGE

## What can be handed downstream as settled knowledge

Safe:
- `ACCEPTED` Claim IDs with matching scope
- source-authority conclusions
- existing-Prompt interpretation principles
- exact author-guide facts
- explicit REJECTED defaults to avoid

Not settled:
- Registry `CANDIDATE/HOLD/CONFLICT`
- hard-relation success rates by model
- final evaluator allocation/thresholds
- exact optimal Prompt density/support count
- canonical-vs-trigger activation equivalence
- WAI17 generation benefit from unresolved support/runtime constructs

## Legacy PROMPT labels

Old files/Registry metadata may still say `PROMPT` or `PROMPT:#5`.
Treat those as historical Prompt/generation-guidance provenance or downstream-domain labels, **not an active team**. New work routes to KNOWLEDGE #44.

Restore:
`main CURRENT_STATE/PRODUCT_GOAL -> Issue #44 -> handoff -> this file -> Claim Registry -> relevant Catalog -> HOLD/Version -> evidence only as needed`.
