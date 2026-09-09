# Generation Knowledge Index

Owner: Issue #44 `[KNOWLEDGE][ONGOING] Persistent generation knowledge corpus for dictionary audit and Stage10`

Branch: `knowledge/generation-corpus`

Status: **ONGOING / GOAL_REBASED / BATCH_A+B+C_COMPLETE / EXACT_FAMILY_GAPS_NEXT**

## Purpose

Restart point for the persistent KNOWLEDGE lane. A new chat must recover current generation knowledge from GitHub without conversational memory.

The corpus is evidence/reference only. It does not itself rewrite production data, #32 verdicts, Stage10 scoring, Prompt grammar, or other team decisions.

## Restart order

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 latest comments
4. this file
5. `docs/knowledge/CURRENT_PRODUCT_GOAL_20260909.md`
6. `docs/knowledge/PRODUCT_GOAL_EVOLUTION_20260909.md`
7. `docs/knowledge/KNOWLEDGE_REASSESSMENT_20260909.md`
8. relevant `docs/knowledge/research/*`
9. `docs/knowledge/GENERATION_KNOWLEDGE_CORPUS.md`
10. `docs/knowledge/GENERATION_KNOWLEDGE_SOURCES.md`
11. requesting Issue only when later handoff is explicitly requested

## Current product-goal baseline

Original Special-first purpose remains valid; it **expanded rather than reversed**.

`short Japanese/English intent -> correct Special Core Dictionary candidate(s) -> minimum useful support/structure -> model-family-appropriate canonical-English Prompt -> safe failure diagnosis -> fewer unnecessary generation iterations`

Primary success criterion:
**reduce manual trial-and-error while preserving semantic correctness, model-family scope, traceability, and safe uncertainty.**

## Evidence classes

- `FACT_EXACT_MODEL`
- `FACT_GENERAL`
- `CONTROLLED_PRACTICAL`
- `PRACTICAL`
- `COMMUNITY`
- `HOLD`
- `REJECT`

Language is not an evidence rank. Mirrors/translations of one experiment are not independent confirmation.

## Current family coverage

| Family | State | Strongest knowledge | Important gaps |
|---|---|---|---|
| WAI Illustrious v17 | strong | exact author settings; quality/Negative overloading warning; Hires confound; practical regional actor-separation evidence | Prompt-only actor/body-site relation ceiling; alternate trigger/rare exposure; exact pruning effect sizes |
| Illustrious XL early | strong | exact composition-tag conflict warning; quality vocabulary | derivative-specific relation binding and minimum-sufficient transferability |
| NoobAI XL 1.1 EPS | strong | exact inference regime; native caption order Special-before-General | actor/body-site relation grammar; camera; broad+specific; canonical/Alias response; rare exposure |
| NoobAI V-Pred 1.0 | medium-strong | exact EPS/V-Pred separation and inference regime | project-relevant composition/binding/pruning evidence |
| Anima | strong | exact formatting/order/profile/tag-dropout/Gelbooru rules; mixed tag/NL; practical multi-character evidence | exact multi-actor ceiling; profile-specific relation/density/pruning effect sizes |

## Current topic coverage

| Topic | State | Current use |
|---|---|---|
| support conflict / anti-support | strong general / medium exact-family | compatible support can be neutral/harmful |
| minimum-sufficient Prompt | **strong framework** | semantic nucleus + role-based pruning + leave-one-out ablation + bounded escalation |
| broad + specific | **TEST_REQUIRED** | no universal add/delete rule |
| actor-target/body-site binding | strong general / medium exact-family | relation correctness separate from concept presence |
| multi-Special composition | strong general / medium exact-family | unary-before-composite; competition/mode collision real |
| Negative interference | strong mechanism / exact-family TEST_REQUIRED | overlapping Negative can suppress intended target |
| canonical vs model trigger | strong Anima / medium cross-family | identity/history/trigger remain separate |
| concept density | strong general | semantic workload > raw token count |
| A1111/Forge chunking | medium-strong tool evidence | reject 75/77 hard-limit simplification; chunk boundary is a confound |
| seed sensitivity | strong general | seed is evidence identity |
| evidence reliability | **strong framework** | E0 case -> E1 repeatability -> E2 paired inference -> E3 generalization |
| human judgement uncertainty | strong general | `TIE / UNCLEAR / BOTH_FAIL / BLOCKED` preserved separately |
| evaluator/tagger limits | strong principle / final coverage pending | vocabulary + semantic class + calibration + OOD before verdict |
| WD EVA02 v3 | strong exact | common/unary baseline; <600-image tags structurally filtered |
| Kagami-24k | strong exact | wide-vocab unary candidate; paired-bootstrap evidence; rare tail still uncertain |
| CL Tagger v2 | strong exact | wide vocab; per-tag calibration/thresholds; OOD refs; license/gated constraints |
| LoRA/personalization | strong mechanism / project TEST_REQUIRED | interference/context prior; exact local effects unresolved |
| Hires/img2img/ADetailer | strong confound rule | final repair != base Prompt success |
| ControlNet/regional/Forge Couple | medium-strong | separate assisted-control lane |
| local empirical history | **strong safety/scope framework** | may tune local ranking, never semantic authority |
| failure diagnosis | medium-strong | diagnostic tree v1; exact family thresholds missing |

