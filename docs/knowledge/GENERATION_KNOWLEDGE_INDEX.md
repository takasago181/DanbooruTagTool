# Generation Knowledge Index

Owner: Issue #44 `[KNOWLEDGE][ONGOING] Persistent generation knowledge corpus for dictionary audit and Stage10`

Branch: `knowledge/generation-corpus`

Status: **ONGOING / GOAL_REBASED / BATCH_A+B_COMPLETE / BATCH_C_NEXT**

## Purpose

This is the restart point for the persistent KNOWLEDGE lane. A new chat must be able to recover current generation knowledge from GitHub without relying on conversational memory.

The corpus is evidence/reference. It does not itself rewrite production data, #32 verdicts, Stage10 scoring, Prompt grammar, or model-family policy.

## Restart order

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 latest comments
4. this file
5. `docs/knowledge/CURRENT_PRODUCT_GOAL_20260909.md`
6. `docs/knowledge/PRODUCT_GOAL_EVOLUTION_20260909.md`
7. `docs/knowledge/KNOWLEDGE_REASSESSMENT_20260909.md`
8. relevant focused research under `docs/knowledge/research/`
9. `docs/knowledge/GENERATION_KNOWLEDGE_CORPUS.md`
10. `docs/knowledge/GENERATION_KNOWLEDGE_SOURCES.md`
11. the requesting Issue only when a later handoff is explicitly requested

## Current product-goal baseline

The original Special-first purpose remains valid; it **expanded rather than reversed**.

Current KNOWLEDGE optimization target:

`short Japanese/English intent -> correct Special Core Dictionary candidate(s) -> minimum useful support/structure -> model-family-appropriate canonical-English Prompt -> safe failure diagnosis -> fewer unnecessary generation iterations`

Primary success criterion:
**reduce manual trial-and-error while preserving semantic correctness, model-family scope, traceability, and safe uncertainty.**

## Evidence classes

- `FACT_EXACT_MODEL`: exact checkpoint/version official/author evidence
- `FACT_GENERAL`: primary research / broadly applicable mechanism evidence
- `CONTROLLED_PRACTICAL`: practical comparison with useful controls
- `PRACTICAL`: useful but incompletely controlled observation
- `COMMUNITY`: hypothesis generator only
- `HOLD`: insufficient/conflicting evidence or needs image test
- `REJECT`: contradicted or unsafe generalization

Language does not determine evidence rank. Mirrors/translations of the same experiment are not independent confirmations.

## Current family coverage

| Family | State | Strongest current knowledge | Major unresolved areas |
|---|---|---|---|
| WAI Illustrious v17 | strong | exact author settings; quality/Negative overloading warning; Hires behavior; practical regional actor-separation evidence | exact Prompt-only relation ceiling, rare-Special exposure/trigger variants, exact support-pruning effect sizes |
| Illustrious XL early | strong | exact quality vocabulary; author warning against conflicting critical composition tags | derivative-specific relation/binding and minimum-sufficient transferability |
| NoobAI XL 1.1 EPS | strong | exact inference regime; native caption order with Special before General | actor/body-site relation grammar, camera support, broad+specific, canonical/Alias response, rare exposure |
| NoobAI V-Pred 1.0 | medium-strong | exact distinction from EPS/inference regime | project-relevant practical composition/binding/pruning evidence |
| Anima | strong | exact formatting/order/profile differences; tag dropout; mixed tag/NL; Gelbooru preference; practical multi-character and hybrid-prompt evidence | exact multi-actor ceiling, profile-specific density/pruning effect sizes, relation reliability |

## Current topic coverage

