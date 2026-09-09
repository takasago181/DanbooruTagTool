# Stage10 PROMPT hard-target prioritized test backlog

最終更新: 2026-09-09  
Owner: PROMPT / Issue #5  
Status: PROMPT-side Stage10 planning candidate. **Not production execution authorization.**

## Purpose

`STAGE_10_PROMPT_HARD_TARGET_CATEGORY_FAMILY_FAILURE_MATRIX_20260909.md` を、Stage10で実際に検証可能な順番へ落とす。

前提:
- 一度に多変数を動かさない。
- hard-targetは「出た/出ない」だけで判定しない。
- exact Special IDs / final evaluator routingはdictionary freeze後までHOLD。
- 具体的な成人向けコアはSpecial identityまたは最小slotで管理し、ここでは露骨な完成Promptを固定しない。

---

## Tier 0 — prerequisites

- dictionary freeze / final representative Special IDs
- family/model exact versions fixed
- resolved Prompt metadata capture
- fixed seed policy
- evaluation lanes ready:
  - target
  - site
  - binding
  - object integrity
  - geometry
  - visibility
  - image quality
  - user repair cost

If any prerequisite is missing: `BLOCKED`, not FAIL.

---

## Tier 1 — family grammar calibration

### T1-1 WAI v17 — lean density
Question:
- minimum sufficient tag/support set vs overstuffed quality/negative set

A/B dimensions:
- lean quality/negative
- generic long quality/negative

Primary metrics:
- target retention
- sharpness/cleanliness
- overprompt conflict

Expected risk:
- long negative / quality overload degrades finish or target salience

### T1-2 NoobAI 1.1 — Special placement
Question:
- native caption order with Special before General vs reordered Special

Primary metrics:
- target realization
- model-trigger mismatch
- general-support interference

### T1-3 Illustrious — version-sensitive grammar
Question:
- tag-centered baseline vs exact-version targeted NL support

Must not mix:
- Onoma base version
- WAI derivative

### T1-4 Anima — hybrid relation support
Question:
- tag-only vs tags + exactly one short relation sentence

Primary metrics:
- binding
- attribute leakage
- scene-detail bleed

---

## Tier 2 — category realization

Select one representative case each after dictionary freeze:
- body-site-specific lane
- restraint/bondage lane
- machine/device lane
- tentacle/non-human appendage lane
- ultra-niche site/object lane

For each family, use the same progression:

1. `CORE_ONLY`
2. `CORE_PLUS_ONE_MEANING_OR_SITE_SUPPORT`
3. `PLUS_ONE_GEOMETRY_OR_VISIBILITY_SUPPORT`
4. `FAMILY_SPECIFIC_RELATION_OR_ORDER_VARIANT`
5. stop; do not keep stacking supports blindly

---

## Tier 3 — binding stress

### T3-1 two actors / one hard target
Check:
- actor-target ownership
- role reversal
- attribute leakage

### T3-2 one actor / multiple hard objects or appendages
Check:
- count
- role split
- site drift
- object degradation

### T3-3 multiple Special retention
Sequence:
- A_ONLY
- B_ONLY
- AB
- BA only if order is the actual question

Do not score AB failure as simple tag-recognition failure until A_ONLY and B_ONLY results are known.

---

## Tier 4 — visibility and geometry

One-question experiments:
- no visibility support vs one visibility support
- no frame support vs one frame support
- no geometry support vs one geometry support

Forbidden first pass:
- changing frame + viewpoint + orientation + visibility simultaneously

Primary trade-off:
- target observability vs composition quality

---

## Tier 5 — Negative interaction

Especially important for anatomy-sensitive or unusual-geometry scenes.

Sequence:
1. family-minimal negative
2. one targeted artifact negative delta
3. generic anatomy-heavy negative only as separate experiment

Do not mechanically treat `bad anatomy` / extra-limb-style negatives as harmless universal defaults for unusual body geometry.

Metrics:
- artifact reduction
- target suppression
- geometry suppression
- false cleanup

---

## Tier 6 — Prompt-only ceiling

Mark `PROMPT_ONLY_LIMIT_CANDIDATE` when repeated fixed-condition tests show:
- persistent actor-target swap
- persistent multi-object binding failure
- persistent contact geometry failure
- visibility rescue repeatedly destroys target
- adding support increases conflict faster than realization

Then compare against an assisted-control lane separately.

Never count assisted-control success as Prompt-only success.

---

## Family-specific stop rules

### WAI v17
Stop adding prose/quality blocks when:
- target does not improve after one meaning + one visibility/geometry support
- finish becomes softer/blurry

### NoobAI 1.1
Before adding NL prose:
- test native-caption Special path
- test relevant canonical/alias surface if approved

### Illustrious
Before globalizing result:
- verify exact version
- distinguish base vs derivative

### Anima
Stop increasing natural-language complexity when:
- relation improves but attributes begin to bleed
- unintended details duplicate across actors

---

## Promotion logic for knowledge

A finding can be promoted from `PROJECT_HYPOTHESIS` only if:
- exact model/version fixed
- actual resolved Prompt recorded
- fixed condition comparison available
- target + quality both reviewed
- no contradictory repeated seed evidence left unexplained

Suggested states:
- `ADOPT_FAMILY_SPECIFIC`
- `ADOPT_CATEGORY_SPECIFIC`
- `HOLD_MORE_SEEDS`
- `HOLD_MODEL_VERSION`
- `CONFLICT`
- `PROMPT_ONLY_LIMIT`

Never promote a model-family result to global grammar automatically.

---

## Boundary

This file prepares Stage10 tests only.
- no Stage10 production run has started
- no production threshold is set
- no final Special ID selection is made
- no #32 or #44 data is modified
