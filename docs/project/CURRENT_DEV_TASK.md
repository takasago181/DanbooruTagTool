# CURRENT DEV TASK

最終同期: 2026-09-10

## Mirror Metadata

- Source Issue: **#30** `[Stage10-PREP][PHASE2_ACTIVE] Targeted evaluator refinement before #42`
- State: **ACTIVE / PHASE2_TARGETED_REFINEMENT / WAVE2_AUTHORIZED_AFTER_PREREQUISITES**
- Branch: `codex/issue30-calibration-design`
- Previous completed phase: #30 Phase 1 representative evaluator calibration
- Completed Phase 2 checkpoint: Wave 1 + human review (`233a2a25b58de388cdf4ccff1183fca0a3260472`)
- Current Stage: Stage10準備Gate実施中

## Purpose

Issue #30 Phase 1は完了・凍結済み。#36/#34が#42 activationを待たせている間に、Stage10でユーザー目視負担をさらに減らせるかを、既存evaluator成果を中心に狭く検証する。

Primary restore anchors:
- `docs/project/ISSUE30_HANDOFF_20260910.md` — Phase 1
- `docs/project/ISSUE30_PHASE2_HANDOFF_20260910.md` — Phase 2
- `docs/project/ISSUE30_PHASE2_EXECUTION_SPEC_20260910.md` — Phase 2 base execution contract
- `docs/project/ISSUE30_PHASE2_WAVE2_EXECUTION_SPEC_20260910.md` — **current continuation contract**
- `docs/project/ISSUE30_PHASE2_CODEX_EXECUTION_PROMPT_20260910.md` — Codex restart/execution prompt
- `docs/project/ISSUE30_PHASE2_CHECKPOINT_TEMPLATE.md` — repository/DEV handoff format

Phase 1 evidence:
- screening-first design commit `87585424e8b5dfae19b6522e60306115641526ac`
- pilot/cache commit `8ff9ef142e6b7c25ae601589a82c136d96748991`
- minimal review result commit `5ea66ec69a7b9aeefde359997428ca5e243daf4b`
- 128 unique images / WD14-Kagami-CL each 128/128
- minimal review 19

Wave 1 accepted evidence:
- branch `codex/issue30-calibration-design`
- human review commit `233a2a25b58de388cdf4ccff1183fca0a3260472`
- P2-001: 2 seedとも `BOTH_FAIL`、device/body-site binding不成立
- P2-002: `A_ONLY_PASS` 1件 + contrast contaminationを伴う `BOTH_PASS` 1件
- P2-003: 2 seedとも `BOTH_PASS`、今回条件ではNegativeへの同一target追加による一貫した抑制なし
- relation/binding/body-siteは引き続き `HUMAN_REVIEW_ONLY`

## Frozen Phase 1 / Wave 1 policy

- Taggers are assistive triage, not Special semantic authority.
- direct / non-relation / simple unaryのみ補助AUTO候補。
- relation/binding / actor-object / body-site / quantity / spatial / insertion/contact/restraint / compound / component-only / disagreement / low-confidenceは原則HUMAN REVIEW。
- gray/unreadable/corrupt/hash/metadata/provenance欠損はsemantic評価前にBLOCKED。
- invalid target/contrastはexperiment-validity failureとしてevaluator failureから分離。
- Wave 1はstructural AUTO promotionの根拠にしない。

## Current continuation — Wave 2

Codexは `docs/project/ISSUE30_PHASE2_WAVE2_EXECUTION_SPEC_20260910.md` を現在の継続仕様として読む。

### Prerequisites before new generation

1. latest `origin/main` を取得する。
2. `origin/main` を `codex/issue30-calibration-design` へ **merge** する。rebase/force rewriteは禁止。Phase 1/Wave 1履歴を保持する。
3. review assetで、実際に使用したPositive/Negative Promptの関連tag/tokenを **`English (日本語)`** で表示する。`canonical_ja` だけの表示では不十分。
4. 日本語フォントは Meiryo → Yu Gothic → MS Gothic を優先し、日本語が□/tofuになるfallbackを有効なreview assetとして扱わない。
5. Wave 1画像は再生成せずcontact sheetだけ再生成し、日本語表示sanity checkを行う。selected fontとdisplay-check PASS/FAILを記録する。
6. review countは `review pairs` と `reviewed images` を別々に記録する。Wave 1では6 pairs = 12 images。
7. merge・表示修正後にPhase 2 focused tests / syntax / dry-runを再実行する。
8. `data/**`、#32 verdict、canonical、local-only images、無関係な未追跡ユーザーファイルを保持する。

前提が1つでもFAILなら新規生成前にSTOPする。

