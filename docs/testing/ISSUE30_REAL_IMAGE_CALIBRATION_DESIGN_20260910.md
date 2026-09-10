# Issue #30 — Real-image evaluator calibration design

Date: 2026-09-10
Status: **DESIGN COMPLETE / IMAGE GENERATION NOT STARTED**

## 1. Purpose and boundary

This document defines a reproducible calibration pass for WD14, Kagami-24k and
CL Tagger v2.00 against human image-level reference judgments. It is a
pre-Stage10 capability test, not approval of `AUTO_CANDIDATE` as production
automatic scoring.

This pass deliberately does **not**:

- generate a 2,788-image sweep;
- start Stage10 production A/B;
- change `data/**`, #32 verdicts, canonical values, or evaluator vocabularies;
- treat a Tagger label as Danbooru semantic or relation ground truth;
- promote relation/binding cases merely because a component tag is detected.

The committed machine-readable per-image contract is
`ISSUE30_REAL_IMAGE_CALIBRATION_RESULT_SCHEMA_20260910.json`. The case manifest
is `ISSUE30_REAL_IMAGE_CALIBRATION_CASES_20260910.csv`.

## 2. Source and provenance

The case manifest starts with all 30 rows from:

`docs/knowledge/current/issue44_evaluator_coverage_20260910/representative_calibration_cases.csv`

read from `knowledge/generation-corpus` at the corrected handoff lineage
(`557aa4c`, synchronized by `dba23df`). The exact desk classifications and
coverage values remain those of the Issue #44 correction checkpoint
`5614819866`.

For reproducibility, the source blobs used for the 30-row seed and its desk
matrix are:

- representative cases CSV: `89fa920c2ab517ad0b62af0e953c995ed7bc8a4b`;
- evaluator coverage CSV: `389f7c6ea4d9eaaa38ddb92876dab3d048caa8bf`;
- summary JSON: `3538b68b449843dfd426aea202806882159787f3`.

| item | value |
|---|---:|
| Special Core entries | 2,788 / 2,788 |
| WD14 direct | 658 (23.60%) |
| Kagami direct | 1,412 (50.65%) |
| CL Tagger v2.00 direct | 1,704 (61.12%) |
| three-evaluator direct union | 1,725 (61.87%) |
| observable including components | 1,957 (70.19%) |
| relation/binding structural risk | 918 (32.93%) |
| `AUTO_CANDIDATE` | 939 |
| `REVIEW_REQUIRED` | 1,018 |
| `BLOCKED` | 831 |

The two supplemental rows are not invented aliases or new canonical data:

- `bound penis` (Special ID 632) supplies an explicit restraint/body-part
  binding example absent from the 30-row handoff table.
- `anus + after footjob` is a controlled multi-Special retention question using
  existing IDs 1 and 8; it is a test combination, not a new Special entry.

## 3. Calibration unit and planned size

The unit of analysis is one generated image and one immutable result record.
The initial wave contains **32 cases × 4 images = 128 planned images** on one
pinned baseline profile. Four images per case are:

1. `target_present_seed_a`: target Prompt, seed A;
2. `target_present_seed_b`: same target Prompt, seed B;
3. `contrast_seed_a`: target absent or the relevant relation removed, seed A;
4. `contrast_seed_b`: same contrast Prompt, seed B.

The contrast must preserve unrelated components where possible. Examples:

- relation case: retain actor/object components but remove or invert the
  requested relation;
- component-only case: retain component tags without claiming the compound
  relation;
- quantity case: change double to single, or vice versa, while holding the
  action fixed;
- compound case: retain one element and remove the other;
- multi-Special case: remove one Special while retaining the other.

If a contrast cannot be made without changing multiple questions, the cell is
marked `UNSUITABLE_CONTRAST` and is not used for threshold fitting. It remains
useful as a human-review example.

The initial profile is the already demonstrated infrastructure baseline:

- Forge Neo API `neo-2.29`;
- `waiIllustriousSDXL_v170`, checkpoint hash `f116b0c78f`;
- 1024×1024, batch 1, Euler a / Automatic;
- Steps 24, CFG 4.5, LoRA absent;
- fixed seed values recorded per image.

The schema permits other model families, checkpoints and LoRA profiles, but
results must not be pooled across model family, checkpoint, LoRA state or
Prompt grammar. A later model-family replication is a separate calibration
stratum, not a silent extension of this baseline result.

For a multi-Special row, `special_id` is the primary ID and `special_ids`
contains the complete set. For a single-Special row they contain the same one
ID.

## 4. One experiment = one question

Each case has a single calibration question in the case manifest. Prompt and
Negative Prompt text is resolved at execution time from the approved Prompt
input contract and stored verbatim in every image record. The manifest stores
the contrast recipe, not a guessed Prompt.

The 32 cases cover these strata:

- simple unary: `anus`, `spread anus`, `anus peek`;
- rare/tail or no verified vocabulary: `bare anus`, `exposed genitals`,
  `genital closeup`, `visible genitals`;
