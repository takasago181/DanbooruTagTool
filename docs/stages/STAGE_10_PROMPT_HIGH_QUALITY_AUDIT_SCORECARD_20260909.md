# Stage10 PROMPT high-quality hard-target audit scorecard

最終更新: 2026-09-09
Owner: PROMPT / Issue #5
Status: PROMPT-side evaluation contract candidate. No production scoring decision.

## Purpose

現在の製品目的である、

> **高品質で生成難度の高い成人向け・ニッチ・複合画像を、少ない手直しで狙い通り生成するPrompt支援**

を評価するため、Stage10で「targetが出たか」と「画像が綺麗か」を混ぜない監査scorecardを定義する。

このscorecardはproduction winner/scoringを決定しない。
Stage10の人間監査・controlled A/Bの情報を潰さず記録するためのPROMPT側候補。

---

## 1. Do not use one scalar score as the primary truth

難しい画像では以下が同時に起こり得る。

- targetは強く出たが画として壊れた
- 画は綺麗だがtarget relationが消えた
- two Specialsの片方だけ残った
- targetは成立したが別actorへbindingされた
- visibilityは改善したがcompositionが悪化した

したがってprimary recordはvectorで保持する。

### Core vectors

- `T` Target fidelity
- `B` Binding / relation correctness
- `V` Visibility / observability
- `G` Geometry / physical coherence
- `Q` Finished-image visual quality
- `C` Conflict / artifact burden
- `M` Model-family fitness / evidence status
- `U` User repair burden
- `R` Reproducibility / traceability

単一summary winnerが必要でも、上記を保存した後にのみ計算/判断する。

---

## 2. Gate checks before scoring

### GATE-0 Intent identity

Required:
- user intent preserved
- target Special specificity not silently broadened/softened
- actor/target meaning not rewritten
- adult-only target assumption preserved where applicable

Fail:
- `REJECT_INTENT_DRIFT`

### GATE-1 Traceability

Required:
- target Special ID/canonical known
- support roles known
- resolved actual Prompt available
- Negative available
- model/settings recorded

Fail:
- `BLOCKED_TRACEABILITY`

### GATE-2 Evaluation capability

If evaluator cannot represent the semantic question:
- do not emit automatic FAIL
- route `REVIEW_EVALUATOR_UNSUPPORTED`

Examples:
- relation
- ownership
- actor-target binding
- body-site binding
- multiple-Special simultaneous retention
- rare concept outside vocabulary

---

## 3. Vector definitions

Each dimension may use `0 / 1 / 2 / 3` for human audit.
The numbers are ordinal labels, not yet production weights.

### T — Target fidelity

`0` target absent / wrong concept
`1` partial or ambiguous
`2` clearly present but incomplete/weak
`3` intended target clearly realized with required specificity

For multiple Special, record each separately:
- `T_A`
- `T_B`
- `T_C` if needed

Do not average away one dropped target.

### B — Binding / relation correctness

`0` wrong actor/target/body-site/ownership
`1` ambiguous or mixed
`2` mostly correct with minor leakage
`3` clear and correct ownership/relation

If no binding/relation question exists:
- `N/A`

### V — Visibility / observability

`0` target not judgeable due crop/occlusion/frame
`1` barely judgeable
`2` adequately visible
`3` clearly visible without sacrificing composition

High V does not automatically mean high Q.

### G — Geometry / physical coherence

`0` major impossible/broken geometry
`1` substantial anatomical/pose inconsistency
`2` mostly coherent, minor issues
`3` coherent pose/geometry for the intended scene

Unusual intended anatomy must not be penalized merely for differing from ordinary anatomy. Judge unintended breakage separately from intended Special semantics.

### Q — Finished-image visual quality

Evaluate as a finished image, not tag presence.

Consider:
- anatomy/coherence excluding intentional target features
- composition balance
- subject readability
- detail consistency
- identity/style consistency
- visual cleanliness
- unwanted artifacts

`0` unusable/broken
`1` visibly weak
`2` usable/good
`3` high-quality finished result

Do not let aesthetic polish hide target failure.

### C — Conflict / artifact burden

Reverse direction: higher is worse.

`0` no meaningful added conflict
`1` minor side effect
`2` significant drift/conflict/artifact
`3` severe conflict causing failure

Record subtype:
- camera conflict
- pose conflict
- support competition
- Negative collision
- quality/style drift
- attribute leakage
- duplication/count artifact

### M — Model-family fitness / evidence status

Not numeric by default.

Values:
- `EXACT_VALIDATED`
- `FAMILY_SUPPORTED`
- `CANDIDATE_UNVALIDATED`
- `CROSS_FAMILY_BORROWED`
- `UNKNOWN`

`CROSS_FAMILY_BORROWED` cannot become production default without explicit validation.

### U — User repair burden

`0` ready-to-use; no meaningful repair
`1` one small optional choice/edit
`2` several choices or manual restructuring
`3` user must effectively rebuild/search Prompt

Lower is better.

Track:
- replacement slot count
- manual candidate selections
- tags user must search manually
- structural edits required

### R — Reproducibility / traceability

`0` cannot reproduce
`1` partial Prompt/settings only
`2` actual Prompt + major settings available
`3` source intent/template + resolved Prompt + Negative + exact model/settings + interventions traceable

