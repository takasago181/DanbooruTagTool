# CURRENT STATE

最終更新: 2026-09-11

## Current Stage

Stage 9 overall Gate 完了 / Stage10 準備Gate実施中 / automated E2E PASS / Special Core Dictionary freeze 完了

本ファイルは現在地のrouting正本。task contract / completion criteria / result evidenceは対応Issueを正本とし、更新競合時はlive Issue / branch / checkpointを優先して同期する。

## Current Core DEV

**Issue #55 — UI-JA V5 production promotion implementation**

Issue #55 `[UI-JA][PRODUCTION][DEV] Promote audited Issue #36 V5 Japanese overlay` をcurrent DEVとして実行する。latest live `main`をbaseとする専用branch `codex/issue55-ui-ja-production-promotion`から、監査済みV5成果物を実local protected runtimeへdeterministic/atomicに反映し、実Windows UI確認後にpost-write auditへ渡す。Issue #36 quarantine branchはread-only evidence/inputであり、production baseまたはmainへの直接mergeには使用しない。

Machine Triage Audit `2660c3106d2252c8aa8f3006f2a1040fd95004db` をDEV受入れ済み。既存Generation Batch 12画像ではWD14 / Kagami-24k / CL Tagger v2.00のraw evaluatorは36/36成功、raw artifact image-ID bindingはPASS。一方、旧Generation Batch reportのevaluator referenceは33件不一致で、reporting/provenance参照 defectだった。retrospective machine-first reductionは0%で、前Batchがrelation/binding/body-site/low-confidence中心だったことによるbatch selection失敗と判定した。

Generation Batch 2は完了。execution/report `7e516bd1ca27c862cdaf023c023bed74e34e6833`、human review `1cd33c7ebec445c3e3870ebce360f9cfee1ffbf9`。16 new images / 8 A/B pairs、WD14 / Kagami / CLは48/48成功、machine-handled 4 images / 2 pairs、human-required 12 images / 6 pairs、blocked 0、image/pair review reduction 25%。人手対象6 pairは6/6 `BOTH_PASS`として記録済み。

Issue #30 accepted integration checkpoint `5629477164`により、16 experiments / 64 images、32 pairs、全件visual audit、既存rawからのevaluator serialization repair、machine-vs-visual calibrationを完了した。Wave 1の再生成・evaluator再実行・Wave 2は行わない。

Current restore anchors:
- Phase 1: `docs/project/ISSUE30_HANDOFF_20260910.md`
- Phase 2 base: `docs/project/ISSUE30_PHASE2_HANDOFF_20260910.md`
- first Generation Batch execution: `6e19da24a9718691b3c2e726bbe256fcb69f4a68`
- first Generation Batch human review: `4a3e6ef5d19b33b5482bcfc86cc362ad6cbad9f3`
- Machine Triage Audit: `2660c3106d2252c8aa8f3006f2a1040fd95004db`
- Generation Batch 2 execution/report: `7e516bd1ca27c862cdaf023c023bed74e34e6833`
- Generation Batch 2 human review: `1cd33c7ebec445c3e3870ebce360f9cfee1ffbf9`
- Issue #30 accepted repair/integration: `9be3fe764c77b7dd6eaba4f791dfb5c3282c8e8b`
- **current continuation: Issue #55 production promotion implementation / stop at `READY_FOR_POST_WRITE_AUDIT` or `HOLD_PRODUCTION_PROMOTION`**
- supporting policy: `docs/project/AUDIT_ARTIFACT_CACHE_POLICY.md`
- broad direction: `docs/project/ISSUE30_BROAD_COVERAGE_AUTOMATION_DIRECTION_20260911.md`
- branch: `codex/issue30-calibration-design`

Issue #42 remains downstream and is still gated on #36 V5 / #34 material UI-JA/search work completion or explicit separation. Phase 2 does not bypass that Gate.

## Workstreams Registry

