# CURRENT QUICK REFERENCE — KNOWLEDGE

Owner: Issue #44 `KNOWLEDGE:#44`  
Branch: `knowledge/generation-corpus`  
Latest organization checkpoint: Issue #44 comment `5600550931`

> This is a quick overview only. **Current verdict source of truth = `CLAIM_REGISTRY.csv`.**

## Purpose

Maintain recoverable generation knowledge so the project can move from short intent -> correct Special candidate -> minimum useful support/structure -> model-appropriate Prompt -> safe failure diagnosis -> fewer unnecessary iterations.

Runtime remains local/non-LLM. KNOWLEDGE does not own production specs, #32 verdicts, or Stage10 production authorization.

## Current focus

Primary empirical lane: **WAI Illustrious v17 + Forge Neo**.

Author guide:
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

## Important ACCEPTED knowledge

- model family/version/profile is part of the claim
- canonical/Alias/implication/UI-JA/model-trigger/generation-support are separate
- presence != relation/body-site/topology/count success
- minimum sufficient != shortest Prompt
- support can become anti-support
- Negative is an active semantic intervention
- A_ONLY/B_ONLY before blaming AB failure on an unknown tag
- one seed != reliability
- Prompt-only / LoRA/control-assisted / postprocess-repaired are separate evidence lanes
- evaluator vocabulary/semantic capability/calibration/OOD must be checked before confidence is interpreted

## Important CANDIDATE knowledge

- Anima natural-language/mixed prompting may help some relation expression but does not solve binding generally
- quality/meta changes can affect composition/style, not just “detail”
- Kagami-24k and CL Tagger v2 may reduce wide-vocabulary evaluator gaps but require final project calibration

## Important HOLD

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
- final WD EVA02/Kagami/CL coverage after dictionary freeze

See `HOLD_CONFLICT_REGISTER.md`.

## Family differences

- **WAI17:** exact author settings known; hard-target relation behavior still largely test-required
- **Illustrious family:** Booru-oriented; composition-tag conflicts are a known concern; derivatives need revalidation
- **NoobAI EPS:** exact native caption order includes Special before General; trained with Danbooru+e621 surfaces
- **NoobAI V-Pred:** separate inference regime; never pool with EPS
- **Anima:** Base/Aesthetic/Turbo separated; tags + NL supported; profile/trigger formatting differs; multi-character relation limits remain empirical

## Semantic / runtime / evaluator boundary

- semantic truth: Danbooru Wiki + active Alias/Implication
- model trigger: exact model evidence / controlled tests
- runtime behavior: official runtime docs/version
- generation effectiveness: controlled scoped evidence
- evaluator result: measurement aid, not semantic authority

## What PROMPT can consume now

Safe to hand off as KNOWLEDGE:
- `ACCEPTED` Claim IDs with matching model/version scope
- support taxonomy
- failure diagnosis/evidence discipline
- current exact author guide facts
- explicit REJECTED defaults to avoid

Not safe to hand off as settled:
- Registry `CANDIDATE/HOLD/CONFLICT`
- WAI/Noob/Anima hard relation success rates
- final evaluator allocation/thresholds
- exact optimal Prompt density/Support count
- canonical-vs-trigger activation equivalence

## Stop point

No large new research in this organization pass. Next empirical decisions remain gated by controlled WAI17 tests and final dictionary freeze/evaluator coverage work described in the HOLD register.

Restore: `handoff -> this file -> Claim Registry -> relevant Catalog -> HOLD/Version -> evidence only as needed`.
