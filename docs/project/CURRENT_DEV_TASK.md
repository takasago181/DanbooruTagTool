# CURRENT DEV TASK

最終同期: 2026-09-11

## Mirror Metadata

- Source Issue: **#30** `[Stage10-PREP][PHASE2_ACTIVE] Targeted evaluator refinement before #42`
- State: **ACTIVE / PHASE2_TARGETED_REFINEMENT / REUSE_ONLY_REVIEW_AUTHORIZED**
- Branch: `codex/issue30-calibration-design`
- Previous completed phase: #30 Phase 1 representative evaluator calibration
- Completed Phase 2 checkpoints:
  - Wave 1 + human review (`233a2a25b58de388cdf4ccff1183fca0a3260472`)
  - Wave 2 execution (`b478f32042fa3b4111a6b86c24cb6c77655d579a`)
  - Wave 2 human review (`34aa09a8d7c82bbfaf798c68c8c98a72a65cce50`, machine-readable `63ac1ee49edef710a3b10135a7a2d33250d6cb96`)
- Current Stage: Stage10準備Gate実施中

## Purpose

Issue #30 Phase 1は完了・凍結済み。#36/#34が#42 activationを待たせている間に、Stage10でユーザー目視負担をさらに減らせるかを、既存evaluator成果を中心に狭く検証する。

現在は**新規生成を行わず、既存Phase 1画像だけで残る個数系 / multi-Special系の有用な問いを再利用レビューする段階**。

Primary restore anchors:
- `docs/project/ISSUE30_HANDOFF_20260910.md` — Phase 1
- `docs/project/ISSUE30_PHASE2_HANDOFF_20260910.md` — Phase 2
- `docs/project/ISSUE30_PHASE2_EXECUTION_SPEC_20260910.md` — Phase 2 base execution contract
- `docs/project/ISSUE30_PHASE2_WAVE2_EXECUTION_SPEC_20260910.md` — completed Wave 2 contract
- `docs/project/ISSUE30_PHASE2_REUSE_REVIEW_SPEC_20260911.md` — **current continuation contract**
- `docs/project/ISSUE30_PHASE2_CHECKPOINT_TEMPLATE.md` — repository/DEV handoff format

## Accepted evidence

### Phase 1

- 128 unique images / WD14-Kagami-CL each 128/128
- minimal review 19
- Taggers are assistive triage, not Special semantic authority.

### Wave 1

- P2-001 `vibrator in anus`: 2 seedとも `BOTH_FAIL`。device/body-site binding不成立。
- P2-002 `holding sex toy`: `A_ONLY_PASS` 1件 + contrast contaminationを伴う `BOTH_PASS` 1件。
- P2-003 `breast expansion`: 2 seedとも `BOTH_PASS`。今回条件ではNegativeへの同一target追加による一貫した抑制なし。

### Wave 2

- P2-004 `double dildo` vs `dildo`: `double dildo` は両端型1本ではなく2本のdildoとして出た。これは `EXACT_COUNT_RETENTION` の正答ではなく、`SHAPE_SPECIFIC_REALIZATION_FAILURE / LEXICAL_DOUBLE_TO_COUNT_COLLAPSE` として保持する。
- P2-005 `anal` vs `anal penetration`:
  - seed 42011 = `B_ONLY_PASS`
  - seed 42012 = `A_ONLY_PASS`
  - canonical/alias surfaceはこのWAI17 profileでseed-sensitive。安定同等とは言えない。
- relation/binding/body-site/count/compound semanticsは引き続き `HUMAN_REVIEW_ONLY`。
- machine positiveはrelated object/body-part presenceの補助証拠に留まり、insertion/binding/count等のsemantic PASSにはしない。

## Frozen policy

- direct / non-relation / simple unaryのみ補助AUTO候補。
- relation/binding / actor-object / body-site / quantity / spatial / insertion/contact/restraint / compound / component-only / disagreement / low-confidenceは原則HUMAN REVIEW。
- gray/unreadable/corrupt/hash/metadata/provenance欠損はsemantic評価前にBLOCKED。
- invalid target/contrastはexperiment-validity failureとしてevaluator failureから分離。
- Wave 1/2はstructural AUTO promotionの根拠にしない。

## Current continuation — Reuse-only review

Codexは `docs/project/ISSUE30_PHASE2_REUSE_REVIEW_SPEC_20260911.md` を現在の継続仕様として読む。

### Immediate order

