# Issue #30 Phase 2 reuse-only human review — 2026-09-11

## RESULT

`CAL-023 double handjob` の既存2ペア・4画像を人手レビューした結果、両seedとも A条件のみ成立し、`A_ONLY_PASS` となった。

## EVIDENCE

| Pair | A | B | Result | Observation |
|---|---|---|---|---|
| seed 30230 | #1: 両手による手淫が成立 | #2: 背中を向けた女と遠方のぼやけた男たち。要求行為なし | `A_ONLY_PASS` | AのみPASS |
| seed 30231 | #3: 両手による手淫が成立 | #4: 黒い服の女2人と男1人が立っているだけ | `A_ONLY_PASS` | AのみPASS |

- Review pairs: **2**
- Reviewed images: **4**
- New images: **0**
- New seeds: **0**
- Evaluator reruns: **0**

## DECISION

この reuse-only 条件では、`double handjob` の具体的な可視条件について A-only の再現が2/2ペア確認された。これは人手レビューによる限定的な evidence であり、Taggerや自動判定への昇格、一般的な relation/count semantics のAUTO化は行わない。

Phase 2は diminishing returns に達した候補として、DEV/ChatGPTによる close判断へ渡す。`CAL-024 teamwork (sexual)` と `CAL-032 anus + after footjob` は引き続き DEFER。追加生成・追加seedは行わない。

## LIMITATION / NEXT

判定対象は既存 Phase 1画像の「2人または両手による手淫が2つ同時に成立しているか」という可視 predicate に限る。次はDEV/ChatGPTが Phase 2 close、または別途根拠を示した最終狭域実験の要否を判断する。
