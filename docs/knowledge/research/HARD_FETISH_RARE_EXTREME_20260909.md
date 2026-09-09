# Hard Fetish Generation Knowledge — Rare / Extreme / Anatomy-Changing Concepts

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `DEEP_RESEARCH_V1 / evidence-reference`

## 1. Scope

成人・合意下の rare / extreme / anatomy-changing Special を対象に、**モデルが普通の人体・頻出構図へ引き戻そうとする力**、rare-token exposure、Negative衝突、評価器coverage不足を重点的に整理する。

Representative project concepts:
- `anal fisting` Extended / 345
- `fisting` Extended / 600
- `large insertion` Core / 3183
- `multiple insertions` Extended / 422
- `self fisting` Extended / 60
- `inflation` Core / 3670
- `stomach bulge` Core / 16749
- `urethral beads` Extended / 335
- `urethral fingering` Extended / 143
- `urethral insertion` Core / 1758
- `urethral penetration` Extended / 57
- Semantic urethral dilation/sounding/play terms
- `triple anal` Extended / 94
- `multiple penetration` Extended / 70
- rare restraint topology such as `shrimp tie` 82 / `strappado` 144
- rare machine relations such as `mecha on girl` 79 / `riding machine` 105 / `sybian` 148
- rare tentacle concepts such as `tentacle dildo` 50 / `tentacle masturbation` 92.

## 2. Four independent rarity questions

A concept can be difficult for different reasons. Keep these separate.

### `TOKEN_RARITY`
Was the exact token/form likely present in training?

### `VISUAL_RARITY`
Even if the text token existed, is the requested visual configuration itself uncommon?

### `COMPOSITION_RARITY`
Are otherwise common entities combined in an unusual relation/count/site?

### `EVALUATOR_RARITY`
Can the automatic evaluator recognize the target at all?

Current Danbooru post_count is only a triage signal. It is not exact model-exposure probability because training cutoff, aliases, caption normalization, source mix and later tag history differ.

## 3. Rare-concept generation evidence

Primary research on rare concepts finds that diffusion models underrepresent long-tail concepts and that suitable seed selection can materially improve rare-concept fidelity without retraining.

Later rare-composition research shows that exposing more frequent concepts related to the rare target can improve composition. The DanbooruTagTool does **not** adopt runtime LLM guidance from that work, but does adopt the experimental lesson:

> rare target + one carefully chosen frequent constituent/support is worth controlled A/B testing.

This does not make the constituent part of canonical meaning.

## 4. Common-knowledge bias

Recent 2026 rare-concept research frames another failure: the model's common-knowledge prior can overpower unusual attributes/configurations.

Project interpretation:
- an unusual target may collapse into the nearest familiar visual state;
- repeatedly strengthening the rare word may not fix structural conflict;
- more frequent related support can help in some cases but can also erase the rare modifier;
- exact-family image tests remain necessary.

## 5. Anatomy-changing concepts

These require careful separation of:

### Intended deviation
The target itself departs from ordinary anatomy/distribution.

### Unwanted artifact
Broken hands, fused limbs, impossible duplicated human body parts, malformed unrelated anatomy.

A generic `bad anatomy` score/Negative can conflate these.

Audit requirement:
- define target anatomy predicates before generation;
- judge intended deviation independently from unrelated artifacts;
- never equate “looks normal” with success for an anatomy-changing target.

## 6. Negative Prompt collision matrix

### High collision risk
- extra/multiple appendage-like concepts
- unusual openings/states
- extreme stretching/enlargement/inflation
- complex restraint poses
- multi-implement/body-site configurations.

### Lower collision risk
- simple unary device/object when human anatomy remains ordinary.

### Required experimental design
For high-risk cases:
1. minimal family-author Negative
2. + broad anatomy Negative
3. + count/extra-limb Negative only when relevant

Measure separately:
- target retention
- unrelated anatomy error rate
- image usability

A Negative that improves general anatomy but destroys the Special is not a net success.

## 7. Count as a separate generation burden

Exact count is hard because the model must bind:
- number of actors
- number of implements
- number of body sites
- simultaneous relations.

A `multiple/triple` target should be scored with a count predicate. Do not accept a visually dense scene as count success.

When exact count is intrinsic:
- `WRONG_COUNT` is a direct semantic failure;
- extra objects/tentacles/limbs are not harmless decoration;
- a unary tagger cannot certify the count relation.

## 8. Self-action and unusual ownership

Self-directed rare concepts add ownership difficulty: the acting body part/object must belong to the same actor as the target site.

This can fail as:
- an implied second actor
- disconnected body part
- wrong ownership
- generic pose replacing self-action.

Evaluation must include `OWNERSHIP_OK` in addition to target presence.

## 9. Urethral/body-site micro-targets

Very small body-site targets create an observability problem independent of model semantics.

Potential false outcomes:
- target may exist but be below resolvable pixel scale;
- tight crop may improve observability while changing pose/composition;
- Hires/inpaint may create the final small feature after base generation.

Therefore:
- visibility/framing is a deliberate experimental variable;
- base and post-Hires/inpaint evidence remain separate;
- absence at low pixel coverage should route to `VISIBILITY_UNCLEAR` before model-ignorance claims.

## 10. Inflation / bulge / body-shape transformation

These concepts can be produced at several semantic strengths:
- broad body-size change
- localized bulge
- internal-pressure-like visual cue
- unrelated weight/body-shape change.

Risk:
A model or LoRA may satisfy a broad silhouette cue while missing the causal/localized concept.

Score:
- target location
- shape distribution
- whether unrelated body proportions changed
- collateral style/context.