| Topic | State | Current use |
|---|---|---|
| quality/meta tags | strong, lower research priority | model-conditioned variables; prune excess where exact family evidence supports it |
| frame/camera conflict | strong | same-role composition tags are replacement/ablation candidates, not default stacks |
| visibility vs geometry | medium-strong | observability support can change pose; evaluate the role it is meant to protect |
| actor-target / body-site binding | strong general / medium exact-family | relation correctness is separate from unary concept presence |
| multi-Special composition | strong general / medium exact-family | A_ONLY/B_ONLY before AB; concept competition/mode collision is real |
| support conflict / anti-support | strong general / medium exact-family | semantically compatible support can be neutral or harmful |
| minimum-sufficient Prompt / pruning | **strong general / medium exact-family** | protected semantic nucleus + role-based pruning + leave-one-out ablation + bounded escalation |
| broad + specific | **TEST_REQUIRED** | no universal add/delete rule recovered; pairwise empirical support test only |
| Negative semantic interference | strong mechanism / exact-family TEST_REQUIRED | overlapping Negative can suppress target; exact magnitude must be tested |
| canonical vs model trigger | strong Anima / medium cross-family | canonical/search/alias/trigger remain separate layers |
| prompt/concept density | strong general | semantic workload > raw token count; no global breakpoint |
| A1111/Forge chunking | medium-strong tool evidence | 75-token chunks invalidate a simple 75/77 hard-limit rule; boundary changes are a confound |
| seed sensitivity / repeatability | strong general | one seed proves a case/counterexample, not reliability |
| Hires/img2img/ADetailer confounds | strong mechanism | final repair does not prove base Prompt success |
| ControlNet/regional/Forge Couple | medium-strong | assisted-control lane remains separate from Prompt-only evidence |
| LoRA/personalization interference | strong mechanism / project TEST_REQUIRED | loaded adapters can leak/interfere/carry context priors |
| evaluator/tagger coverage | medium-strong | unary taggers cannot globally ground relation/composite success |
| failure diagnosis | medium-strong | diagnostic tree v1 exists; exact thresholds remain open |

## High-value durable conclusions

1. **Model family is part of the claim identity.** Do not flatten WAI / Illustrious / NoobAI EPS / NoobAI V-Pred / Anima into one grammar.
2. **Canonical identity, Japanese display/search, alias/history, and model trigger are separate layers.** Equal dictionary meaning does not prove equal activation.
3. **Support needs two axes:** semantic role and empirical generation effect. `compatible` does not mean `include`.
4. **Multi-concept failure is not evidence that one tag is unknown.** Test unary concepts before composite diagnosis.
5. **Relation/ownership/body-site binding is distinct from entity presence.**
6. **Negative Prompt is an intervention.** Target-overlapping negatives require controlled removal/ON-OFF evidence.
7. **Seed is evidence identity.** One seed is insufficient for a general reliability claim.
8. **Post-processing/control can rescue a result.** Hires/img2img/ADetailer/regional/ControlNet must be recorded as separate interventions.
9. **LoRA/personalization can introduce interference and hidden context priors.**
10. **Prompt density is competing semantic workload, not token count alone.**
11. **Current Danbooru post_count is not direct model-exposure evidence.**
12. **The product goal is minimum-sufficient reliable assistance, not maximum tag accumulation.**
13. **Minimum sufficient is not shortest.** Preserve the semantic nucleus and high-information relation structure; remove redundant/conflicting support empirically.
14. **Same-role composition support should usually be replaced/tested, not stacked by default.** Exact Illustrious author evidence supports this.
15. **Broad + specific remains empirical.** Do not auto-add a parent/constituent merely because it is semantically related.
16. **A1111/Forge-style long prompts are chunked.** `75/77 tokens = hard project limit` is rejected.
17. **Stop Prompt escalation when all relevant functional support roles have been tested without repeatable benefit; escalate to assisted control/HOLD rather than unrelated tag growth.**

## Failure-diagnosis tree v1

Source:
`docs/knowledge/research/BATCH_A_FALSE_ASSUMPTION_PREVENTION_20260909.md`

Order:
1. traceability
2. semantic identity
3. unary activation
4. composition/binding
5. visibility/geometry
6. Negative collision
7. Prompt competition / anti-support pruning
8. LoRA/personalization
9. multi-seed sensitivity
10. assisted-control ceiling
11. evaluator blindness

Never skip directly from failed final image to `tag unknown`.

## Minimum-sufficient Prompt protocol v1

Source:
`docs/knowledge/research/BATCH_B_MINIMUM_SUFFICIENT_PROMPT_20260909.md`

### Protected semantic nucleus
Do not prune meaning merely to make generation easier:
- selected Special(s)
- intrinsic count/actor/ownership/target/body-site/relation
- intrinsic implement/object/modifier
- model-specific trigger syntax where separately justified

### Research pruning order
1. unrelated decoration / excess aesthetic-quality content
2. duplicate/synonymous representations
3. same-role frame/viewpoint conflicts
4. unproven broad parents/constituents
5. optional context/NL that carries no binding/geometry value
6. visibility/geometry/resource supports one at a time
7. weighting only after structural conflicts are cleaned

### Leave-one-out support ablation
For support set `{s1,s2,...}`, compare the full set against `-s1`, `-s2`, etc. on the same predetermined seeds. Judge target, binding, visibility and collateral errors—not a unary tagger score alone.

No exact statistical KEEP/PRUNE threshold is fixed yet.