1. latest `origin/main` を取得する。
2. `origin/main` を `codex/issue30-calibration-design` へ mergeする。rebase/force rewriteは禁止。
3. frozen Phase 1 128-image artifacts / evaluator outputsを再利用する。
4. 個数系候補 `CAL-022 / CAL-023 / CAL-024` をcurrent local canonical dataで確認し、**画像だけでPASS条件を短い日本語にできるケースだけ**選ぶ。
5. `CAL-023 double handjob` は、local canonical日本語が明確な二者/二重行為要件を示す場合の優先候補。
6. `CAL-032 anus + after footjob` は、両Specialの成功条件を静止画だけで直接観察できる場合のみ使用する。`after footjob` が文脈推測を要するならDEFERする。
7. 最大2 experiments / 8 reviewed images。1 experiment / 4 imagesで十分ならそこで止める。
8. **新規画像生成 0 / 新規seed 0 / evaluator再実行不要**。既存結果を利用する。
9. bilingual contact sheetを作成し、ユーザーに見るべき条件を具体的日本語で表示する。
10. repositoryへdesign/manifest/resultをcommit/pushし、user/DEV review待ちでSTOPする。

### Review question rule

質問は「何が画像に出ていればPASSか」をそのまま書く。

良い例:
- `2人が同時にこの行為へ参加しているか？`
- `要求された2つの行為が同時に成立しているか？`

禁止する抽象表現:
- `同じ意味を保持しているか？`
- `同じ視覚的対象を誘発するか？`
- `semantic retentionは成立したか？`

1つの短い具体的日本語質問にできないcaseはreviewへ出さずDEFERする。

For each selected case, record:
- `visible_pass_condition_ja`
- `visible_fail_condition_ja`
- `why_this_is_judgeable_from_one_still_image`

### Review UX

各review cellに:
- image number
- case ID
- A/B
- seed
- concrete Japanese question
- actual Positive Prompt tags/tokens: `English (日本語)`
- actual Negative Prompt tags/tokens: `English (日本語)`

日本語フォント:
- Meiryo
- Yu Gothic
- MS Gothic

□/tofu表示は `REVIEW_ASSET_INVALID / BLOCKED`。

ユーザーはraw evaluator logを見ない。

## Existing-tool-first

- Multi Prompt Slots
- built-in X/Y/Z
- Forge Neo Infinite Image Browsing
- Forge API
- existing Issue #30 runner/review tooling
- WD14 / Kagami-24k / CL Tagger v2.00 existing outputs

新規extensionや大型automation platformは、具体的な不足と実益が証明されない限り導入しない。

## Decision labels

- ADOPT
- HOLD
- REJECT
- TARGETED_IMAGE_TEST_REQUIRED
- DEFER

## Hard prohibitions

- current reuse passでの新規画像生成禁止
- original 128-image pilotの全再実行禁止
- 2,788-image sweep禁止
- Stage10 production A/B禁止
- production `data/**`変更禁止
- #32 verdict / canonical変更禁止
- Tagger direct-matchをstructural Special truthへ昇格禁止
- relation/binding全面AUTO化禁止
- Phase 1/Wave 1/Wave 2 evidenceのmetric改善目的reinterpretation禁止
- model-family flattening禁止
- 大型独自automation platform禁止
- runtime LLM dependency禁止
- unnecessary extension installation禁止

## Reuse-only completion checkpoint

repositoryから取得可能にする:
- selected existing case(s)
- selected/deferred rationale
- exact concrete Japanese review question(s)
- reused image count
- reused evaluator count
- review pairs / reviewed images の別件数
- bilingual contact sheet locator
- selected Japanese font / display check
- design/manifest/result
- remaining uncertainty

終了後は追加生成・追加wave・Stage10へ自動進行せずSTOPする。

## Repository handoff

Codexはprivate Issue書込みを完了条件にしない。review可能なbranch/commit、実行report、tests、protected-data確認、local-only artifact locatorをrepositoryへcommit/pushする。

DEV/ChatGPTはGitHubから回収し、Issue #30へ `RESULT / EVIDENCE / DECISION / LIMITATION / NEXT` checkpointを記録する。

## Downstream

#42は依然として #36 V5 / #34 material UI/search workの完了または明示分離待ち。Phase 2はそのGateを迂回しない。

## Start / continuation Gate

Codexは作業開始前に必ず:
1. latest `main` を取得
2. Issue #30がPHASE2_ACTIVEであることを確認
3. `CURRENT_STATE.md` current core DEV = #30 Phase 2 reuse-only review を確認
4. 本ファイル Source Issue = #30 を確認
5. `ISSUE30_PHASE2_REUSE_REVIEW_SPEC_20260911.md` を確認
6. scope不一致ならSTOP

Current routing authority: `docs/project/CURRENT_STATE.md`.
