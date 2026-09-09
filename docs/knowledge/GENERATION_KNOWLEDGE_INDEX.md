# Generation Knowledge Index

Owner: Issue #44 `[KNOWLEDGE][ONGOING] Persistent generation knowledge corpus for dictionary audit and Stage10`

Branch: `knowledge/generation-corpus`

Status: ONGOING

## Purpose

This index is the restart point for the persistent KNOWLEDGE lane. It exists so a new chat can recover current generation knowledge from GitHub without depending on conversational memory.

The knowledge corpus is evidence/reference. It does not itself rewrite production data, #32 verdicts, Stage10 scoring, Prompt grammar, or model-family policy.

## Restart order

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 latest comments
4. this file
5. `docs/knowledge/GENERATION_KNOWLEDGE_CORPUS.md`
6. `docs/knowledge/GENERATION_KNOWLEDGE_SOURCES.md`
7. the current requesting Issue (#32 / #42 / Stage10 / UI-JA bridge etc.)

## Evidence classes

- `FACT_EXACT_MODEL`: exact checkpoint/version official or author evidence
- `FACT_GENERAL`: primary research / broadly applicable mechanism evidence
- `CONTROLLED_PRACTICAL`: practical comparison with useful controls
- `PRACTICAL`: useful but incompletely controlled observation
- `COMMUNITY`: hypothesis generator only
- `HOLD`: insufficient/conflicting evidence or needs image test
- `REJECT`: contradicted or unsafe generalization

Language does not determine evidence rank.

## Current family coverage

| Family | Current state | Strongest current knowledge | Major unresolved areas |
|---|---|---|---|
| WAI Illustrious v17 | strong | exact author settings, quality/negative cautions, Hires behavior | exact camera/visibility placement, rare-Special exposure, model-specific trigger variants |
| Illustrious XL early | strong | official quality vocabulary and composition-tag conflict warning | exact downstream-finetune transferability, relation binding limits by derivative |
| NoobAI XL 1.1 EPS | strong | exact CFG/Steps/Euler a/resolution and native caption order | exact camera ordering, canonical/Alias response equivalence, rare tag exposure |
| NoobAI V-Pred 1.0 | medium-strong | exact distinction from EPS and inference regime | practical composition/binding evidence at current project usage |
| Anima | strong | exact tag format, order, profile differences, tag/NL coexistence, trigger spelling differences | exact relation reliability, multi-actor ceiling, profile-specific prompt density |

## Current topic coverage

| Topic | State | Audit usefulness |
|---|---|---|
| quality/meta tags | strong | treat as semantic/style variables, not transparent quality switches |
| frame/camera conflict | strong | detect Prompt conflict before blaming Special semantics |
| visibility vs geometry | medium-strong | visibility support can change pose/geometry; do not call it a neutral no-op |
| actor-target / multi-character binding | strong general / medium exact-family | separate composition failure from tag-unknown failure |
| multi-Special composition | medium-strong | A_ONLY/B_ONLY before AB; support escalation in steps |
| negative semantic interference | medium-strong | anatomy/count negatives are high-risk when target concept overlaps |
| canonical vs model trigger | medium-strong | canonical identity and model trigger spelling must remain separate |
| prompt/concept density | strong general | count concepts/relations, not only tokens; open-model performance drops as concepts increase |
| Hires / img2img / ADetailer confounds | strong mechanism | final-pass repair does not prove base Prompt success |
| ControlNet / OpenPose assisted control | strong mechanism | separate assisted-control lane from Prompt-only baseline |
| LoRA interference | medium | fixed-prompt/seed comparison required; trigger is not a hard on/off switch |
| broad + specific tags | medium | useful disambiguation candidate; exact-family effect requires controlled A/B |
| evaluator/tagger coverage | medium | simple tag classifiers cannot be ground truth for rare/relation/composite Specials |

## High-value durable conclusions

1. **Model family is part of the claim identity.** Never flatten WAI / Illustrious / NoobAI EPS / NoobAI V-Pred / Anima into one Prompt grammar.
2. **Canonical identity, Japanese display/search wording, and model trigger spelling are separate layers.** Equal dictionary meaning does not prove equal generation response.
3. **Support is typed.** Meaning support, Geometry/Kinematic, Visibility, Resource parking/disambiguation, Aesthetic support, and redundant decoration must not be conflated.
4. **A multi-concept failure is not evidence that a single tag is unknown.** Test single concepts before composite failure diagnosis.
5. **Negative Prompt terms are interventions.** A target overlapping the negative must not be judged weak without an ON/OFF comparison.
6. **Post-processing/control can rescue a result.** Hires, img2img, ADetailer, ControlNet, regional prompting and similar interventions belong in evidence metadata.
7. **Prompt density is about competing concepts/relations, not token count alone.**
8. **Human/controlled review remains required for rare, relational, body-site-binding and multi-Special cases when automatic evaluators lack vocabulary/semantic reach.**

## Current HOLD backlog

- anatomy-sensitive Negative ON/OFF for unusual anatomy/count-changing Specials
- exact NoobAI EPS 1.1 camera/visibility optimization
- canonical / Alias / Semantic generation-response equality or ranking
- exact family-specific prompt-density breakpoint
- exact simultaneous Special-count breakpoint
- `fully visible / clearly visible / unobstructed / in frame / body part focus` family-specific effect
- LoRA interaction rules that generalize across checkpoints
- precise threshold for abandoning Prompt-only and escalating to regional/ControlNet assistance
- robust multi-character left/right ownership in Anima and other target families

## Research priorities before final dictionary audit use

Priority A — audit false-PASS prevention:
- unusual anatomy + Negative collisions
- actor-target/body-site binding
- support-class misclassification (meaning vs visibility/geometry)
- post-processing rescue confounds
- alias/model-trigger/canonical confusion

Priority B — model-specific Prompt support:
- NoobAI EPS exact camera/framing
- WAI v17 support/quality interactions
- Anima tag-only vs hybrid short-NL relation behavior
- multi-Special composition under each target family

Priority C — Stage10 evaluator design:
- tagger vocabulary/coverage by final Special dictionary
- automatic vs REVIEW routing by semantic class
- failure classification from multiple evaluator signals

## Maintenance rules

After a substantial research batch:
- update sources first;
- update the consolidated corpus;
- update this index only for coverage/state changes;
- retain HOLD explicitly;
- if a prior conclusion is superseded, keep the history and state why;
- never silently convert PRACTICAL/COMMUNITY into FACT.

## Historical anchors

- Issue #4 completed Stage10 pre-start KNOWLEDGE research.
- `docs/stages/STAGE_10_KNOWLEDGE_HANDOFF.md` is the historical Stage10 handoff snapshot.
- Issue #37 established that simple `standing/sitting/long_hair/smile` fixtures are plumbing-only, not representative Special-centered calibration.
- Issue #38 established semantic/evidence constraints for translation automation.
- Issue #44 is the ongoing knowledge corpus and should remain open across stages.