### Wave 2 priority questions

既存structural coverageとWave 1結果を再利用し、以下を優先する。

1. `EXACT_COUNT_RETENTION`
2. `CANONICAL_VS_ALIAS_OR_ALTERNATE_TRIGGER`
3. `MULTI_SPECIAL_RETENTION`

実在Special IDはcurrent canonical project dataからCodexが選ぶ。ユーザーに辞書手動探索を要求しない。

既存証拠で十分ならそのquestionはskipする。quota埋めは禁止。

### Wave 2 bound

- 最大 **12 new images**
- 各比較は2 predetermined fixed seedsから開始
- one experiment = one primary question
- A/B差分以外固定
- 追加seedへ自動進行しない
- mixed/unclearはDEV/ChatGPT reviewへ戻す
- multi-SpecialはcompatibleなA_ONLY/B_ONLY既存証拠を優先再利用する
- cleanなmulti-Special設計が合計12枚を超えるなら、上限を増やさずmulti-Specialをdeferする

### Review UX

ユーザーに見せるreview assetでは、少なくとも以下を英語原文＋日本語ラベルで併記する。
- target / contrast
- actor / count
- visibility / geometry / support
- 比較に関係するNegative Prompt tag/token

英語はcanonical/実行payload、日本語はdisplay-only。

ユーザー回答は原則 `A / B / both / neither / tie / unclear` に圧縮する。

## Default WAI17 lane

- Forge Neo
- WAI Illustrious v17
- Euler a
- Steps 25
- CFG 5
- 1024×1344 when appropriate
- fixed paired seeds
- Hires OFF / ADetailer OFF / LoRA OFF / ControlNet OFF / regional OFF / Forge Couple OFF

Prompt-only evidenceとassisted evidenceは分離する。

## Existing-tool-first

- Multi Prompt Slots
- built-in X/Y/Z
- Forge Neo Infinite Image Browsing
- Forge API
- existing Issue #30 runner
- WD14 / Kagami-24k / CL Tagger v2.00

新規extensionや大型automation platformは、具体的な不足と実益が証明されない限り導入しない。

## Decision labels

- ADOPT
- HOLD
- REJECT
- TARGETED_IMAGE_TEST_REQUIRED

## Hard prohibitions

- original 128-image pilotの全再実行禁止
- 2,788-image sweep禁止
- Stage10 production A/B禁止
- production `data/**`変更禁止
- #32 verdict / canonical変更禁止
- Tagger direct-matchをstructural Special truthへ昇格禁止
- relation/binding全面AUTO化を狙わない
- Phase 1/Wave 1 evidenceのmetric改善目的reinterpretation禁止
- model-family flattening禁止
- 大型独自automation platform禁止
- runtime LLM dependency禁止
- unnecessary extension installation禁止
- Wave 2の12-image cap超過禁止

## Wave 2 completion checkpoint

Codexは前提PASS後、Wave 2 design/manifestを作成し、planned new images <=12ならbounded Wave 2を実行してよい。

終了時にrepositoryから取得可能にする:
- merged main SHA
- Wave 2 candidate rationale
- selected questions / Special IDs
- test manifest
- exact Prompt / Negative
- runner/review-display changes
- tests / dry-run result
- generated/reused/blocked counts
- review-required pairs と reviewed images の別件数
- local-only artifact root
- contact sheet locator
- selected Japanese font
- Japanese display-check result
- remaining uncertainty

Wave 2終了後は追加seed・追加wave・Stage10へ自動進行せずSTOPする。

## Repository handoff

Codexはprivate Issue書込みを完了条件にしない。review可能なbranch/commit、実装/実行report、tests、protected-data確認、local-only artifact locatorをrepositoryへcommitし、可能ならremoteへpushする。

DEV/ChatGPTはその成果をGitHubから回収し、Issue #30へ `RESULT / EVIDENCE / DECISION / LIMITATION / NEXT` checkpointを記録する。

## Downstream

#42は依然として #36 V5 / #34 material UI/search workの完了または明示分離待ち。Phase 2はそのGateを迂回しない。

## Start / continuation Gate

Codexは作業開始前に必ず:
1. latest `main` を取得
2. Issue #30がPHASE2_ACTIVEであることを確認
3. `CURRENT_STATE.md` current core DEV = #30 Phase 2 を確認
4. 本ファイル Source Issue = #30 を確認
5. `ISSUE30_PHASE2_EXECUTION_SPEC_20260910.md` を確認
6. `ISSUE30_PHASE2_WAVE2_EXECUTION_SPEC_20260910.md` を確認
7. scope不一致ならSTOP

Current routing authority: `docs/project/CURRENT_STATE.md`.