- relation: `armpit sex`, `buttjob`, `cloth glansjob`;
- component-only: `cuddling handjob`, `footjob under table`, `footjob with
  boots`;
- body-part/site binding: `anal fingering`, `anal object insertion`,
  `double anal`;
- actor/subject/object: `cooperative footjob`, `cooperative handjob`,
  `grabbing another's ass`;
- spatial/multi-person assignment: `mutual masturbation`, `cooperative
  fellatio`, `oral sandwich`;
- quantity/multiple: `double footjob`, `double handjob`, `teamwork (sexual)`;
- compound retention: `hug and suck`, `stand and carry`, `cock and ball
  torture`;
- insertion/contact/restraint topology: `anal object insertion`, `cloth
  glansjob`, `cock and ball torture`, supplemental `bound penis`;
- multi-Special retention: supplemental `anus + after footjob`;
- evaluator disagreement: the 12 handoff rows whose WD14/Kagami/CL desk
  classes differ, including `cloth glansjob`, `cuddling handjob`, `double
  anal`, `cooperative footjob`, `oral sandwich`, `hug and suck` and
  `after footjob`;
- outcome controls: at least one `AUTO_CANDIDATE`, one `REVIEW_REQUIRED` and
  one `BLOCKED` row.

The source 30 are intentionally retained even where several cases are hard or
similar. Removing them would bias the calibration toward easy unary tags.

## 5. Human reference protocol

Human judgment is the image-level reference. It is a reference label, not a
claim that a Tagger or a single reviewer defines Danbooru semantics.

For every image:

1. render the image and show the case question, but hide Tagger scores/tags,
   desk recommendation and proposed routing;
2. obtain two independent blinded labels;
3. use the tri-state values `true`, `false`, `unclear`, or `not_applicable` for
   each applicable dimension;
4. preserve both raw rater records;
5. adjudicate disagreements with a third reviewer or documented adjudication;
6. set `reference_state=UNRESOLVED` when the disagreement cannot be resolved.

An `UNRESOLVED` reference is excluded from promotion/threshold fitting and is
sent to human review. It is not silently converted to a negative label.

The required dimensions are:

- target concept present;
- actor/subject correct;
- target/object correct;
- body-part ownership/site correct;
- count correct;
- spatial relation correct;
- all compound elements retained;
- unwanted extra interpretation present;
- usable for Stage10 preference judgment.

`overall_reference_verdict` is derived only after the dimensions are recorded:
`PASS` requires all applicable required dimensions to be true and no unwanted
extra interpretation; `FAIL` requires a required dimension to be false or an
unwanted extra interpretation; otherwise it is `UNCLEAR`.

## 6. Evaluator capture and normalization

For each evaluator, store the untouched raw response as an external artifact
with a hash, plus normalized `raw_score` and `detected_tags` in the image
record. A normalized observation is one of:

- `DIRECT`: evaluator exposes the target vocabulary;
- `COMPONENT_PROXY`: only component tags are observed;
- `NONE`: no useful target/component observation;
- `UNVERIFIED`: evaluator execution or version could not be verified.

Normalization never rewrites the Prompt, invents aliases, or turns a component
into proof of a relation. Raw scores remain comparable only within the same
evaluator version and output format.

The correctness label for an evaluator is computed against the adjudicated
human reference for the relevant dimension, not against the evaluator's own
tag. For a relation/binding case, a direct relation tag can still be `FP` if
the image shows the wrong actor, site, direction, count or topology.

## 7. Comparison matrix

Run every strategy over the same image records and preserve the threshold grid
and routing decision in the result artifact:

1. evaluator alone: WD14, Kagami, CL v2.00 separately;
2. `OR`: any eligible evaluator positive;
3. `AND`: all required evaluators positive;
4. majority vote: at least two of three positive;
5. CL-primary + WD/Kagami support: CL must meet its threshold; support may
   raise confidence but cannot override a relation/binding human-review rule;
6. disagreement→human: any non-unanimous evaluator state abstains to review;
7. limited component proxy: permitted only for explicitly unary visual target
   dimensions after calibration; never sufficient for actor/object, ownership,
   count, spatial, insertion/contact/restraint or compound retention.

Thresholds are explored per evaluator × capability class × model profile.
Initial pooled classes are `DIRECT_UNARY`, `RARE_TAIL`, `RELATION_BINDING`,
`COMPONENT_PROXY`, `COMPOUND`, `QUANTITY_SPATIAL` and `BLOCKED`. A tag-specific
threshold is only considered when a later dataset has at least 20 resolved
positive and 20 resolved negative images for that tag, with an independent
holdout. The 32-case wave is not large enough to freeze tag-specific or
production thresholds.

Use case-level leave-one-case-out evaluation while exploring thresholds, so
images from one case cannot teach and test the same case. Report both the
development decision and the held-out result.

## 8. Metrics

For every evaluator and combination strategy, report:

