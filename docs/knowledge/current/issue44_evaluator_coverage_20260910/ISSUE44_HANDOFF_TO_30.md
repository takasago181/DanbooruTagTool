# Issue #44 — Special 2,788 evaluator coverage handoff to #30

Date: 2026-09-10
Branch: `knowledge/generation-corpus`
Scope: desk/vocabulary coverage + structural relation-risk routing only. No image generation or Stage10 A/B was run.

## 1. What was classified

All 2,788 finalized Special Core Dictionary entries were classified against the available evaluator vocabulary state.

Machine-readable table:

- `docs/knowledge/current/issue44_evaluator_coverage_20260910/special2788_evaluator_coverage.csv`

Representative calibration cases:

- `docs/knowledge/current/issue44_evaluator_coverage_20260910/representative_calibration_cases.csv`

Raw aggregate summary:

- `docs/knowledge/current/issue44_evaluator_coverage_20260910/summary.json`

The table contains Special ID, canonical, WD14 class, Kagami class, CL class, usable vocabulary observations, relation requirement/reasons, human-review requirement, and provisional final recommendation.

## 2. Evaluator vocabulary coverage

### WD14 / wd-eva02-large-tagger-v3

Pinned vocabulary revision: `b25b82a03f7282e41aa2f257a52c7583b710bd1c`.

- DIRECT: 1,484 / 2,788 = **53.23%**
- DIRECT + current reviewed alias/approx layer: 1,484 / 2,788 = **53.23%**
- COMPONENT_ONLY: 450 additional entries
- DIRECT/ALIAS/COMPONENT observable predicate range: 1,934 / 2,788 = **69.37%**

### Kagami-24k

Resolved model revision: `1a1e36f52d0fa202a26cf8f4169f42ef92b9367d`.

- DIRECT: 1,785 / 2,788 = **64.02%**
- DIRECT + current reviewed alias/approx layer: 1,785 / 2,788 = **64.02%**
- COMPONENT_ONLY: 353 additional entries
- DIRECT/ALIAS/COMPONENT observable predicate range: 2,138 / 2,788 = **76.69%**

### CL Tagger v2 stable/fixed release

Target is stable/fixed `v2_00`.

Exact vocabulary coverage is **not measured in this checkpoint**. The official model vocabulary is gated and the workflow did not have an authorized `HF_TOKEN`; the request returned HTTP 401. Every CL cell is therefore `UNVERIFIED_GATED`, not a negative coverage result.

Do not report CL coverage as 0%. This is an access/provenance blocker, not evidence that CL cannot observe those Specials.

Once an authorized token accepted for the official gated repository is available, rerun the same analyzer. It will populate the CL column and recompute the true three-evaluator union without changing production data.

## 3. Combined confirmed coverage

Because CL stable v2.00 is gated, the currently confirmed combined range is a **WD14 + Kagami lower bound**, not the final three-evaluator figure.

- direct union: 1,800 / 2,788 = **64.56%**
- direct + current reviewed alias/approx union: 1,800 / 2,788 = **64.56%**
- including component predicates: 2,137 / 2,788 = **76.65%**

The final 3-evaluator combined percentage is pending CL v2.00 vocabulary authorization.

## 4. Alias / approximate interpretation

The current machine run found no *additional* reviewed alias/approx matches beyond direct canonical matches in the currently consumed semantic bridge fields.

This means **0 additional alias uplift was proven by the current reviewed mapping**. It does not mean the project has no linguistic aliases, and it must not be interpreted as permission to invent equivalences. A future alias uplift must come from an explicit reviewed mapping with provenance.

## 5. Structural relation risk and provisional routing

The desk pass does not equate tag presence with image correctness. Production Generation Profile fields and conservative lexical/family signals were used to identify relation/binding-sensitive cases.

Detected relation/binding review requirement:

- 1,397 / 2,788 = **50.11%**

Provisional routing over the currently verified evaluator state:

- `AUTO_CANDIDATE`: 618 / 2,788 = **22.17%**
- `REVIEW_REQUIRED`: 1,497 / 2,788 = **53.69%**
- `BLOCKED`: 673 / 2,788 = **24.14%**

`AUTO_CANDIDATE` is not automatic-evaluation approval. It means only that a verified evaluator has a direct/alias vocabulary observation and the desk pass did not identify a structural relation/binding requirement. These entries still require real-image calibration before Stage10 can auto-score them.

