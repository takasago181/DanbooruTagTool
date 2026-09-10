# CURRENT STATE

最終更新: 2026-09-11

## Current Stage

Stage 9 overall Gate 完了 / Stage10 準備Gate実施中 / automated E2E PASS / Special Core Dictionary freeze 完了

本ファイルは現在地のrouting正本。task contract / completion criteria / result evidenceは対応Issueを正本とし、更新競合時はlive Issue / branch / checkpointを優先して同期する。

## Current Core DEV

**Issue #30 / PHASE2_TARGETED_REFINEMENT / MACHINE_TRIAGE_AUDIT**

Issue #30 Phase 1 / Phase 2 Wave 1 / Wave 2 / reuse-only review / Generation Batchは実行済み。

Generation Batchでは3実験・12画像をまとめて生成し、WD14 / Kagami-24k / CL Tagger v2.00を通したと報告されたが、全6ペア / 12画像が最初から人間レビュー対象になっており、「機械で処理できる分を先に除外し、残りだけユーザーへ回す」という本来の省力化目的を満たしていない。

さらにGeneration Batch resultの evaluator reference に同一最終artifact参照が混ざる疑いがあるため、現在は**新規生成を止めて evaluator provenance と machine-first routing を監査する段階**。

Current restore anchors:
- Phase 1: `docs/project/ISSUE30_HANDOFF_20260910.md`
- Phase 2 base: `docs/project/ISSUE30_PHASE2_HANDOFF_20260910.md`
- Generation Batch execution: `6e19da24a9718691b3c2e726bbe256fcb69f4a68`
- Generation Batch human review: `4a3e6ef5d19b33b5482bcfc86cc362ad6cbad9f3`
- **current continuation: `docs/project/ISSUE30_PHASE2_MACHINE_TRIAGE_AUDIT_20260911.md`**
- branch: `codex/issue30-calibration-design`

`CURRENT_DEV_TASK.md` is synchronized to Source Issue #30 / PHASE2_MACHINE_TRIAGE_AUDIT.

Issue #42 remains downstream and is still gated on #36 V5 / #34 material UI-JA/search work completion or explicit separation. Phase 2 does not bypass that Gate.

## Workstreams Registry

| TEAM_ID | Status | Issue / scope | Branch / locator | Current phase | Restore anchor |
| --- | --- | --- | --- | --- | --- |
| `DICT:#32:R2` | COMPLETED / PROMOTED / CARRY_FORWARD_ONLY | #32 Special Core Dictionary historical validation | `dict-validation/quarantine` | 2,788/2,788 validation complete。approved effective subsetは#49でproduction反映済み。REVIEW/ITRはparked evidenceとして保持 | Issue #32 + #48 + #49 + #43 freeze |
| `KNOWLEDGE:#44` | ACTIVE / ONGOING / COVERAGE_COMPLETE | persistent generation knowledge corpus | `knowledge/generation-corpus` | 2,788 × WD14 / Kagami-24k / CL Tagger v2.00 desk coverage完了。#30 handoff済み。必要な追加知識/校正返却を担当 | Issue #44 correction checkpoint `5614819866` + commit `557aa4c` |
| `UIJA:#36:V5` | ACTIVE / CHATGPT_LED_REPAIR | Japanese overlay final convergence / semantic repair | `ui-ja/issue36-relaxed-v5-chatgpt-repair` | 30,629 rowsを既存31 audit shardsへ分割し、ChatGPT側で明確な翻訳・意味欠陥を修正/監査。V4はimmutable evidenceとして保持 | Issue #36 latest V5 checkpoint |
| `UIJA-ORCH:#46` | SUPERSEDED / CLOSED | historical independent Codex orchestration for V3.1/V4 | Issue #46 / `codex/issue46-orchestrator` | historical evidence only | Issue #46 superseded checkpoint |
| `UIJA-PARENT:#34` | OPEN / CROSS-CUTTING / SEARCH_RELEVANCE_REMAINS | bilingual search relevance and remaining parent UI concerns | Issue #34 | `anal -> piano/analog_clock/...` 等のsubstring/fuzzy search noiseが主要残件 | Issue #34 current body |
| `TEMP:#30` | ACTIVE / CORE_DEV / PHASE2_MACHINE_TRIAGE_AUDIT | Forge Neo evaluator calibration & A/B automation | `codex/issue30-calibration-design` | 既存Generation Batch 12画像のevaluator provenanceとmachine-first human-review削減を監査。新規生成0 | `docs/project/ISSUE30_PHASE2_MACHINE_TRIAGE_AUDIT_20260911.md` |
| `PREP:#42` | RESERVED / GATED | Stage10 pre-evaluation product-purpose improvement | Issue #42 | #30 Phase 1 prerequisite satisfied。#36/#34 material homework完了または明示分離後にactivate | Issue #42 |
| `PROMPT:#5` | GATED | Stage10 formal Prompt handoff | Issue #5 | #42 result後にformal handoff | Issue #5 |
| `MAINT:#24` | OPEN / SAFETY_DEBT | Local protected data backup / restore verification | Issue #24 | GitHub外protected dataのbackup/restore・manifest・非破壊restore検証 | Issue #24 |