| TEAM_ID | Status | Issue / scope | Branch / locator | Current phase | Restore anchor |
| --- | --- | --- | --- | --- | --- |
| `DICT:#32:R2` | COMPLETED / PROMOTED / CARRY_FORWARD_ONLY | #32 Special Core Dictionary historical validation | `dict-validation/quarantine` | 2,788/2,788 validation complete。approved effective subsetは#49でproduction反映済み。REVIEW/ITRはparked evidenceとして保持 | Issue #32 + #48 + #49 + #43 freeze |
| `KNOWLEDGE:#44` | ACTIVE / ONGOING / COVERAGE_COMPLETE | persistent generation knowledge corpus | `knowledge/generation-corpus` | 2,788 × WD14 / Kagami-24k / CL Tagger v2.00 desk coverage完了。#30 handoff済み。必要な追加知識/校正返却を担当 | Issue #44 correction checkpoint `5614819866` + commit `557aa4c` |
| `UIJA:#36:V5` | ACTIVE / CHATGPT_LED_REPAIR | Japanese overlay final convergence / semantic repair | `ui-ja/issue36-relaxed-v5-chatgpt-repair` | 30,629 rowsを既存31 audit shardsへ分割し、ChatGPT側で明確な翻訳・意味欠陥を修正/監査。V4はimmutable evidenceとして保持 | Issue #36 latest V5 checkpoint |
| `UIJA-ORCH:#46` | SUPERSEDED / CLOSED | historical independent Codex orchestration for V3.1/V4 | Issue #46 / `codex/issue46-orchestrator` | historical evidence only | Issue #46 superseded checkpoint |
| `UIJA-PARENT:#34` | OPEN / CROSS-CUTTING / SEARCH_RELEVANCE_REMAINS | bilingual search relevance and remaining parent UI concerns | Issue #34 | `anal -> piano/analog_clock/...` 等のsubstring/fuzzy search noiseが主要残件 | Issue #34 current body |
| `TEMP:#30` | COMPLETED / ACCEPTED / INTEGRATED | Forge Neo evaluator calibration & A/B automation | `main @ 9be3fe7` / historical branch `codex/issue30-calibration-design` | Wave 1 16 experiments / 64 images、full visual audit、raw-based evaluator serialization repair、machine-vs-visual calibration完了。再生成・再評価・Wave 2なし | Issue #30 checkpoint `5629477164` / repaired calibration artifacts |
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
- Issue #30 Phase 2 Generation Batch: **COMPLETED / HUMAN REVIEWED**
  - execution `6e19da24a9718691b3c2e726bbe256fcb69f4a68`
  - human review `4a3e6ef5d19b33b5482bcfc86cc362ad6cbad9f3`
  - 3 experiments / 12 generated images
  - GB-001 = 2 × UNCLEAR
  - GB-002 = 2 × BOTH_PASS
  - GB-003 = 2 × BOTH_PASS
  - all 12 were sent to human review; human-work reduction objective not demonstrated
- Issue #30 Machine Triage Audit: **COMPLETED / DEV ACCEPTED**
  - audit `2660c3106d2252c8aa8f3006f2a1040fd95004db`
  - actual evaluator success 36/36
  - raw evaluator image-ID binding PASS
  - old report reference mismatches 33 = reporting defect
  - A/B marker PASS
  - retrospective human-review reduction 0%
- Issue #30 Phase 2 Generation Batch 2: **COMPLETED / HUMAN REVIEWED**
  - execution/report `7e516bd1ca27c862cdaf023c023bed74e34e6833`
  - human review `1cd33c7ebec445c3e3870ebce360f9cfee1ffbf9`
  - 4 experiments / 16 generated images / 8 A/B pairs
  - evaluator success 48/48
  - machine-handled 4 images / 2 pairs
  - human-required 12 images / 6 pairs
  - blocked 0
  - image/pair user-review reduction 25%
  - human-required 6/6 pairs `BOTH_PASS`
- Issue #30 Broad Coverage Wave 1 + evaluator serialization repair: **COMPLETED / ACCEPTED / INTEGRATED**
  - 16 experiments / 64 valid images / 32 A/B pairs
  - full ChatGPT visual audit 64/64 images / 32/32 pairs
  - existing raw artifacts only: 0 image regeneration / 0 evaluator reruns / 192/192 raw artifacts consumed
  - repaired rows 64、stale embedded evaluator locators 189、image hash binding PASS
  - frozen route preservation image 64/64、pair 32/32
  - machine-handled 2 pairs、visual false-safe 1/2 = 50%（N=2 diagnostic only）
  - integration commit `9be3fe764c77b7dd6eaba4f791dfb5c3282c8e8b`、checkpoint `5629477164`
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
- A/B pair単位のmachine/human/blocked routingと削減率を実測する
- **Wave 1だけは校正目的で全valid imageをChatGPT目視監査し、machine-handledも隠さない**
- Wave 1のmachine review-reduction値は「機械なら隠した量」の診断値であり、actual visual-review reductionとは扱わない
- family別false-safeが十分低いと確認できた範囲のみ、後続Waveでsample auditへ移行可能

Review UX carry-forward:
- user-facing contact sheetは**画像 + 大きな番号 + 必要時A/B + 大きな具体的日本語質問**へ簡素化
- Wave 1は全valid imageを複数sheetへ分割。通常4 A/B pairs / 8 images程度、細部判定時はさらに少なくする
- 48–80 imagesを1枚へ潰して小さくしない
- full Prompt/Negative、raw evaluator score、model/settings wallは原則contact sheetから外す
- question font >=24px、可能なら28–32px
- Meiryo -> Yu Gothic -> MS Gothic
- tofu/square表示は review asset invalid
- A/B markerはmanifest conditionから導出し、全A/全B/不一致はBLOCKED

