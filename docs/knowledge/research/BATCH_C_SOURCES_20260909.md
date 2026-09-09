# Batch C Source Registry — Evidence Reliability / Evaluator Boundaries — 2026-09-09

Owner: Issue #44 `[KNOWLEDGE][ONGOING] Persistent generation knowledge corpus for dictionary audit and Stage10`

Research target:
- predetermined paired-seed evidence;
- absolute reliability vs pairwise improvement;
- small-sample paired binary inference;
- human pairwise judgement with ties/uncertainty;
- tagger vocabulary/calibration/OOD limits;
- capability-routed evaluator evidence;
- local personal success/failure history without semantic-authority contamination;
- assisted-control evidence identity.

---

## Statistical / paired-comparison evidence

### C01 — McNemar test, NIST

- URL: https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/mcnemar.htm
- Class: `FACT_STATISTICAL`
- Scope:
  - paired binary outcomes;
  - tests whether discordant pair probabilities differ.
- Key use:
  - A/B generated from the same predetermined seed naturally forms a paired observation when the outcome is binary (`target succeeds/fails`);
  - only discordant pairs (`A fail/B pass`, `A pass/B fail`) identify directional difference;
  - both-pass/both-fail pairs still matter for absolute reliability but not McNemar direction.
- Small-sample note:
  - NIST documents an exact/binomial small-sample treatment.

### C02 — statsmodels exact McNemar

- URL: https://www.statsmodels.org/dev/generated/statsmodels.stats.contingency_tables.mcnemar.html
- Class: `FACT_STATISTICAL`
- Key use:
  - exact mode uses the binomial distribution;
  - appropriate conceptual reference for small paired binary A/B tables.

### C03 — SciPy exact binomial test / confidence intervals

- URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html
- Class: `FACT_STATISTICAL`
- Key use:
  - exact binomial test for a proportion;
  - exact/Wilson confidence intervals available for observed success proportions.
- Product implication:
  - report uncertainty on absolute success rates rather than only raw `7/8`-style counts.

### C04 — Kagami-24k paired bootstrap design

- Model card: https://huggingface.co/Redstonexs/kagami-24k
- Class: `FACT_EXACT_EVALUATOR`
- Key use:
  - compares models on identical held-out images;
  - paired bootstrap over images, so each system sees the same data and per-image difficulty is paired;
  - predeclared release criterion uses confidence intervals on metric differences;
  - explicitly acknowledges a comparison where an interval touches zero rather than claiming a decisive win.
- Product implication:
  - pair on the same seeds/cases and keep uncertainty visible;
  - do not treat every point-estimate advantage as established.

---

## T2I benchmark sampling evidence

### C05 — GenEval

- Paper: https://arxiv.org/abs/2310.11513
- Code: https://github.com/djghosh13/geneval
- Class: `FACT_GENERAL_EVALUATION`
- Key use:
  - object-focused evaluation separates concept categories such as count, color, position and attribute binding;
  - benchmark uses multiple images per prompt (four in its standard generation procedure).
- Product implication:
  - one image is insufficient for benchmark-level reliability;
  - different semantic questions should not be collapsed into one score.
- Do not infer:
  - four is the universal DanbooruTagTool seed count.

### C06 — T2I-CompBench

- Code: https://github.com/Karine-Huang/T2I-CompBench
- Class: `FACT_GENERAL_EVALUATION`
- Key use:
  - standard evaluation generates ten images per prompt;
  - separates color, shape, texture, spatial, non-spatial and complex composition metrics;
  - uses fixed seeds across methods for comparable evaluation.
- Product implication:
  - multiple samples and semantic-category-specific scoring are normal in serious compositional evaluation.
- Do not infer:
  - ten images are required for every Stage10 experiment.

---

## Human pairwise preference / tie evidence

### C07 — Pick-a-Pic

- Paper: https://proceedings.nips.cc/paper_files/paper/2023/file/73aacd8b3b05b4b503d58310b523553c-Paper-Conference.pdf
- Project overview: https://stability.ai/research/pick-a-pic
- Class: `FACT_GENERAL_HUMAN_EVAL`
- Key use:
  - each comparison contains a prompt, two images, and a preference label **or tie**;
  - authors piloted multiple interfaces and report two images with ties as the best option among tested interfaces for engagement and inter-rater agreement.
- Product implication:
  - do not force A/B binary judgement when no meaningful preference exists;
  - `TIE` is legitimate evidence, not reviewer failure.

### C08 — HPS v2 / HPD v2

- Repo: https://github.com/tgxs002/HPSv2
- Class: `FACT_GENERAL_HUMAN_EVAL`
- Key use:
  - ~798k human preference choices;
  - pairwise comparison is a standard human-preference representation for T2I.
- Product implication:
  - pairwise judging is appropriate for A/B support experiments, but a generic preference score is not the same as Special semantic correctness.

### C09 — ImageReward

