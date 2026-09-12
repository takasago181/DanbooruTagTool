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
- generation knowledge corpus
- Prompt composition/support/anti-support knowledge
- minimum-sufficient Prompt research
- model-family Prompt guidance
- generation-effectiveness questions
- narrow controlled validation when a concrete adopted feature/research question requires it

KNOWLEDGE does not own production/spec adoption.
Historical Issue #5 is provenance only.

## Two horizons

### v1-supporting
- canonical/semantic authority
- Alias/implication boundaries
- Japanese understanding/search support
- source reliability
- browse/discovery explanation
- terminology traceability

### future/advanced generation
- WAI/Illustrious/NoobAI/Anima generation behavior
- support/anti-support
- binding/body-site/count/topology
- Negative interactions
- LoRA/control/postprocess
- evaluator/tagger limits
- controlled A/B evidence

Both use the same Claim Registry/HOLD/version system.

## Current empirical lane — only when justified

Primary local test lane remains **WAI Illustrious v17 + Forge Neo**.

Author guide context:
- Euler a
- Steps 15–30
- CFG 5–7
- short quality/Negative baseline
- Hires can materially repair anatomy

Project isolation baseline:
- 25 steps / CFG 5 / 1024×1344 portrait when appropriate
- fixed paired seeds
- Hires / ADetailer / LoRA / regional / Control OFF

**25 steps is a baseline, not a proven hard-target optimum.**
Do not run broad image tests merely to complete v1.

## Important ACCEPTED knowledge

- model family/version/profile is part of the claim
- canonical/Alias/implication/UI-JA/model-trigger/generation-support are separate
- presence != relation/body-site/topology/count success
- minimum sufficient != shortest Prompt
- support can become anti-support
- Negative is an active semantic intervention
- A_ONLY/B_ONLY before blaming AB failure on an unknown tag
- one seed != reliability
- fixed seed alone != exact cross-environment reproducibility
- runtime prompt preprocessing != Danbooru semantics or checkpoint generation behavior
- compositional targets should be diagnosable as atomic predicates instead of only one holistic score
- Prompt-only / LoRA-control-assisted / postprocess-repaired are separate evidence lanes
- evaluator vocabulary/semantic capability/calibration/OOD must be checked before confidence is interpreted

## Important CANDIDATE/HOLD areas

CANDIDATE examples:
- Anima natural-language/mixed prompting may help some relation expression but does not solve binding generally
- quality/meta changes can affect composition/style, not just detail
- Kagami-24k and CL Tagger v2 may reduce wide-vocabulary evaluator gaps but require project calibration

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
- final WD EVA02/Kagami/CL coverage

See `HOLD_CONFLICT_REGISTER.md`.

## Semantic / runtime / evaluator boundary

- semantic truth: Danbooru Wiki + active Alias/Implication
- model trigger: exact model evidence / controlled tests
- runtime behavior: official runtime docs/version
- generation effectiveness: controlled scoped evidence
- evaluator result: measurement aid, not semantic authority
- product adoption: DEV/product routing, not automatic from KNOWLEDGE

## What can be handed downstream as settled knowledge

Safe:
- `ACCEPTED` Claim IDs with matching scope
- source-authority conclusions
- support/failure principles within their scope
- exact author-guide facts
- explicit REJECTED defaults to avoid

Not settled:
- Registry `CANDIDATE/HOLD/CONFLICT`
- hard-relation success rates by model
- final evaluator allocation/thresholds
- exact optimal Prompt density/support count
- canonical-vs-trigger activation equivalence
- WAI17 generation benefit from runtime constructs without controlled evidence

## Legacy PROMPT labels

Old files/Registry metadata may still say `PROMPT` or `PROMPT:#5`.
Treat those as historical Prompt/generation-guidance provenance or downstream-domain labels, **not an active team**. New work routes to KNOWLEDGE #44.

Restore:
`main CURRENT_STATE/PRODUCT_GOAL -> Issue #44 -> handoff -> this file -> Claim Registry -> relevant Catalog -> HOLD/Version -> evidence only as needed`.