Practical LoRA reports that attempt to isolate hyper/body-size concepts show that adapter training can unintentionally alter global body proportions. Treat this as LoRA collateral, not target proof.

## 11. Rare LoRA evidence

Rare/extreme LoRAs provide two useful kinds of information:

### Positive hypothesis value
They reveal likely visual constituents/supports and prove that an adapter can learn a concept.

### Confound value
They can import:
- body-shape priors
- camera priors
- background/context
- style
- anatomy distortions
- favorite counts/poses.

Therefore a dedicated LoRA is a **separate capability lane**, not evidence that its trigger/support applies to the base model.

Use same-seed comparisons:
- base checkpoint, no LoRA
- LoRA loaded, no trigger if informative
- LoRA + trigger
- varied weight if needed.

## 12. Model-family notes

### WAI Illustrious v17
The author warns against oversized quality/aesthetic and Negative stacks, while Hires can repair limbs. Both are especially relevant to rare anatomy-changing concepts.

Hard rule:
- retain pre-Hires image;
- use minimal official baseline first;
- test anatomy Negative separately.

### NoobAI XL 1.1 EPS
Full Danbooru/e621 coverage supports broad adult/nonhuman vocabulary exposure, but low current post_count or Semantic labels still cannot certify exact learned tokens.

The e621 component may help some nonhuman/anatomy concepts relative to pure-Danbooru assumptions, but no exact per-tag exposure table is available -> `HOLD`.

### Anima
Strong semantic language encoding makes short factual decomposition an interesting candidate for rare relations/states, but model priors can still overpower unusual combinations.

Keep:
- tag-only
- concise hybrid
as separate conditions; do not assume prose always improves rare concepts.

## 13. Evaluator routing

Suggested capability classes:

- `DIRECT_COMMON`
  - common unary concept and evaluator vocabulary covered
- `DIRECT_RARE`
  - exact target exists but rarity/calibration uncertain
- `ALIAS_TRIGGER_TEST`
  - canonical/search identity known, generation trigger equivalence unproven
- `SEMANTIC_DECOMPOSE`
  - Semantic/search concept represented as measurable predicates
- `RELATION_REVIEW`
  - body-site/ownership relation not safely automated
- `COUNT_REVIEW`
  - exact simultaneous count needed
- `ANATOMY_NEGATIVE_AB`
  - unusual anatomy under possible Negative collision
- `LORA_ASSISTED_ONLY`
  - robust result only recovered with adapter
- `POSTPROCESS_RESCUE`
  - robust result requires inpaint/Hires repair
- `HUMAN_ONLY`
  - evaluator vocabulary/semantics insufficient.

No global confidence threshold across these classes.

## 14. WD EVA02 rare-tail warning

WD EVA02 v3 filtered tags with fewer than 600 images. The project has many hard-target rows near/below this range and 336 Semantic-layer entries without a direct canonical post_count.

Consequences:
- missing target output can be structural vocabulary absence;
- low confidence can mean undercoverage, not generation failure;
- exact 600 boundary also makes “just above 600” very different from “well-covered” only in vocabulary inclusion, not guaranteed quality.

Use Kagami/CL Tagger breadth comparisons after dictionary freeze, but breadth itself is not semantic ground truth.

## 15. Minimum-sufficient support for rare targets

Start with a protected semantic nucleus.

Then test only supports tied to a failure hypothesis:
- missing visual constituent -> one meaning support
- wrong geometry -> one geometry support
- hidden target -> one visibility support
- ownership confusion -> one resource/binding support
- target too rare -> one broad/frequent constituent A/B

Stop when all relevant roles have been tested without repeatable benefit. Do not turn rarity into unlimited Prompt growth.

## 16. Evidence threshold

For rare concepts:
- E0 one-seed success = proof of possibility only
- E1 multiple predetermined seeds = repeatability direction
- E2 paired comparison = evidence for support/Negative/trigger difference
- E3 multiple representative rare concepts/families = candidate reusable rule.

A single spectacular LoRA/example image is never E3 evidence.

## 17. Priority hard cases for eventual controlled tests

1. direct common vs direct rare within same semantic family
2. rare canonical vs Alias/alternate trigger
3. Semantic decomposition vs raw phrase
4. unusual anatomy with/without broad Negative
5. exact count 1 -> 2 -> 3
6. rare target alone vs + one frequent constituent
7. base vs LoRA-assisted
8. base vs postprocess rescue
9. prompt-only vs regional/pose assistance where relation geometry is the blocker.

## 18. HOLD backlog

- exact rare-tag exposure for WAI v17 / NoobAI 1.1 / Anima
- exact frequency threshold where broad support becomes worthwhile
- anatomy-negative effect magnitude by family
- exact count ceiling by concept/model
- micro-body-site observability resolution threshold
- LoRA weight/context leakage rules that generalize
- automated relation/count/anatomy evaluator suitable for hard rare targets.

## Sources

- Rare concept generation / SeedSelect: https://arxiv.org/abs/2304.14530
- Rare-to-Frequent: https://arxiv.org/abs/2410.22376
- 2026 rare-concept common-knowledge bias: https://arxiv.org/abs/2607.14765
- ConceptMix: https://arxiv.org/abs/2408.14339
- Negative prompt mechanism: https://arxiv.org/abs/2406.02965
- WD EVA02 v3: https://huggingface.co/SmilingWolf/wd-eva02-large-tagger-v3
- Kagami-24k: https://huggingface.co/Redstonexs/kagami-24k
- CL Tagger v2: https://huggingface.co/cella110n/cl_tagger_v2
- Project dictionary: `04_性行為・性的刺激.txt`, `05_挿入・性具・機械.txt`, `06_拘束・BDSM・支配.txt`, `08_異形・触手・非人間.txt`.
