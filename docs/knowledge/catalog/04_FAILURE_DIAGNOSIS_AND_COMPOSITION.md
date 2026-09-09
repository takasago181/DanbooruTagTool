# 04 — Failure Diagnosis / Composition

## 失敗時の基本診断順

`traceability -> semantic identity -> unary activation -> composition/binding -> visibility/geometry -> Negative collision -> Prompt competition/pruning -> LoRA -> seed sensitivity -> assisted-control ceiling -> evaluator blindness`

## 重要な区別

### unary success != composite success
A単独/B単独が出てもABで崩れることがある。
AB失敗を「Bタグをモデルが知らない」と即断しない。

### presence != relation
画像に必要な名詞が全部あっても、以下が違えば失敗:
- actor
- target
- owner
- body-site
- source / destination
- functional relation
- topology
- count

### visibility failure != semantic failure
crop / occlusion / frame不足で判定できないケースを、concept omissionと分ける。

## multi-Specialの切り分け

推奨順:
1. A_ONLY
2. B_ONLY
3. AB minimal
4. AB + visibility support
5. AB + geometry/binding support
6. resource disambiguation
7. aestheticは最後

## 代表failure class

- `CONCEPT_OMITTED`
- `WRONG_ACTOR_TARGET`
- `WRONG_BODY_SITE`
- `WRONG_COUNT`
- `OBJECT_ONLY_RELATION_FAIL`
- `TOPOLOGY_FAIL`
- `VISIBILITY_UNCLEAR`
- `STYLE_CONTEXT_LEAK`
- `NEGATIVE_COLLISION_SUSPECTED`
- `POSTPROCESS_RESCUE`
- `ASSISTED_ONLY`
- `EVALUATOR_UNCOVERED`
- `UNCLEAR`

## concept density

難しさはraw token長だけでなく、
- requested concept数
- role数
- binding数
- actor/resource数
- exact count
- unusual geometry
で上がる。

## seed

seedは実験identityの一部。
1 seedの成功/失敗はケース証拠であって一般則ではない。

## 原本

- `research/BATCH_A_FALSE_ASSUMPTION_PREVENTION_20260909.md`
- `research/HARD_FETISH_COMPOSITE_FAILURE_MATRIX_20260909.md`
- `research/BATCH_C_EVIDENCE_RELIABILITY_20260909.md`
- `GENERATION_KNOWLEDGE_CORPUS.md`