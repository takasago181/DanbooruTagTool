# 03 — Prompt / Support Design

## 基本原則

**minimum sufficient Prompt = 最短Promptではない。**

意味核を守り、冗長・競合・未検証要素を削った状態を目指す。

## Protected semantic nucleus

削除してはいけない候補:
- selected Special
- intrinsic count
- actor / owner / target
- body-site
- intrinsic relation
- implement / modifier
- model-specific trigger syntax（根拠がある場合のみ）

## Support role

現行分類:
- Meaning support
- Geometry / Kinematic
- Visibility
- Resource parking / disambiguation
- Aesthetic
- Optional variation

supportは意味的に正しくても、生成上は neutral / harmful になり得る。

### anti-supportの主因
- same-role composition conflict
- actor/resource conflict
- count conflict
- strong trigger prior
- Negative collision
- LoRA context leakage
- Prompt density / concept competition

## 削る順

1. unrelated decoration / excess aesthetic-quality
2. duplicate / synonym
3. same-role frame/viewpoint conflict
4. unproven broad parent / constituent
5. structural valueのない長い自然文
6. visibility / geometry / resource supportを1個ずつ
7. weight調整は構造競合を除去した後

## broad + specific

**自動採用しない。**

rare conceptでは頻出constituentを足す価値があるが、common priorへ引っ張る可能性もある。

扱い:
- A/B candidate
- semantic authorityにしない
- model/version依存

## Negative Prompt

Negativeは単なる掃除役ではない。

- targetと意味が重なるNegativeは意図した概念を抑制し得る。
- `bad anatomy / extra limbs / extra arms` 等は unusual anatomy / multi-appendage / count-changing caseで高リスク。
- exact effectはmodel-familyごとにON/OFF test。

## quality / aesthetic

WAI17では作者が盛りすぎを警告。

一般ルールにせず、exact model author baselineを優先。

## one experiment = one question

例:
- visibility supportの効果だけ
- broad parent追加だけ
- Negative ON/OFFだけ
- weight変更だけ

同時に複数変数を動かさない。

## 原本

- `research/BATCH_B_MINIMUM_SUFFICIENT_PROMPT_20260909.md`
- `research/BATCH_A_FALSE_ASSUMPTION_PREVENTION_20260909.md`
- `GENERATION_KNOWLEDGE_CORPUS.md`
- `docs/AUXILIARY_TAG_ROLE_POLICY.md`
- `docs/stages/STAGE_10_KNOWLEDGE_HANDOFF.md`