## Completed

- Stage9 overall Gate: **PASS / completed**
- Issue #28 automated E2E: **PASS / completed**
- Issue #6 Forge Neo comparison environment: **PASS_WITH_NOTE / completed**
- Issue #35 Japanese-first desktop UI: **ISSUE35_FINAL_COMPLETION_PASS / completed / closed**
- Issue #32 dictionary validation: **completed**
- Issue #48 independent final promotion audit: **completed**
- Issue #49 production promotion: **completed / post-write audited / merged**
- Issue #43 Special Core Dictionary naming/freeze: **PASS_ISSUE43_FREEZE / completed**
- Issue #44 final evaluator desk coverage: **SATISFIED / HANDOFF COMPLETE**
- Issue #30 Phase 1 representative evaluator calibration: **COMPLETED / FROZEN EVIDENCE**
  - 32 Special cases × 4 = 128 unique images
  - WD14 / Kagami / CL each 128/128
  - minimal human review 19
  - provisional AUTO-support 8 / HUMAN_REVIEW_ONLY 9 / BLOCKED 2 / UNRESOLVED 1
  - broad Special semantic AUTO rejected; Taggers remain assistive triage
- Issue #30 Phase 2 Wave 1: **COMPLETED / HUMAN REVIEWED**
- Issue #30 Phase 2 Wave 2: **COMPLETED / HUMAN REVIEWED**
  - P2-004 `double dildo`: exact-count testとしては不適切。shape/lexical collapse evidenceとして保持
  - P2-005 `anal` vs `anal penetration`: seed-sensitive (`B_ONLY_PASS` / `A_ONLY_PASS`)
  - structural AUTO promotionなし
- Issue #30 Phase 2 reuse-only review: **COMPLETED / HUMAN REVIEWED**
  - `CAL-023 double handjob`
  - 2 pairs / 4 existing images
  - both `A_ONLY_PASS`
  - new generation 0 / evaluator rerun 0
- Issue #30 Phase 2 Generation Batch: **COMPLETED / HUMAN REVIEWED / DESIGN_REVIEW_REQUIRED**
  - execution `6e19da24a9718691b3c2e726bbe256fcb69f4a68`
  - human review `4a3e6ef5d19b33b5482bcfc86cc362ad6cbad9f3`
  - 3 experiments / 12 generated images / reported evaluator runs 36
  - GB-001 = 2 × UNCLEAR
  - GB-002 = 2 × BOTH_PASS
  - GB-003 = 2 × BOTH_PASS
  - all 12 were sent to human review; human-work reduction objective not demonstrated
- Issue #46 historical orchestration: **superseded / closed**

## Frozen terminology

- formal concept: **`Special Core Dictionary`**
- historical snapshot/corpus / compatibility identifier: `Special2788`
- user-selected nucleus: `Core Tag Set`
- per-entry: `Special` where unambiguous; `Special Core Entry` in explicit prose when useful
- relationship: `Special Core Dictionary -> Core Tag Set -> Auxiliary/support -> Prompt`

## Quarantine carry-forward rule — DO NOT DISCARD

#32でproductionへpromotionしなかった項目は将来の検証資産として保持する。

- Special REVIEW: 305
- Special IMAGE_TEST_REQUIRED: 17
- semantic-support IMAGE_TEST_REQUIRED: 33 rows
- その他、証拠不足 / model-family依存 / controlled image evidence待ちでparkされた候補

非promotionは非破棄。#42 / #30 Phase 2 / Stage10 controlled tests等で必要に応じて再評価する。

