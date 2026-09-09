# Failure Diagnosis, Testing and Evaluation

## Diagnose before blaming the tag

Use this order when a target is missing or wrong:

1. `TRACEABILITY` — exact model/version/settings/Prompt/seed known?
2. `IDENTITY_EXPOSURE` — spelling/canonical/Alias/trigger issue?
3. `UNARY_REALIZATION` — can the concept appear alone?
4. `COMPOSITION_BINDING` — does it fail only with other concepts/actors?
5. `VISIBILITY_GEOMETRY` — is the target cropped/occluded/physically impossible?
6. `PROMPT_CONTRADICTION` — frame/viewpoint/pose/support conflict?
7. `NEGATIVE_COLLISION` — does Negative overlap the intended concept?
8. `PROMPT_DENSITY` — concept/support pressure or broad-parent dominance?
9. `LORA_PERSONALIZATION` — adapter context/interference?
10. `SEED_SENSITIVITY` — isolated seed effect?
11. `POSTPROCESS_CONTROL` — did Hires/inpaint/regional control rescue/change it?
12. `EVALUATOR_BLINDNESS` — image may be right but machine judge cannot represent the relation.

## Failure classes

- F1 identity/exposure failure
- F2 single-concept realization failure
- F3 composition/competition failure
- F4 binding/ownership failure
- F5 visibility/crop/occlusion failure
- F6 Prompt contradiction
- F7 Negative collision
- F8 model-family/settings mismatch
- F9 postprocess/control confound
- F10 evaluator blindness.

## Evidence-strength ladder

### E0 — Case/debug
One/few predetermined examples. Useful for mechanism/counterexample, not reliability.

### E1 — Repeatability
Predetermined paired seeds, all outputs retained, no cherry-picking.

### E2 — Comparative inference
Predeclared sample, paired analysis, uncertainty, effect size/practical usefulness, explicit TIE/UNCLEAR handling.

### E3 — Generalization
Multiple representative semantic cases and relevant model scopes before promoting a reusable rule.

There is no context-free `N seeds = proven` rule.

## Paired A/B outcome states

Preserve at least:
- `A_ONLY_PASS`
- `B_ONLY_PASS`
- `BOTH_PASS`
- `BOTH_FAIL`
- `TIE`
- `UNCLEAR`
- `BLOCKED`.

Relative A/B improvement and absolute success reliability are separate. `BOTH_FAIL` may not determine directional superiority but is important product evidence.

## Experiment discipline

- one experiment = one primary question
- same seed/settings for paired comparisons where possible
- change one meaningful variable at a time
- preserve actual Positive/Negative Prompt strings
- preserve checkpoint/hash, sampler, steps, CFG, resolution
- preserve all loaded LoRAs/weights
- record Hires/ADetailer/img2img/control separately
- do not keep only successful images.

## Evaluator capability gate

Before interpreting a machine score:
1. Is the target in its vocabulary / representable?
2. Is the semantic class appropriate for that evaluator?
3. Is the exact version/calibration/threshold known?
4. Is the image OOD/unusual for the evaluator?
5. Does human review contradict the machine?

## Tagger roles

Unary taggers are useful for common visual presence/attributes. They are weak as sole ground truth for:
- rare tags
- relation/body-site ownership
- restraint topology
- source-destination
- exact simultaneous count
- compound Special retention
- Alias equivalence.

Current evaluator knowledge:
- WD EVA02 v3: common/unary baseline; tags under its filtering threshold create structural coverage gaps
- Kagami-24k: wider vocabulary candidate, rare-tail reliability still separate
- CL Tagger v2: wide vocabulary, per-tag calibration/threshold/OOD information; still not relation ground truth
- full Special2788 comparative coverage remains queued for after dictionary finalization.

## Primary originals

- `../research/BATCH_C_EVIDENCE_RELIABILITY_20260909.md`
- `../research/BATCH_C_SOURCES_20260909.md`
- `../GENERATION_KNOWLEDGE_CORPUS.md` sections 7–9
- `../research/BATCH_A_FALSE_ASSUMPTION_PREVENTION_20260909.md`