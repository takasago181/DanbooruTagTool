# Hard Adult Challenge v1

Status: FROZEN DESIGN / quarantine-only
Scope: adult-only semantic/search + future generation stress evaluation
Parent work: Issue #41 UI-JA R3 pilot

## Purpose

This challenge exists because the fresh100 R3 pilot is a general semantic/search safety gate, not a representative sample of the user's primary adult hard-tag use case.

The challenge asks two separate questions:

1. Can Japanese display/search automation preserve the exact Special2788 canonical meaning without sibling collision?
2. After semantic/search safety is proven, can model-family-specific Prompt automation make the selected hard Special observable in generated images without hiding failure behind excessive support tags?

The challenge MUST NOT be used to rewrite production `data/**`, change canonical identity, promote #32 verdicts, or start Stage10 production A/B.

## Source-of-truth inputs

### Existing Special2788 category structure
Use the existing prompt-reference categories as the sampling universe, not a newly invented taxonomy.

Primary v1 strata:
- `01 身体・解剖`
- `04 性行為・性的刺激`
- `05 挿入・性具・機械`
- `06 拘束・BDSM・支配`
- `07 体液・排泄・汚損`
- `08 異形・触手・非人間`
- `09 生殖・妊娠・授乳`

The main adult dictionaries already preserve Layer identity:
- Core (`C`)
- Extended (`E`)
- Alias (`A`)
- Semantic (`S`)

Alias/Semantic rows are retrieval/context evidence only. They are not automatically equal to canonical model response and are not semantic authority.

### PROMPT / KNOWLEDGE constraints incorporated

From the Stage10 KNOWLEDGE handoff and Issue #4/#38 lane returns:

- Japanese display and Japanese search are separate artifacts.
- False READY is worse than high REVIEW.
- Canonical meaning is established before Japanese wording.
- Broad Japanese genre words must not silently resolve to one canonical when several sibling meanings are plausible.
- Meaning support, Geometry/Kinematic support, Visibility support, Resource parking/disambiguation support, and Aesthetic support are separate roles.
- Multiple-Special failure must be separated into recognition, single-concept, compositional/binding, and visibility/crop/occlusion failure.
- NoobAI / WAI Illustrious / Illustrious / Anima remain separate Prompt families.
- Do not globally inject `8k`, `ultra detailed`, `sharp focus`, anatomy-negative boilerplate, or `safe/nsfw` negative conventions.
- Current Danbooru post_count is not proof of checkpoint training strength.
- `canonical / Alias / Semantic` identity in the dictionary does not prove equal model response; that remains a generation-side experiment.

Hard-domain KNOWLEDGE guidance is adopted as test structure:
- Anal: separate body-site / broad act / specific action / object / relation.
- Japanese `調教`: decompose to visible primitives; never auto-map to generic `training`.
- Machine-sex intent: separate machine identity / restraint geometry / connector-object / body-site / action.
- Tentacle: test existence -> contact/grab -> restraint/binding -> body-region relation -> specific act -> multi-Special.
- Excretion/scat: separate material/object recognition / excretion action / contamination/contact state / actor-target relation / compound state.

## Fixed canonical challenge set

`hard_adult_challenge_v1.jsonl` contains 64 rows.

Quota:
- Anatomy boundary: 6
- Sexual action: 10
- Insertion / toys / machine: 12
- Bondage / BDSM / domination: 12
- Fluids / excretion / contamination: 12
- Tentacle / nonhuman: 8
- Reproduction / lactation: 4

Selection is intentionally not proportional to category size. It over-samples sibling-collision and relation/body-site cases because these are the failure modes most damaging to Japanese retrieval.

## Ambiguous Japanese trap set

`hard_adult_ambiguity_probes_v1.jsonl` contains 16 Japanese probes.

These are not translation-answer rows. They test whether automation refuses false one-to-one mappings.

Expected behaviors:
- `RESOLVE_ONE`: one exact canonical is supported.
- `RETURN_SET`: several plausible canonicals should be surfaced.
- `REVIEW_DECOMPOSE`: Japanese genre/concept word is broader than any one canonical and should be decomposed to visible primitives or reviewed.

Example principle:
- `肛門` may resolve to body-site `anus`.
- `アナルセックス` may resolve to sexual-action `anal`.
- broad `アナル` must not silently collapse body-site, act, fingering, object insertion, etc. into one result.
- broad `調教` must not auto-resolve to a made-up generic canonical; it should expose concrete BDSM/restraint/role candidates.
- broad `機械姦` must distinguish `sex_machine`, machine/robot partner semantics, machine penetration, and restraint geometry rather than asserting one identity.
- broad `スカトロ` must not collapse `scat`, `defecating`, `pseudo_scat`, `human_toilet`, urine-related concepts, etc. into one synonym.