## Issue #30 Phase 1 / Phase 2 policy — frozen carry-forward

TaggerはSpecial Core Dictionaryの完全なsemantic ground truthにしない。

Allowed role:
- automatic pre-screening
- direct/non-relation/simple-unaryの補助候補
- disagreement / low-confidence detection
- review prioritization
- safe abstention / HUMAN REVIEW routing

Default HUMAN REVIEW:
- relation / binding
- actor/subject/object
- body-part ownership/site
- quantity / multi-person assignment
- spatial topology/direction
- insertion / contact / restraint
- compound retention
- component-only
- evaluator disagreement / weak confidence

Artifact/experiment separation:
- gray/unreadable/corrupt/hash/metadata/provenance failure -> BLOCKED before semantic evaluation
- target/contrast generation不成立 -> experiment validity failure; evaluator精度と混同しない

Machine-first user-work rule:
- future batchは `generate -> evaluator -> machine triage -> unresolvedだけuser review`
- machine-handled候補をmandatory contact sheetから外す
- 構造意味をTagger単独でAUTO truthにしない
- evaluator run countは実artifact成功数から計算し、`images × 3` の算術だけで成功扱いしない
- per-image evaluator reference整合性を自動検査する

Review UX carry-forward:
- user-facing contact sheetは**画像 + 大きな番号 + 必要時A/B + 大きな具体的日本語質問**へ簡素化
- full Prompt/Negative、seed、case ID、evaluator score、model/settings、token glossaryは原則contact sheetから外す
- question font >=24px、可能なら28–32px
- Meiryo -> Yu Gothic -> MS Gothic
- tofu/square表示は review asset invalid
- A/B markerはmanifest conditionから導出し、全A/全B/不一致はBLOCKED

## Active / Ready Work

### #30 Phase 2 — CURRENT CORE DEV / MACHINE_TRIAGE_AUDIT

Current contract:
`docs/project/ISSUE30_PHASE2_MACHINE_TRIAGE_AUDIT_20260911.md`

Current objective:
1. existing 12 Generation Batch imagesの各WD14/Kagami/CL raw artifactを確認
2. evaluator referenceが各image IDへ正しく紐付くか検証
3. actual successful evaluator run countを算出
4. report-only defectならreportを修正し、evaluator再実行しない
5. missing/wrong raw evaluatorだけ既存画像へ限定再実行
6. current 12 imagesをretrospective machine-first routing
7. 既存human resultと比較し、人間レビュー削減率を計測
8. userにはcurrent 12 imagesを再レビューさせない
9. commit/push後STOP

Future Batch is **NOT YET AUTHORIZED**。
Audit PASS後の候補仕様:
- 4–5 experiments
- normally 16–20 images
- hard cap 20
- machine-judgeable direct/simple-unary + genuinely structural testsを混在
- 全部structuralにして全画像user reviewへ回す設計は禁止

### #36 UI-JA V5 — ChatGPT-led repair/audit

Current policy:
- GitHub remains canonical; chat history is not canonical.
- V4 artifacts remain frozen as evidence. V5 is a separate repair lane.
- current branch: `ui-ja/issue36-relaxed-v5-chatgpt-repair`
- 30,629-row table is processed through the existing 31 audit shards.
- ChatGPT performs translation/semantic repair review directly.
- Codex/Luna is not used for translation-quality judgment or semantic audit in the current lane.
- after all shards: integration/revalidation -> separate independent production-promotion gate.

### #34 UI-JA parent remaining concerns

Primary remaining concern is bilingual search relevance/noise, including substring/fuzzy collisions such as `anal -> piano / analog_clock / analogous_colors`.
Before #42 activation, material concern must be completed or explicitly separated from the Stage10 Gate.

### #24 protected-data maintenance

GitHub外local protected dataについて、backup location / freshness / manifest / restore verification / rebuildabilityを明示する。
本件はcore DEVを自動的に占有しない。

## WAITING / GATED

### #42 Stage10 pre-evaluation product-purpose improvement

Dictionary promotion/freeze prerequisite: **SATISFIED**。
#44 evaluator coverage prerequisite: **SATISFIED**。
#30 Phase 1 representative calibration prerequisite: **SATISFIED**。

Phase 2は追加 refinement laneであり、#42 Gateを自動解除しない。