`REVIEW_REQUIRED` includes cases where taggers can see useful labels/components but cannot safely prove the full Special, especially subject/object binding, body-site ownership, spatial assignment, quantity, multiple actors, insertion/contact/restraint topology, or compound retention.

`BLOCKED` means the currently verified evaluators do not expose a useful enough observation, or a relation-sensitive Special lacks useful observable predicates. CL authorization can move some vocabulary-blocked cases, but relation-sensitive cases must not automatically become AUTO merely because CL has a matching label.

## 6. Main failure categories for automation

1. **Subject/object binding** — detecting two unary labels does not establish who acts on whom.
2. **Body-part ownership/site binding** — detecting a body part and an action does not establish the required attachment or target site.
3. **Multi-person assignment** — actor count and role allocation can be lost even when all components are tagged.
4. **Exact quantity** — `double`, two-/three-way structures, and repeated actions need count-sensitive calibration.
5. **Spatial/directional topology** — front/back, under/over, source/destination and around/through/in relationships are not guaranteed by unary tags.
6. **Insertion/contact/restraint topology** — presence of involved objects/body parts is weaker than proof of the requested relation.
7. **Compound Specials** — a model may output only a subset of the requested conjunction.
8. **Rare-tail vocabulary and calibration** — vocabulary presence alone is not evidence of reliable precision/recall for rare concepts.
9. **Alias/equivalence risk** — evaluator spellings/near-synonyms are observation aids, not Danbooru semantic authority.
10. **Evaluator/model/version drift** — coverage and thresholds must remain pinned to exact evaluator releases.

## 7. Representative real-image calibration set

The selected file intentionally includes both likely successes and likely failures. Current strata include:

- simple/unary candidates: `anus`, `spread anus`, `anus peek`
- rare/no-vocabulary: `bare anus`, `exposed genitals`, `genital closeup`
- relation: `armpit sex`, `buttjob`, `cloth glansjob`
- component-only: `cuddling handjob`, `footjob under table`, `footjob with boots`
- body-part relation: `anal fingering`, `anal object insertion`, `double anal`
- actor/subject-object: `cooperative footjob`, `cooperative handjob`, `crotch rub`
- spatial/multi-person assignment: `mutual masturbation`, `cooperative fellatio`, `oral sandwich`
- count/multiple: `double footjob`, `double handjob`, `two-footed footjob`
- compound: `hug and suck`, `stand and carry`, `cock and ball torture`
- outcome controls include one additional AUTO, REVIEW and BLOCKED example.

No alias-dependent calibration example was fabricated because this run did not prove an additional reviewed alias mapping. Add such a stratum only after a reviewed alias/approx correspondence is available.

For #30, the first calibration wave should deliberately mix the above strata rather than start with only obvious unary successes.

## 8. Provisional Stage10 boundary

### May enter real-image automatic-calibration candidate pool

Only `AUTO_CANDIDATE`, and even then not yet as production automatic scoring. #30 must establish per-evaluator/per-class threshold behavior and false-positive/false-negative behavior on generated images first.

### Must return to human A/B by default

- any `REVIEW_REQUIRED`
- any subject/object, actor assignment, body-site ownership, spatial relation, count, multi-person, insertion/contact/restraint topology or compound-retention requirement
- any contradiction between evaluators
- any rare or weakly calibrated tag where confidence behavior is unstable
- any case where only component predicates fire but the Special relation itself is unproven

### Do not auto-score with current evidence

- `BLOCKED`
- CL-only assumptions until stable `v2_00` vocabulary and image calibration are actually available
- invented aliases or semantic substitutions

## 9. Remaining blocker before exact three-evaluator closure

The only evaluator-coverage infrastructure blocker identified in this checkpoint is authorized access to the official gated CL Tagger v2 stable/fixed (`v2_00`) vocabulary. The analyzer is already prepared to consume it through `HF_TOKEN` and recompute all 2,788 rows.

This should be resolved before #30 treats the coverage matrix as a final three-evaluator matrix. #30 can still use the current WD14+Kagami result as a conservative lower-bound input and begin designing the calibration protocol, but should not claim exact three-evaluator coverage yet.

## 10. Guardrails confirmed

- no production `data/**` modified
- no #32 classifications modified
- no Special canonical modified
- evaluator output not used as Danbooru semantic authority
- no 2,788-image generation sweep started
- no Stage10 production A/B started
- no unsolicited cross-team production change requested
