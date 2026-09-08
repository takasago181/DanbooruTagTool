# STAGE 10 PREP

## 目的

Special2788の機能を実画像A/B比較で検証する。

## 現時点の重要原則

- 普段の「良い画像を作るPrompt」とテストPromptを分ける。
- 1実験につき原則1疑問。
- 比較対象以外の条件を固定する。
- Special成立の有無を画像から判定しやすくする。
- model family差を保持する。
- Promptの実出力を追跡可能にする。
- Stage10専用の採点・実験管理機能を現時点で本体へ追加しない。
- Stage9 overall Gate完了だけでStage10本番A/B開始とはしない。
- Issue #28 automated E2E functional testはPASS済み。
- Stage10比較自動化はexternal / existing tool first。不足箇所だけ薄いglue/harnessを追加する。
- WD14その他TaggerをSpecial2788の完全なground truthとして扱わない。
- unsupported / low-confidenceはFAILではなくREVIEWへ送る。
- simple tag用の1つのconfidence/margin thresholdをrelation/composite/rare Specialや別model familyへ共通適用しない。

## Issue #6 comparison environment completion

Issue #6: **PASS_WITH_NOTE / completed**。

- Multi Prompt Slots fixed SHA: `b3f45b17e5a24a20b4fa04edac74e6a4fec23dfe`
- Forge Neo Infinite Image Browsing fixed SHA: `ced039479c2e1463c9bdb136d355e01b3dfc9279`
- fixed-seed A/B (Seed 5072): PASS
- generated-image Prompt/PNG metadata traceability: PASS
- existing baseline regular-generation regression: PASS
- audit commit: `472a219058771fe117b87d62c9d53d5402b8cff9`
- evidence: `docs/testing/ISSUE6_COMPLETION_CHECKPOINT_20260908.md`, `docs/testing/ISSUE6_EXTENSION_INSTALL_AND_VERIFICATION_20260908.md`, `docs/testing/ISSUE6_EXTENSION_AUDIT_20260908.md`

## Issue #30 infrastructure pipeline checkpoint

Issue #30 external-tool-first配管: **PASS_PIPELINE**。

- evidence branch: `codex/issue30-automation-dry-run-20260908`
- evidence commit: `f2fc7acb15f996630c9f008284d80cf3261fb32f`
- Forge Neo API `neo-2.29`
- fixed model `waiIllustriousSDXL_v170` / hash `f116b0c78f`
- Seed 5072 / Steps 24 / CFG 4.5 / Euler a / Automatic / 1024x1024 / batch 1 / LoRA none
- `/sdapi/v1/txt2img` → PNG SHA-256 → `/sdapi/v1/png-info` actual Prompt/metadata → WD14 raw confidenceまで通過
- user manual operations: 0
- Agent Scheduler: HOLD
- model switch / production scoring / production A_WIN・B_WIN判定: 未実施

## Generic golden-set disposition

Generic golden set evidence:
- commit `33215269cfeb33b3afab0c36a6a8bd52cb55952e`
- targets: `standing / sitting / long_hair / smile`
- 4 experiments × 2 seeds = 8 A/B / 16 images
- metadata 16/16 / WD14 raw 16/16 / selected target vocabulary coverage 100%

Issue #37 KNOWLEDGE + PROMPT review conclusion:

**`REPLACE_OR_AUGMENT_WITH_SPECIAL_REPRESENTATIVE_SET`**

The generic set is retained only as a **plumbing/evaluator fixture**. It is not representative enough for DanbooruTagTool's Special2788-centered Stage10 product-purpose calibration.

The generic contact-sheet task is therefore **PAUSED / SUPERSEDED as the next product-representative step**. Existing evidence is preserved.

## Special-representative test design — adopted direction

Design authority:
- `docs/testing/ISSUE30_SPECIAL_REPRESENTATIVE_ROUTING_DESIGN_20260908.md`
- Issue #37 joint checkpoint

Representative calibration must include categories such as:

1. actual Special2788 direct presence/absence
2. rare / niche Special
3. relation / actor-target / body-site binding
4. multiple-Special simultaneous retention
5. support-tag ON/OFF affecting observability/visibility while Special identity stays fixed
6. canonical/Alias identity-sensitive behavior where relevant

Each pair still follows **one experiment = one question**.

Routing classes are capability-aware. Unsupported/insufficient evidence -> `REVIEW`; required metadata/traceability/infrastructure missing -> `BLOCKED`. Only validated compatible evaluator classes may emit candidate `A_WIN / B_WIN`.

## Negative Prompt boundary