- Paper: https://arxiv.org/abs/2304.05977
- Repo: https://github.com/zai-org/ImageReward
- Class: `FACT_GENERAL_HUMAN_EVAL`
- Key use:
  - reward model trained from expert comparisons;
  - demonstrates that learned preference metrics are useful but are trained toward broad human preference, not project-specific rare Special truth.
- Product implication:
  - aesthetic/preference rewards may be auxiliary, not semantic ground truth for rare/relational targets.

### C10 — Human anatomy T2I annotation study

- URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC11663238/
- Class: `FACT_GENERAL_HUMAN_EVAL`
- Key use:
  - reports non-perfect inter-rater agreement and variation in annotator styles across anatomy/error categories.
- Product implication:
  - human judgement itself carries uncertainty; `UNCLEAR` and rule-based disagreement review are necessary for anatomy/complex relation cases.

---

## Tagger/evaluator exact evidence

### C11 — WD EVA02-Large Tagger v3

- Official model: https://huggingface.co/SmilingWolf/wd-eva02-large-tagger-v3
- Class: `FACT_EXACT_EVALUATOR`
- Exact facts used:
  - ratings, characters, general tags;
  - training/validation derived from Danbooru up to last image ID 7,220,105;
  - tags with fewer than **600 images were filtered out**;
  - reported P=R threshold 0.5296 / F1 0.4772;
  - v3 tags updated through 2024-02-28.
- Product implication:
  - rare Special absence from WD vocabulary is structural, not image failure;
  - global WD confidence cannot be semantic ground truth for rare/composite/relational Specials.

### C12 — Kagami-24k

- Model: https://huggingface.co/Redstonexs/kagami-24k
- Class: `FACT_EXACT_EVALUATOR`
- Exact facts used:
  - EVA02-L Danbooru tagger;
  - 24,000 general tags;
  - Apache-2.0;
  - evaluated on 11,639 posts newer than all compared training cutoffs;
  - common-intersection benchmark reports higher macro-AP/fine AP than WD EVA02 and substantially wider vocabulary coverage;
  - paired-bootstrap intervals are reported;
  - model card explicitly warns that large vocabulary does not mean the rare tail is equally well validated.
- Product implication:
  - useful wide-vocabulary evaluator candidate;
  - vocabulary presence and ranking performance do not establish relation/composite truth.

### C13 — CL Tagger v2

- Model: https://huggingface.co/cella110n/cl_tagger_v2
- License: https://huggingface.co/cella110n/cl_tagger_v2/blob/main/LICENSE.md
- Class: `FACT_EXACT_EVALUATOR`
- Current exact facts:
  - stable v2.00 released 2026-06-14; provisional v2_01a 2026-06-18;
  - fixed 384px SigLIP2 SO400M encoder;
  - v2.00 vocabulary 106,536; provisional v2_01a 108,036;
  - tag-wise calibration and thresholds are included;
  - model card recommends 0.55 when using a single practical threshold and notes F1-optimal per-tag thresholds tend to over-tag;
  - `model_ood_ref.npz` contains OOD reference statistics;
  - gated access and custom model license apply.
- Product implication:
  - per-tag calibration/OOD information is valuable for conservative routing;
  - a one-size threshold is explicitly not the only supported usage;
  - evaluator output still includes false positives/negatives and ambiguous General/Meta limitations; it is not semantic truth.
- Reproducibility choice:
  - prefer stable v2.00 for fixed comparisons unless a provisional version is deliberately pinned and accepted.

---

## Evidence discipline derived from these sources

1. **Pair the same seed/case across A/B.** Independent A and B seed pools waste the strongest experimental control available.
2. **Report both relative and absolute outcomes.** McNemar/sign-style direction can ignore concordant pairs, but both-fail seeds are critical product failures.
3. **Predetermine seeds.** Searching for a seed that demonstrates the desired effect invalidates a reliability claim.
4. **Do not copy benchmark sample counts mechanically.** GenEval/CompBench demonstrate multi-sample necessity, not a universal count.
5. **Allow `TIE` and `UNCLEAR`.** Forcing a binary judgement creates false evidence.
6. **Human preference is not semantic correctness.** Preference/reward models are auxiliary signals only for this product's niche semantic goal.
7. **Evaluator capability must be checked before score interpretation.** Vocabulary, semantic class, calibration and OOD are part of evaluator identity.
8. **A global confidence threshold is not justified across evaluator/model/semantic classes.** CL Tagger itself exposes per-tag metrics/calibration; WD has a structurally filtered vocabulary; relation/composite semantics exceed unary classifier assumptions.
9. **Exact statistical significance is not practical sufficiency.** A tiny but statistically consistent change can still be irrelevant to user iteration reduction; effect/collateral utility must be reported.
10. **Local personal history must stay empirical.** Repeated user-local outcomes may influence local ranking under matching model/context, but must never rewrite canonical semantic truth.