- precision, recall, false-positive rate and false-negative rate;
- balanced accuracy;
- resolved-image count and abstention count;
- pairwise evaluator agreement and three-way agreement;
- relation-sensitive failure rate: automatic-positive images where any
  applicable actor/object, ownership/site, count, spatial or topology
  dimension is false/unclear;
- `AUTO_CANDIDATE` precision;
- fraction sent to human review;
- BLOCKED rate and infrastructure-blocked rate separately.

For small strata, include Wilson confidence intervals and raw confusion counts;
do not rank strategies by a rounded percentage alone. A strategy that has
higher automation but a worse false-positive bound is rejected.

## 9. Provisional routing rules

These rules are calibration hypotheses, not frozen production truth.

### BLOCKED

Route to `BLOCKED` when required Prompt/image path/hash/PNG metadata/evaluator
version is missing, the evaluator did not execute, or the case has no useful
verified target/component observation. A blocked evaluator result is not an
image-level FAIL.

### HUMAN_REVIEW_REQUIRED

Default to human review for:

- relation/binding, actor assignment, body-site ownership, quantity, spatial
  direction, insertion/contact/restraint and compound retention;
- component-only proxy observations;
- evaluator disagreement, weak rare-tail behavior or unclear human labels;
- any direct evaluator result contradicted by a required human dimension;
- any model/checkpoint/LoRA profile without its own calibration evidence.

### AUTO_CANDIDATE

`AUTO_CANDIDATE` is allowed only as a candidate input to calibration when the
desk row is direct, the human reference is resolved, the case is not
relation-sensitive, and required provenance is complete. It becomes a
`CALIBRATED_AUTO_CANDIDATE` only if its class-specific strategy passes the
holdout gate below. It must return to human review on disagreement, abstention,
or any unsupported dimension.

No class is promoted from the 32-case pilot directly to Stage10 production
automatic scoring solely because it has zero observed false positives in this
small sample.

## 10. Stage10 production-start Gate

Stage10 production A/B remains prohibited until all of the following are true:

1. the exact model/checkpoint/Prompt/Negative/metadata path is frozen for the
   tested profile and independently reproducible;
2. every proposed automatic capability class has at least 30 resolved positive
   and 30 resolved negative holdout images from multiple cases (or a larger
   sample justified by the class risk);
3. its precision point estimate is at least 0.98, its false-positive rate is at
   most 0.02, and the one-sided 95% confidence bounds do not contradict those
   limits;
4. no relation-sensitive class is auto-routed without class-specific evidence
   for actor/object, ownership/site, count, spatial and topology dimensions;
5. evaluator disagreement and component-only cases have an explicit human
   fallback with an acceptable measured review fraction;
6. BLOCKED is lossless and traceable, with zero missing-required-metadata cases
   silently scored as FAIL or AUTO;
7. an independent reviewer accepts the confusion matrices, raw artifacts,
   human-label protocol and failure analysis;
8. #42, #5 and the remaining `STAGE_10_PREP.md` gates are satisfied or
   explicitly separated by management.

If any condition is unmet, the result is `HOLD_PRE_STAGE10`, not a partial
production authorization.

## 11. Expected failure modes

The run must explicitly look for:

- subject/object reversal while both unary concepts are detected;
- body-part ownership or site mismatch;
- multiple people with roles assigned to the wrong person;
- one action detected where a double/triple quantity is required;
- front/back, left/right, above/below or source/destination inversion;
- insertion/contact/restraint topology reduced to separate object/body-part
  tags;
- only one element of a compound Special being retained;
- rare-tail visual false positives or unstable scores;
- apparent alias/equivalence that is not a reviewed mapping;
- version drift between evaluator vocabulary and runtime;
- prompt or negative-prompt changes that alter visibility and are mistaken for
  evaluator quality;
- metadata/hash/path loss that must be BLOCKED rather than judged visually.

## 12. Minimal execution procedure

The future execution should be:

1. verify the pinned model, Forge Neo API, evaluator versions and local
   protected-data backup; record a run manifest;
2. freeze the 32-row case manifest and assign one question per case;
3. resolve and save the exact positive/contrast Prompts and Negative Prompts;
4. generate only the 128 planned calibration images, recording seed and actual
   PNG metadata immediately;
5. hash each image and raw evaluator response before any labeling;
6. run WD14, Kagami and CL v2.00 with pinned versions;
7. conduct blinded two-rater human labeling and adjudication;
8. compute per-evaluator and combination confusion matrices with case-level
   cross-validation;
9. produce a review queue for disagreement, relation/binding, component-only,
   rare-tail and BLOCKED records;
10. write a checkpoint with metrics, limitations and the next Gate. Do not
    rewrite production routing from a single pilot result.

The only helper tooling justified at this stage is a thin validator/aggregator
that checks schema validity, required provenance, hash presence, joins raw
evaluator outputs to human labels, and emits confusion matrices. It must not
become a new GUI, queue platform or production scorer.