## Durable conclusions

1. Model family/version/profile is part of every generation claim.
2. Canonical identity, Japanese UI/search, Alias/history, and model trigger are separate layers.
3. Support needs both a semantic role and an empirical effect classification.
4. Multi-concept failure is not evidence that one component tag is unknown.
5. Relation/ownership/body-site binding is distinct from component presence.
6. Negative Prompt is an active semantic intervention.
7. Seed is part of experiment identity; one seed is not a reliability estimate.
8. Post-processing/control interventions must be separate from Prompt-only success.
9. LoRA/personalization can introduce interference and hidden priors.
10. Prompt difficulty is semantic/concept/binding load, not raw token length alone.
11. Current Danbooru post_count is not direct model-exposure probability.
12. Minimum sufficient is not shortest; preserve the semantic nucleus and useful structural relation information.
13. Same-role composition tags should be replacement/ablation candidates, not default stacks.
14. Broad + specific remains empirical; do not auto-add parent/constituent.
15. A1111/Forge-style long prompts are chunked; `75/77 = hard project limit` is rejected.
16. Stop Prompt escalation when all relevant support roles fail to give repeatable benefit; use assisted-control/HOLD instead of unrelated tag growth.
17. Relative A/B improvement and absolute reliability must be reported separately.
18. For paired binary outcomes, informative directional evidence comes from discordant pairs; total seed count alone is not evidence strength.
19. Statistical significance is not product usefulness; direction, magnitude, collateral error, uncertainty and user-value are separate.
20. Human `TIE` and `UNCLEAR` are legitimate and different outcomes.
21. Evaluator vocabulary/semantic capability/calibration/OOD must be checked before interpreting confidence.
22. Preference/aesthetic reward models are not rare-Special semantic ground truth.
23. Local personal generation history may influence local empirical ranking only under pinned context; it must never rewrite canonical/semantic truth.

## Failure-diagnosis tree v1

Source: `docs/knowledge/research/BATCH_A_FALSE_ASSUMPTION_PREVENTION_20260909.md`

`traceability -> semantic identity -> unary activation -> composition/binding -> visibility/geometry -> Negative collision -> Prompt competition/pruning -> LoRA -> seed sensitivity -> assisted-control ceiling -> evaluator blindness`

## Minimum-sufficient Prompt protocol v1

Source: `docs/knowledge/research/BATCH_B_MINIMUM_SUFFICIENT_PROMPT_20260909.md`

Protected nucleus:
- selected Special(s)
- intrinsic count/actor/ownership/target/body-site/relation
- intrinsic implement/modifier
- justified model trigger syntax

Pruning order:
1. unrelated decoration / excess quality-aesthetic content
2. duplicate/synonymous representations
3. same-role frame/viewpoint conflicts
4. unproven broad parents/constituents
5. optional context/NL with no structural value
6. visibility/geometry/resource supports one at a time
7. weighting only after structural conflicts are cleaned

Use paired leave-one-out support ablation on predetermined seeds. Judge target, binding, visibility and collateral errors—not one unary tagger score.

## Evidence reliability protocol v1

Source: `docs/knowledge/research/BATCH_C_EVIDENCE_RELIABILITY_20260909.md`

### E0 — CASE / DEBUG
One/few predetermined pairs. Mechanism/counterexample only.

### E1 — REPEATABILITY
Predetermined paired seeds, all outputs retained, no cherry-picking.

### E2 — COMPARATIVE / INFERENCE
Predeclared sample + paired analysis + uncertainty + practical effect + defined TIE/UNCLEAR handling.

### E3 — GENERALIZATION / RULE
Multiple representative semantic cases + relevant model scope + collateral/evaluator analysis.

For binary A/B success, preserve:
- `A_ONLY_PASS`
- `B_ONLY_PASS`
- `BOTH_PASS`
- `BOTH_FAIL`
- `UNCLEAR/BLOCKED`

McNemar/exact-binomial reasoning can analyze discordant directions, while absolute success rates remain separately essential.