## Current HOLD backlog

- exact anatomy/count-changing Negative effect magnitude by family/Special
- NoobAI EPS actor/body-site/camera/visibility behavior
- WAI v17 Prompt-only relation/binding ceiling
- canonical/Alias/Semantic/alternate-trigger response outside exact Anima evidence
- exact prompt-density and simultaneous-Special breakpoints
- exact effect of `fully visible / clearly visible / unobstructed / in frame / body part focus`
- project-specific LoRA x Special/support rules
- robust left/right ownership by family
- **project-specific seed/sample-count protocol and uncertainty rule**
- exact KEEP/MIXED/PRUNE evidence threshold for support ablation
- precise Prompt-only -> assisted-control escalation threshold
- local success/failure-history confidence rules

## Reassessment map

`docs/knowledge/KNOWLEDGE_REASSESSMENT_20260909.md` classifies prior knowledge as:
`KEEP_CORE / MODEL_ONLY / DOWNGRADE / TEST_REQUIRED / OBSOLETE_AS_GOAL / REJECT / MISSING`.

Major priority shift:
generic sampler/aesthetic micro-optimization is downgraded; conflict prevention, minimum-sufficient support, relation/binding, failure diagnosis, seed reliability and model-specific adverse guidance are higher priority.

## Research batches

### Batch A — false-assumption prevention
**COMPLETE first durable pass**

- `docs/knowledge/research/BATCH_A_FALSE_ASSUMPTION_PREVENTION_20260909.md`
- `docs/knowledge/research/BATCH_A_SOURCES_20260909.md`

Main gains:
failure diagnosis; concept competition; relation binding; trigger drift; Negative collision; seed sensitivity; LoRA confounding; assisted-control separation.

### Batch B — minimum-sufficient Prompt / pruning
**COMPLETE first durable pass**

- `docs/knowledge/research/BATCH_B_MINIMUM_SUFFICIENT_PROMPT_20260909.md`
- `docs/knowledge/research/BATCH_B_SOURCES_20260909.md`

Main gains:
- minimum-sufficient definition;
- semantic nucleus protection;
- two-axis support model;
- pruning order v1;
- leave-one-out ablation;
- role-bounded stopping principle;
- A1111/Forge chunk-boundary caution;
- exact model pruning constraints for WAI/Illustrious/NoobAI/Anima;
- broad+specific remains explicitly HOLD/TEST_REQUIRED.

### Batch C — evidence reliability / remaining confounds
**NEXT**

Targets:
1. project-appropriate predetermined seed/sample protocol
2. evidence hierarchy for `KEEP / MIXED / PRUNE` support conclusions
3. pairwise/human judgement uncertainty
4. evaluator false-positive/false-negative effects on pruning
5. LoRA x Special/support practical interactions
6. deterministic local success/failure history without semantic-authority contamination
7. assisted-control evidence identity and stopping decision refinement

### Batch D — lower priority
**PENDING**

- aesthetic/quality refinements not already relevant to target success
- generic sampler micro-optimization

## Independence mode

Current user instruction: KNOWLEDGE works independently from other active teams.

During this mode:
- no requests for another team's judgement;
- no use of an in-progress team verdict as evidence authority;
- no cross-writes to another team's Issue/workspace;
- stable project decisions and completed historical artifacts may be read as context;
- research outputs are stored only under Issue #44 / `knowledge/generation-corpus`;
- cross-team handoff occurs only when explicitly requested later.

## Maintenance rules

After a substantial research batch:
- record sources, evidence class, language, exact scope and limitations;
- store focused conclusions under `docs/knowledge/research/`;
- refresh this index;
- periodically consolidate stable conclusions into the core corpus;
- keep HOLD explicit;
- preserve superseded history and explain why;
- never silently promote PRACTICAL/COMMUNITY into FACT.

## Historical anchors

- `docs/PRODUCT_GOAL_LOCK.md`: original Special-first purpose lock; still structurally valid.
- `docs/CODEX_IMPLEMENTATION_SPEC_JA_v1.3.md`: early/frozen Special-first implementation goal; still aligned.
- Issue #4 / `docs/stages/STAGE_10_KNOWLEDGE_HANDOFF.md`: historical completed pre-Stage10 handoff, not ongoing owner.
- Issue #37: simple `standing/sitting/long_hair/smile` fixtures are plumbing-only, not representative product calibration.
- Issue #38: semantic/evidence constraints for translation automation.
- Issue #44: ongoing persistent generation-knowledge owner.