## Phase A — semantic / UI-JA gate

For every fixed canonical row, automation records independently:
- `display_ja`
- `search_ja[]`
- term class
- semantic evidence
- exact/broad/rejected search relation
- sibling collision candidates
- effective risk class
- READY / REVIEW

Required failure checks:
1. body-site lost
2. actor lost/added
3. target lost/added
4. action <-> state collapse
5. object <-> action collapse
6. parent/child collapse
7. broad genre word -> single canonical false resolve
8. count/cardinality change
9. inside/on/outside relation loss
10. consent/relation qualifier loss when encoded by canonical

Hard Adult semantic PASS requires:
- semantic false READY = 0
- search false READY = 0
- body-site/actor/target silent loss = 0
- broad-trap false one-to-one resolve = 0
- unresolved evidence is REVIEW, not guessed READY

## Phase B — generation knowledge attachment

Only after Phase A semantic safety, attach Prompt-generation evidence. This phase consumes PROMPT/KNOWLEDGE artifacts; it must not redefine canonical meaning.

Each challenge row can receive:
- `meaning_support[]`
- `geometry_kinematic_support[]`
- `visibility_support[]`
- `relation_support[]`
- `resource_parking_support[]`
- `aesthetic_support[]`
- `negative_experiment_flags[]`

Support entries require provenance and model-family scope.

## Phase C — model-family stress matrix

Run separately for:
- WAI Illustrious v17
- Illustrious
- NoobAI XL 1.1 EPS
- NoobAI XL V-Pred 1.0 when applicable
- Anima Base / Aesthetic / Turbo as separate profiles when applicable

Do not assume one grammar.

Per row, start minimal and escalate one support role at a time:

- `G0`: canonical Special only in family baseline
- `G1`: + Meaning support, if evidence says required
- `G2`: + Geometry/Kinematic support
- `G3`: + Visibility support
- `G4`: + Relation / Resource parking support
- `G5`: + Aesthetic support (Stress mode only)

For compound tests:
- `A_ONLY`
- `B_ONLY`
- `AB_MINIMAL`
- optional `BA`
- `AB + Frame`
- `AB + Viewpoint`
- `AB + targeted Geometry/Visibility/Relation`

Never add multiple support classes at once when the goal is causal attribution.

## Generation failure classes

Every image result must classify failure before any new support is added:

- `EXPOSURE_RECOGNITION_FAILURE`: model does not visibly express the concept
- `SINGLE_CONCEPT_FAILURE`: row fails alone
- `COMPOSITIONAL_BINDING_FAILURE`: A/B work alone but merge/drop/misbind together
- `VISIBILITY_FAILURE`: concept may exist but crop/occlusion/frame prevents judgement
- `WRONG_SIBLING_FAILURE`: visible result corresponds to a sibling canonical
- `OVER_SUPPORT_FAILURE`: support changed the intended Special meaning or introduced another concept

## Automation-ready metadata

Future runner should persist at minimum:
- challenge_id
- category / Special ID / canonical / Layer / source post_count
- Japanese query used
- resolved canonical set
- display/search decision
- exact model + checkpoint version
- positive Prompt actual output
- Negative Prompt actual output
- Seed / resolution / sampler / scheduler / Steps / CFG
- support blocks by role
- LoRA name + weight if explicitly in the experiment lane
- condition ID (`G0..G5`, `A_ONLY`, etc.)
- generated artifact identity
- judgement
- failure class
- deterministic run/replay hashes

## Automation target

The intended end state is:

`Special2788 category -> challenge sampler -> semantic/UI-JA resolver -> ambiguity gate -> model-family Prompt builder -> local generation runner -> result collector -> failure classifier -> review/metrics -> only then bulk automation`

The automation must preserve quarantine boundaries until the challenge gate passes. This challenge does not authorize bulk remaining-P0 processing by itself.

## Pass policy before bulk automation

The future bulk gate should require both:

### Semantic gate
- 0 false READY
- 0 false search synonym approval
- 0 broad-trap silent single resolve
- deterministic replay PASS

### Generation gate
- results stored with exact model metadata
- failure classified rather than patched blindly
- no cross-family Prompt rule promoted without evidence
- at least one meaningful sample from every v1 hard-domain stratum
- rare/Extended rows represented, not Core-only success

If a failure reveals a general rule, update the rule and revalidate every matching challenge row; do not patch only the sampled tag.