No context-free `N seeds = proven` rule is accepted.

## Evaluator capability gate v1

Before any machine verdict:
1. target in vocabulary / representable?
2. semantic class suitable for this evaluator?
3. exact evaluator version/calibration/threshold known?
4. OOD/unusual input risk?
5. human-machine contradiction?

Conceptual routes:
- `DIRECT_UNARY`
- `COUNT_ATTRIBUTE`
- `DECOMPOSED`
- `RELATION_HUMAN_OR_SPECIALIZED`
- `GEOMETRY_VISIBILITY`
- `UNSUPPORTED_OR_OOD`

Unsupported/OOD -> REVIEW, not image failure.

## Local empirical history boundary

May remember, under matching context:
- support tended to help/hurt;
- alternate trigger worked for exact model version;
- relation was seed-sensitive;
- assisted control was usually required.

Must not learn automatically:
- canonical meaning;
- Alias equivalence;
- intrinsic semantic-support truth;
- model-independent rules.

Context identity should include exact checkpoint, Specials, trigger surface, support set, Prompt/Negative, seed/settings, LoRA, post-processing/control, evaluator and outcome uncertainty.

## Current HOLD backlog

Highest value:
- WAI v17 Prompt-only actor-target/body-site ceiling
- NoobAI EPS actor/body-site/camera/visibility support
- cross-family canonical/Alias/alternate-trigger response
- exact anatomy/count-changing Negative effects
- broad+specific interaction
- exact simultaneous-Special/density breakpoints
- project-specific LoRA x Special/support interactions
- exact `fully visible / in frame / body part focus` family effects
- project-specific final evaluator coverage after dictionary freeze
- exact KEEP/MIXED/PRUNE thresholds for persistent guidance
- exact Prompt-only -> assisted-control escalation threshold

## Research batches

### Batch A — false-assumption prevention
**COMPLETE**
- `BATCH_A_FALSE_ASSUMPTION_PREVENTION_20260909.md`
- `BATCH_A_SOURCES_20260909.md`

### Batch B — minimum-sufficient Prompt / pruning
**COMPLETE**
- `BATCH_B_MINIMUM_SUFFICIENT_PROMPT_20260909.md`
- `BATCH_B_SOURCES_20260909.md`

### Batch C — evidence reliability / evaluator boundaries
**COMPLETE**
- `BATCH_C_EVIDENCE_RELIABILITY_20260909.md`
- `BATCH_C_SOURCES_20260909.md`

Main gains:
- E0-E3 evidence hierarchy;
- paired-vs-absolute outcome separation;
- small-sample exact paired reasoning;
- TIE/UNCLEAR handling;
- capability-routed evaluator gate;
- current WD/Kagami/CL Tagger evidence identities;
- deterministic local-history authority boundary;
- assisted-control evidence separation.

### Next — exact-family gap research
**NEXT**

Priority:
1. WAI v17 actual relation/body-site/multi-actor behavior
2. NoobAI EPS relation/body-site/framing behavior
3. cross-family canonical/Alias/alternate-trigger drift
4. unusual anatomy/count Negative interactions
5. broad+specific behavior
6. LoRA x Special/support under realistic anime checkpoints

Generic sampler/aesthetic micro-optimization remains lower priority unless it materially affects these targets.

## Independence mode

Current user instruction: KNOWLEDGE remains independent from other active teams.

- no requests for another team's judgement;
- no in-progress team verdict used as evidence authority;
- no cross-writes to another team's Issue/workspace;
- stable project decisions/completed historical artifacts may be read as context;
- outputs stored only under Issue #44 / `knowledge/generation-corpus`;
- cross-team handoff only when explicitly requested later.

## Maintenance

After each substantial batch:
- record source/evidence class/language/exact scope/limitations;
- store focused conclusions under `docs/knowledge/research/`;
- refresh this index;
- consolidate stable conclusions periodically into core corpus;
- keep HOLD and superseded interpretations explicit;
- never silently promote PRACTICAL/COMMUNITY into FACT.

## Historical anchors

- `docs/PRODUCT_GOAL_LOCK.md`: original Special-first purpose, still valid.
- `docs/CODEX_IMPLEMENTATION_SPEC_JA_v1.3.md`: early Special-first implementation goal, still structurally aligned.
- Issue #4 / `STAGE_10_KNOWLEDGE_HANDOFF.md`: completed historical pre-Stage10 handoff, not ongoing owner.
- Issue #37: simple generic fixtures are plumbing-only, not representative product calibration.
- Issue #38: semantic/evidence constraints for UI-JA automation.
- Issue #44: ongoing persistent generation-knowledge owner.