Audit artifact cleanup carry-forward:
- original/source generated imagesはprotected evidenceでありaudit cleanup対象外
- disposable audit copyのみcurrent-only retentionで上書き/削除可能
- cleanup rootは明示設定、sentinel + canonical path + strict descendant + ownership manifestを必須化
- unknown/unowned target、path escape、保護領域混入時は0 deletionでSTOP
- public本体Git historyへ生成監査画像を蓄積しない
- Google Driveは使用しない

## Active / Ready Work

Current core DEV is Issue #55. Scope is limited to audited Issue #36 V5 Japanese overlay production promotion, deterministic post-write verification, and real Windows UI acceptance. Issue #30 is completed and integrated; its Wave 1 generation/re-evaluation routing is historical and inactive.

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
12. #30 Phase 2 Generation Batch 2 machine-first — **SATISFIED / HUMAN REVIEW COMPLETE**
13. #30 Broad Coverage Wave 1 — **SATISFIED / COMPLETED / REPAIR_ACCEPTED / INTEGRATED**
14. #36 V5 repair/audit -> integration/revalidation -> independent promotion gate — **PROMOTION IMPLEMENTATION ACTIVE AS #55 / POST-WRITE AUDIT REMAINS**
15. #34 bilingual search relevance/noise — **REMAINS / resolve or explicitly separate before #42**
16. #42 product-purpose improvement pass — REMAINS
17. #5 formal Prompt handoff — REMAINS / after #42
18. `docs/stages/STAGE_10_PREP.md` remaining checks — REMAINS
19. Stage10 production A/B — NOT STARTED

## Canonical dependency order

Parallel now:
- UI-JA lane: `#36 V5 repair/audit -> integration/revalidation -> independent promotion gate`
- cross-cutting: `#34 bilingual search relevance`, `#24 protected-data safety`

#30 Wave 1は完了済みで、#42 activation Gateを自動解除しない。

#42 activation still waits for material #36/#34 work completion or explicit separation.

Then:
`#42 product-purpose improvement -> #5 formal Prompt handoff -> remaining STAGE_10_PREP checks -> Stage10 production A/B`

## Next Actions

1. #55で監査済み#36 V5 overlayを実local productionへ安全に反映し、`READY_FOR_POST_WRITE_AUDIT`または`HOLD_PRODUCTION_PROMOTION`で停止
2. #34 bilingual search relevance/noiseをresolveまたはStage10 Gateから明示分離
3. #42は#36/#34 material homework完了または明示分離まで`RESERVED / GATED`として維持
4. managementがGate確認後に#42をcurrent core DEVとして明示activate
5. #42 product-purpose improvement pass
6. #5 formal Prompt handoff
7. `STAGE_10_PREP.md` remaining checksをclose
8. 全Gate完了後のみ Stage10 production A/B
9. parallel safety debt: #24 protected-data backup / restore verification

## Source-of-Truth Rule

- current core DEV = **Issue #55 UI-JA V5 production promotion implementation**
- current DEV Issue number = **#55**
- current continuation = **production write + deterministic verification + real Windows UI acceptance; stop before independent post-write audit**
- Issue #30 accepted integration checkpoint = `5629477164`
- Issue #30 accepted main commit = `9be3fe764c77b7dd6eaba4f791dfb5c3282c8e8b`
- audit cleanup policy = `docs/project/AUDIT_ARTIFACT_CACHE_POLICY.md`
- broad direction = `docs/project/ISSUE30_BROAD_COVERAGE_AUTOMATION_DIRECTION_20260911.md`
- Machine Triage Audit accepted evidence = `2660c3106d2252c8aa8f3006f2a1040fd95004db`
- first Generation Batch execution evidence = `6e19da24a9718691b3c2e726bbe256fcb69f4a68`
- first Generation Batch human review evidence = `4a3e6ef5d19b33b5482bcfc86cc362ad6cbad9f3`
- Batch 2 execution/report evidence = `7e516bd1ca27c862cdaf023c023bed74e34e6833`
- Batch 2 human review evidence = `1cd33c7ebec445c3e3870ebce360f9cfee1ffbf9`
- Phase 1 evidence is frozen; do not restart original 128-image pilot wholesale
- final formal concept name = **`Special Core Dictionary`**
- #32/#48/#49/#43 dictionary validation/promotion/freeze chain is completed; do not restart it
- #32 parked REVIEW / IMAGE_TEST_REQUIRED evidence is carry-forward asset and must not be discarded
- #44 exact evaluator desk coverage is completed
- Issue #46 is superseded historical evidence; current UI-JA route = Issue #36 V5
- DEV切替時は live GitHub Issue + CURRENT_STATE を同一管理操作で整合させる
- completion reportだけで次Gateへ進まない。live GitHub stateを再確認する