残るactivation Gate:
- #36 V5 material UI-JA/data homework complete or explicitly separated
- #34 material bilingual-search/search-noise concern complete or explicitly separated

### #5 PROMPT formal handoff

Formal completionは以下の後:
1. #43 final freeze handoff — SATISFIED
2. #44 evaluator coverage return — SATISFIED
3. #30 representative routing/calibration Phase 1 — SATISFIED
4. #42 product-purpose improvement result — REMAINS

## Current Gates

1. Stage9 overall Gate — SATISFIED
2. #28 automated E2E — SATISFIED
3. Stage10 KNOWLEDGE handoff base — SATISFIED
4. #6 Forge Neo comparison environment — SATISFIED / PASS_WITH_NOTE
5. #30 infrastructure plumbing — SATISFIED / PASS_PIPELINE
6. #35 completion — SATISFIED
7. #32 validation + independent promotion audit — SATISFIED
8. #49 production FIX implementation + post-write audit + production merge — SATISFIED
9. #43 naming/final dictionary freeze — SATISFIED
10. #44 final evaluator coverage — SATISFIED
11. #30 Phase 1 controlled representative calibration + minimal review — **SATISFIED / FROZEN**
12. #30 Phase 2 targeted refinement — **ACTIVE / MACHINE_TRIAGE_AUDIT**
13. #36 V5 repair/audit -> integration/revalidation -> independent promotion gate — **ACTIVE**
14. #34 bilingual search relevance/noise — **REMAINS / resolve or explicitly separate before #42**
15. #42 product-purpose improvement pass — REMAINS
16. #5 formal Prompt handoff — REMAINS / after #42
17. `docs/stages/STAGE_10_PREP.md` remaining checks — REMAINS
18. Stage10 production A/B — NOT STARTED

## Canonical dependency order

Parallel now:
- Core DEV: `#30 Phase 2 machine-triage/evaluator-provenance audit`
- UI-JA lane: `#36 V5 repair/audit -> integration/revalidation -> independent promotion gate`
- cross-cutting: `#34 bilingual search relevance`, `#24 protected-data safety`

#42 activation still waits for material #36/#34 work completion or explicit separation.

Then:
`#42 product-purpose improvement -> #5 formal Prompt handoff -> remaining STAGE_10_PREP checks -> Stage10 production A/B`

## Next Actions

1. #30 evaluator provenance + machine-first routing audit; new generation 0
2. audit resultから、機械で安全に除外できるreview範囲を確定
3. 必要なら4–5 experiments / 16–20 imagesの次Batchを別途authorize
4. #36 V5 workをGitHub正本へ継続反映
5. #34 bilingual search relevance/noiseをresolveまたはStage10 Gateから明示分離
6. #30 Phase 2 close/diminishing-return判断
7. managementがGate確認後に#42をcurrent core DEVとして明示activate
8. #42 product-purpose improvement passで#30 Tagger-assisted triage policyを統合
9. #5 formal Prompt handoff
10. `STAGE_10_PREP.md` remaining checksをclose
11. 全Gate完了後のみ Stage10 production A/B
12. parallel safety debt: #24 protected-data backup / restore verification

## Source-of-Truth Rule

- current core DEV = **Issue #30 / Phase 2 Machine Triage Audit**
- `CURRENT_DEV_TASK.md` Source Issue = **#30**
- current continuation contract = `docs/project/ISSUE30_PHASE2_MACHINE_TRIAGE_AUDIT_20260911.md`
- Generation Batch execution evidence = `6e19da24a9718691b3c2e726bbe256fcb69f4a68`
- Generation Batch human review evidence = `4a3e6ef5d19b33b5482bcfc86cc362ad6cbad9f3`
- future Generation Batch is not authorized until current audit is accepted
- Phase 1 evidence is frozen; do not restart original 128-image pilot wholesale
- final formal concept name = **`Special Core Dictionary`**
- #32/#48/#49/#43 dictionary validation/promotion/freeze chain is completed; do not restart it
- #32 parked REVIEW / IMAGE_TEST_REQUIRED evidence is carry-forward asset and must not be discarded
- #44 exact evaluator desk coverage is completed
- Issue #46 is superseded historical evidence; current UI-JA route = Issue #36 V5
- DEV切替時は Issue + CURRENT_STATE + CURRENT_DEV_TASK を同一管理操作で同期する
- completion reportだけで次Gateへ進まない。live GitHub stateを再確認する
