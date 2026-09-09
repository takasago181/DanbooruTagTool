# Generation Knowledge Index

Owner: Issue #44 `[KNOWLEDGE][ONGOING] Persistent generation knowledge corpus for dictionary audit and Stage10`

Branch: `knowledge/generation-corpus`

Status: ONGOING / GOAL_REBASED / BATCH_A_COMPLETE

## Purpose

This index is the restart point for the persistent KNOWLEDGE lane. It exists so a new chat can recover current generation knowledge from GitHub without depending on conversational memory.

The knowledge corpus is evidence/reference. It does not itself rewrite production data, #32 verdicts, Stage10 scoring, Prompt grammar, or model-family policy.

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
11. the current requesting Issue when/if a later handoff is explicitly requested

## Current product-goal baseline

The original Special-first purpose remains valid; it has **expanded rather than reversed**.

Current KNOWLEDGE optimization target:

`short Japanese/English intent -> correct Special Core Dictionary candidate(s) -> minimum useful support/structure -> model-family-appropriate canonical-English Prompt -> safe failure diagnosis -> fewer unnecessary generation iterations`

Primary success criterion:
**reduce manual trial-and-error while preserving semantic correctness, model-family scope, traceability, and safe uncertainty.**

Detailed baseline:
- `docs/knowledge/CURRENT_PRODUCT_GOAL_20260909.md`
- `docs/knowledge/PRODUCT_GOAL_EVOLUTION_20260909.md`

## Evidence classes

- `FACT_EXACT_MODEL`: exact checkpoint/version official or author evidence
- `FACT_GENERAL`: primary research / broadly applicable mechanism evidence
- `CONTROLLED_PRACTICAL`: practical comparison with useful controls
- `PRACTICAL`: useful but incompletely controlled observation
- `COMMUNITY`: hypothesis generator only
- `HOLD`: insufficient/conflicting evidence or needs image test
- `REJECT`: contradicted or unsafe generalization

Language does not determine evidence rank. Translations/mirrors of one experiment are not counted as independent confirmations.

## Current family coverage

| Family | Current state | Strongest current knowledge | Major unresolved areas |
|---|---|---|---|
| WAI Illustrious v17 | strong | exact author settings, quality/negative cautions, Hires behavior; practical Forge Couple actor-separation evidence | exact Prompt-only relation ceiling, rare-Special exposure, trigger variants, support pruning |
| Illustrious XL early | strong | official quality vocabulary and composition-tag conflict warning | derivative-specific relation binding and minimum-sufficient support transferability |
| NoobAI XL 1.1 EPS | strong | exact CFG/Steps/Euler a/resolution and native caption order | exact actor/body-site relation grammar, camera ordering, canonical/Alias response, rare exposure |
| NoobAI V-Pred 1.0 | medium-strong | exact distinction from EPS and inference regime | practical composition/binding evidence at project-relevant complexity |
| Anima | strong | exact tag format/order/profile differences, tag/NL coexistence, Gelbooru preference; practical multi-character failure/repair evidence | relation reliability, multi-actor ceiling, profile-specific density/pruning |

## Current topic coverage

| Topic | State | Audit/product usefulness |
|---|---|---|
| quality/meta tags | strong but lower research priority | treat as semantic/style variables; prioritize only when they affect Special success/composition |
| frame/camera conflict | strong | detect Prompt conflict before blaming Special semantics |
| visibility vs geometry | medium-strong | visibility support can change pose/geometry; not a neutral no-op |
| actor-target / multi-character binding | strong general / medium exact-family | relation binding is distinct from unary recognition; exact WAI/NoobAI evidence still needed |
| multi-Special composition | strong general / medium exact-family | A_ONLY/B_ONLY before AB; concept competition/mode collision is a real failure class |
| support conflict / anti-support | medium-strong after Batch A | semantically compatible support can still be generation-harmful |
| minimum sufficient Prompt / pruning | weak-medium | next major research target |
| negative semantic interference | strong mechanism / exact-family TEST_REQUIRED | overlapping Negative can suppress intended concepts; magnitude requires family tests |
| canonical vs model trigger | strong for Anima / medium cross-family | exact Anima Gelbooru preference + rename examples; cross-family trigger drift unresolved |
| prompt/concept density | strong general | count concepts/relations/bindings, not only tokens; no global breakpoint |
| seed sensitivity / evaluation repeatability | strong general | seed affects composition; one seed is not a reliability estimate |
| Hires / img2img / ADetailer confounds | strong mechanism | final-pass repair does not prove base Prompt success |
| ControlNet / regional / Forge Couple assisted control | medium-strong | separate assisted-control lane; assisted success does not certify Prompt-only success |
| LoRA interference | strong mechanism / project TEST_REQUIRED | multi-LoRA/personalized concepts can leak/interfere; exact project rules unresolved |
| broad + specific tags | medium | plausible reinforcement/dilution/conflict; Batch B target |
| evaluator/tagger coverage | medium-strong | simple classifiers cannot ground rare/relation/composite success globally |
| failure diagnosis | medium-strong after Batch A | durable diagnostic tree v1 exists; exact-family thresholds still missing |

## High-value durable conclusions

