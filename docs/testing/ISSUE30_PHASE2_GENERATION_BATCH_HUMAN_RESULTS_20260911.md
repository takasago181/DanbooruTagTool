# Issue #30 Phase 2 Generation Batch Wave human review — 2026-09-11

## RESULT

12画像・6ペアをレビューした。`GB-002` と `GB-003` は各2ペアとも `BOTH_PASS`。`GB-001` は性具を手に持つ点は確認できるが、バイブレーター同定が曖昧なため2ペアとも `UNCLEAR` とした。

## EVIDENCE

| Pair | A | B | Result |
|---|---|---|---|
| GB-001 / seed 43001 | 手に持った性具、ディルド寄り | 手に持つがディルドっぽい | `UNCLEAR` |
| GB-001 / seed 43002 | ディルド | 電マ、バイブレーターとも解釈可能 | `UNCLEAR` |
| GB-002 / seed 43011 | 成立 | 成立 | `BOTH_PASS` |
| GB-002 / seed 43012 | 成立 | 成立 | `BOTH_PASS` |
| GB-003 / seed 43021 | 成立 | 成立 | `BOTH_PASS` |
| GB-003 / seed 43022 | 成立 | 成立 | `BOTH_PASS` |

- Review pairs: **6**
- Reviewed images: **12**
- New images: **0**
- New seeds: **0**
- Evaluator reruns: **0**

## DECISION

`SINGLE_SUPPORT_TAG_EFFECT`（GB-002）と `SPECIFIC_ONLY_VS_BROAD_PLUS_SPECIFIC`（GB-003）は、今回の4画像単位ではA/Bの双方が成立しており、追加タグによる優位性は確認できない。`MULTI_SPECIAL_RETENTION`（GB-001）は手持ち状態は成立するが、バイブレーターという具体的同定が不確実で、明確なPASSにはしない。

これは人手レビューによる限定 evidence であり、relation・binding・body-site・count・multi-person semantics の自動昇格は行わない。Phase 2 close/diminishing-return はDEV/ChatGPTが判断する。

## LIMITATION / NEXT

GB-001の「電マ」と「バイブレーター」の語義境界が残る。追加seedは自動で行わず、追加実験をする場合も別途狭い根拠が必要。現batchで停止する。