---

## 4. Critical success rules

A candidate cannot be called high-quality success solely because `Q=3`.

Minimum conceptual requirements for a hard-target PASS candidate:

- `T` target(s) adequate
- `B` adequate where required
- `V` judgeable
- `G` not substantially broken
- `Q` usable/high
- `C` not severe
- `R` sufficient for interpretation

For multiple Special:
- all required `T_*` must be recorded
- one target dropping is not hidden by average score

---

## 5. Proposed PROMPT-side verdict vocabulary

### `PASS_HIGH_QUALITY_HARD_TARGET_CANDIDATE`
Target intent and finished quality both strong enough to continue validation.

### `PASS_TARGET_WEAK_QUALITY`
Target works, but finished image quality/composition needs improvement.

### `PASS_QUALITY_WEAK_TARGET`
Image is attractive/coherent, but intended Special/relation is weak or missing.
Not a product success for the stated intent.

### `REVISE_BINDING`
Concepts exist but ownership/actor-target/body-site relation is wrong/ambiguous.

### `REVISE_VISIBILITY`
Target may exist but framing/crop/occlusion prevents reliable use/judgement.

### `REVISE_GEOMETRY`
Prompt/support induces broken or conflicting physical structure.

### `REVISE_DENSITY_CONFLICT`
Over-support / competing instructions / style blocks degrade the result.

### `REVIEW_MODEL_UNKNOWN`
Likely model-family behavior issue; evidence insufficient.

### `REVIEW_EVALUATOR_UNSUPPORTED`
Automatic evaluator cannot answer the actual semantic question.

### `PROMPT_ONLY_LIMIT`
Repeated targeted Prompt support fails with the same structural class; further Prompt bloat is not justified.

### `ASSISTED_CONTROL_CANDIDATE`
May benefit from regional/pose/control intervention, to be evaluated in a separate lane.

### `REJECT_INTENT_DRIFT`
Result/Prompt only succeeds after weakening or changing the requested intent.

### `BLOCKED_TRACEABILITY`
Actual Prompt/settings/interventions are insufficiently recorded.

---

## 6. A/B comparison record

For each A/B pair record separately:

### Shared controls
- condition ID
- model/checkpoint/hash
- seed
- resolution
- sampler/scheduler
- Steps / CFG
- LoRA/control/postprocessing state

### A
- actual Positive
- actual Negative
- support blocks
- T/B/V/G/Q/C/M/U/R
- failure classes

### B
- same fields

### Difference statement
Exactly what changed between A/B.

### Human question
One sentence only.

### Result interpretation
Do not use only `A_WIN / B_WIN`.
Also preserve:
- which target dimension improved
- which quality dimension worsened
- whether the direction is seed-sensitive
- whether evaluator support exists

---

## 7. Seed sensitivity

One seed can produce misleading confidence.

For any candidate rule intended to affect production Prompt behavior:
- record result per seed
- do not average away direction reversals
- mark `SEED_SENSITIVE` if qualitative conclusion changes

Possible states:
- `CONSISTENT_DIRECTION`
- `MIXED_DIRECTION`
- `SEED_SENSITIVE`
- `INSUFFICIENT_SEEDS`

Exact production seed count is not decided here.

---

## 8. High-quality hard-image test families

Final exact cases wait for dictionary freeze / KNOWLEDGE inputs, but PROMPT evaluation should cover these classes.

1. direct rare/niche Special
2. broad vs specific retention
3. canonical vs Alias/model surface
4. multi-Special same image
5. actor-target relation
6. body-site/ownership binding
7. difficult geometry/pose
8. visibility/crop-sensitive target
9. support ON/OFF
10. under-supported vs sufficient vs over-supported
11. Negative collision-sensitive target
12. quality/aesthetic support vs target fidelity
13. family-specific tag-only vs hybrid relation support
14. Prompt-only ceiling case

Easy/common cases remain plumbing controls, not product-purpose proof.

---

## 9. Human review focus

For rare/composite/relational cases, human review should answer concrete semantic questions rather than general preference only.

Bad question:
- Which image looks better?

Better audit structure:
- Is target A present?
- Is target B present?
- Are actor/target roles correct?
- Is required region visible?
- Is geometry coherent?
- Which image has higher finished visual quality after target fidelity is considered?

This prevents an attractive but semantically wrong image from winning.

---

## 10. Automated evaluator role

Automatic taggers/classifiers may contribute evidence where vocabulary and semantics match.

They must not override:
- relation/binding human judgement
- rare vocabulary absence
- multiple-Special retention semantics
- visibility vs true absence distinction

Unsupported automated evaluation is a routing condition, not evidence of Prompt failure.

---

## 11. Current relationship to Stage9 / Stage10

Stage9 guarantees safe deterministic construction/provenance.

This scorecard adds the missing Stage10 question:

> **Did the safe Prompt actually produce the intended difficult image at high finished quality?**

No Stage9 invariant is modified by this document.

---

## Boundary

- no production scoring formula
- no global weighted sum
- no automatic winner threshold
- no Stage10 production A/B start
- no #32 verdict change
- no KNOWLEDGE #44 work takeover
- no production data/UI modification