For unusual-anatomy Special tests, do not mechanically fix anatomy-sensitive negatives such as:

- `bad anatomy`
- `extra limbs`
- `extra arms`
- similar malformed-anatomy suppression

Their interaction with the target Special is a separate one-question A/B experiment. This is experiment isolation, not a production Negative Prompt rule.

## HOLD until final Special2788 dictionary freeze

Do not finalize before the dictionary is frozen:

- representative test Special IDs / exact final case list
- WD14 / Kagami-24k / CL Tagger v2 final responsibility split
- each Tagger's final Special2788 coverage
- per-Special `AUTO` / `REVIEW` final routing
- production confidence / margin thresholds

PROMPT may prepare Prompt structures, A/B questions, support-isolation patterns, and replacement workflow now, but case selection is not final.

## Required KNOWLEDGE evaluator follow-up after dictionary freeze

Compare the finalized 2,788-entry Special set against:

- WD14 / `wd-eva02-large-tagger-v3`
- Kagami-24k
- CL Tagger v2 stable/fixed release

Return coverage to PROMPT and Issue #30 before final evaluator allocation.

At minimum report:
- raw vocabulary coverage
- Core / Extended / Alias / Semantic coverage separately
- post-count-band coverage
- raw Alias coverage and canonical-target coverage separately
- representative-image evaluator disagreement when available

## Stage9 → Stage10 Gate

Stage9 completed:
- Stage9A PASS
- Stage9B PASS / Issue #3 PASS
- Stage9C PASS
- Stage9D PASS
- Issue #17 completed
- Issue #22 independent audit PASS
- PR #27 merged / merge `0f17d65e1e3c737dfacd9cfee0c9d4062b683ade`
- Issue #26 protected integrity completed

Comparison boundary remains `ComposerVariant` and `Stage9ComposerSession.comparison_snapshot()`; Stage9 does not finalize result scoring/winner selection or model grammar.

## Automated E2E Gate

Issue #28: **PASS / completed**。

- evidence head `04629908b38c29e3896eeca3c1fb64cf164c7142`
- PR #33 merged / merge `9504fd64ce6b4acc762f589a734d67eac6b79e93`
- full suite 285 passed / exit 0
- real Tk 8.6.15 / required scenarios 3/3 PASS / no mocked rendering
- Stage0 protected hash/size/path-set checks PASS

E2E does not prove visual layout/manual inspection, exhaustive 2,788 Special behavior, Forge simultaneous performance, or image quality.

## Stage10開始前チェック

- [x] Stage9B完了（Issue #2）
- [x] Stage9B監査PASS（Issue #3）
- [x] Stage9C/9D処理・監査PASS（Issue #17 / #22）
- [x] Stage9 overall Gate完了
- [x] Automated E2E functional test PASS（Issue #28）
- [ ] Stage10正式handoff
- [x] Forge Neo比較環境導入・動作確認（Issue #6） — PASS_WITH_NOTE
- [ ] Forge Neo A/B automation external-tool-first（Issue #30）
  - [x] Forge API → fixed-seed A/B → PNG actual metadata → WD14 raw — PASS_PIPELINE
  - [x] generic golden set — accepted as plumbing fixture only
  - [x] Special-representative test/routing direction — adopted via Issue #37
  - [ ] final dictionary freeze後のTagger coverage比較
  - [ ] final representative case selection
  - [ ] capability-aware AUTO/REVIEW routing calibration
- [x] Multi Prompt Slots等の比較手段確認（Issue #6）
- [ ] テストPrompt班へ正式Specialデータ提供（Issue #5）
- [ ] A/Bの固定条件最終定義
- [x] metadata保存方法定義（Issue #6 baseline / handoff）
- [x] #4 KNOWLEDGEのStage10知識整理結果を正式handoffへ反映
- [ ] model familyごとのPrompt grammar差を保持し未検証共通化していない
- [x] 実Prompt traceability baseline確認
- [ ] REVIEW対象だけを人間が効率よく確認できる最終運用を代表Specialセットで確認

Knowledge handoff正本: `docs/stages/STAGE_10_KNOWLEDGE_HANDOFF.md`

## 現在地

Stage10本番A/Bは**未開始**。

Issue #30はインフラ配管PASS。generic golden setはplumbing fixtureに降格・保持。Special代表テスト方式とrouting思想は#37で修正済み。最終Specialデータ・Tagger割当・AUTO/REVIEW mapping・production thresholdは、辞書freeze後のKNOWLEDGE coverage比較までHOLD。

このchecklistを満たす前にStage10本番画像A/Bを正式開始しない。