1. **Model family is part of the claim identity.** Never flatten WAI / Illustrious / NoobAI EPS / NoobAI V-Pred / Anima into one Prompt grammar.
2. **Canonical identity, Japanese display/search wording, and model trigger spelling are separate layers.** Equal dictionary meaning does not prove equal generation response.
3. **Support is typed and also needs an effect axis.** Meaning/Geometry/Visibility/Resource/Aesthetic classification does not guarantee a support is beneficial; semantically compatible support may be redundant or harmful.
4. **A multi-concept failure is not evidence that a single tag is unknown.** Test unary concepts before diagnosing composite failure.
5. **Relation binding is distinct from concept presence.** Actor-target/body-site/ownership correctness must be evaluated separately from entity/tag presence.
6. **Negative Prompt terms are interventions.** A target overlapping the Negative must not be judged weak without controlled removal/ON-OFF evidence.
7. **Seed is part of composition evidence identity.** One seed can demonstrate a case/counterexample; it cannot estimate general reliability.
8. **Post-processing/control can rescue a result.** Hires, img2img, ADetailer, ControlNet, regional prompting and similar interventions belong in evidence metadata and separate lanes.
9. **LoRA/personalization can introduce interference and hidden context priors.** LoRA-loaded evidence cannot be attributed solely to the base Special/support Prompt.
10. **Prompt density is about competing concepts/relations, not token count alone.**
11. **Current Danbooru post_count is not direct model-exposure evidence.** Training date/source/normalization/tag history matter.
12. **Human/controlled review remains required for rare, relational, body-site-binding and multi-Special cases when automatic evaluators lack semantic reach.**
13. **The product goal is minimum sufficient reliable assistance, not maximum tag accumulation.**

## Failure-diagnosis tree v1

Detailed source:
`docs/knowledge/research/BATCH_A_FALSE_ASSUMPTION_PREVENTION_20260909.md`

High-level order:
1. traceability gate
2. semantic identity
3. single-concept activation
4. composition/binding comparison
5. visibility/geometry
6. Negative collision
7. Prompt competition / anti-support pruning
8. LoRA/personalization
9. multi-seed sensitivity
10. assisted-control ceiling
11. evaluator blindness

Do not skip directly from failed final image to “tag unknown.”

## Current HOLD backlog

- anatomy-sensitive Negative ON/OFF for unusual anatomy/count-changing Specials
- exact NoobAI EPS 1.1 actor/body-site/camera/visibility support behavior
- WAI v17 Prompt-only relation/binding ceiling
- canonical / Alias / Semantic generation-response equality or ranking outside exact Anima evidence
- exact family-specific prompt-density breakpoint
- exact simultaneous Special-count breakpoint
- `fully visible / clearly visible / unobstructed / in frame / body part focus` family-specific effect
- project-specific LoRA interaction rules
- precise threshold for abandoning Prompt-only and escalating to regional/ControlNet assistance
- robust multi-character left/right ownership by target family
- Stage10 project-specific seed/sample-count protocol
- empirically justified minimum-sufficient support/pruning rules

## Reassessment map

`docs/knowledge/KNOWLEDGE_REASSESSMENT_20260909.md` classifies prior knowledge as:
- KEEP_CORE
- MODEL_ONLY
- DOWNGRADE
- TEST_REQUIRED
- OBSOLETE_AS_GOAL
- REJECT
- MISSING

Major priority change:
Generic sampler/aesthetic micro-optimization is downgraded. Conflict prevention, minimum-sufficient support, relation/binding, failure diagnosis, seed reliability and model-specific adverse guidance are higher priority.

## Research batches

### Batch A — false-assumption prevention
**Status: COMPLETE first durable pass**

Files:
- `docs/knowledge/research/BATCH_A_FALSE_ASSUMPTION_PREVENTION_20260909.md`
- `docs/knowledge/research/BATCH_A_SOURCES_20260909.md`

Improved gaps:
- failure diagnosis: partial -> medium-strong
- seed/sample reliability: strong general evidence
- actor-target/body-site: strong general + useful Anima practical, WAI/NoobAI exact gaps remain
- trigger drift: strong Anima evidence, cross-family gap remains
- LoRA interference: mechanism strongly supported, project specifics remain TEST_REQUIRED
- assisted-control boundary: sequence proposed, threshold still HOLD

### Batch B — minimum sufficient Prompt / pruning
**Status: NEXT**

Targets:
1. required vs redundant support
2. support conflict/anti-support removal order
3. broad parent + specific Special interaction
4. concept density vs raw token count
5. model-family support ordering/weighting only where evidence supports it
6. evidence needed to remove a support candidate safely
7. stopping rule for Prompt additions -> assisted control

### Batch C — evidence reliability / remaining confounds
**Status: PENDING**

Targets:
- project-specific multi-seed protocol
- evaluator uncertainty/human-vs-machine boundary
- LoRA x Special/support practical interactions
- assisted-control threshold refinement
- local empirical history interpretation

### Batch D — lower priority
**Status: PENDING**

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
- create/update source registry with evidence class and exact scope;
- store focused durable conclusions under `docs/knowledge/research/`;
- update this index for coverage/state changes;
- periodically consolidate stable conclusions into the core corpus;
- retain HOLD explicitly;
- if a prior conclusion is superseded, keep the history and state why;
- never silently convert PRACTICAL/COMMUNITY into FACT.

## Historical anchors

- `docs/PRODUCT_GOAL_LOCK.md`: original Special-first purpose lock; still structurally valid.
- `docs/CODEX_IMPLEMENTATION_SPEC_JA_v1.3.md`: early/frozen Special-first implementation goal; still structurally aligned.
- Issue #4 completed Stage10 pre-start KNOWLEDGE research; historical handoff remains `docs/stages/STAGE_10_KNOWLEDGE_HANDOFF.md`.
- Issue #37 established that simple `standing/sitting/long_hair/smile` fixtures are plumbing-only, not representative Special-centered calibration.
- Issue #38 established semantic/evidence constraints for translation automation.
- Issue #44 is the ongoing persistent knowledge corpus and should remain open across stages.
