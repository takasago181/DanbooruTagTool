# Codex Execution Prompt — Issue #30 Phase 2

あなたは DanbooruTagTool の Issue #30 Phase 2 実行担当です。

今回の担当は「設計を自由に作り直すこと」ではありません。ChatGPT/DEV側で確定した Phase 2 実行仕様に従い、既存成果物の分析、test manifest作成、必要最小限のrunner改修、preflight / dry-run、許可範囲内の実画像生成、evaluator処理、review asset作成、GitHub上で取得可能な成果物作成を実行してください。

## Restore order

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #30 latest body/comments
4. `docs/project/CURRENT_DEV_TASK.md`
5. `docs/project/ISSUE30_HANDOFF_20260910.md`
6. `docs/project/ISSUE30_PHASE2_HANDOFF_20260910.md`
7. `docs/project/ISSUE30_PHASE2_EXECUTION_SPEC_20260910.md`
8. Phase 1 related artifacts under `docs/testing/`
9. necessary KNOWLEDGE / PROMPT references

最重要の実行仕様は `docs/project/ISSUE30_PHASE2_EXECUTION_SPEC_20260910.md`。

Chat history is not canonical.

## Start Gate

作業開始前に必ず:
- latest `main` を取得
- Issue #30 が `PHASE2_ACTIVE` であることを確認
- `CURRENT_STATE.md` current core DEV = Issue #30 Phase 2 を確認
- `CURRENT_DEV_TASK.md` Source Issue = #30 を確認
- execution specを確認
- scope不一致ならSTOP

## First task

既存128-image Phase 1 pilotを再実行せず、既存証拠を structural capability 単位で整理する。

Structural classes:
- `UNARY_OBJECT_OR_STATE`
- `BODY_SITE_STATE`
- `SIMPLE_RELATION`
- `BINDING_RELATION`
- `RESTRAINT_TOPOLOGY`
- `DEVICE_RELATION`
- `MULTI_OBJECT_OR_COUNT`
- `NONHUMAN_APPENDAGE_RELATION`
- `ANATOMY_CHANGING`
- `COMPOSITE_HARD`

既存128枚について、検証済み範囲、人間レビュー証拠、evaluator-only evidence、PASS/FAIL/UNRESOLVED、追加画像の必要性、追加テストの期待価値を整理する。

Required outputs:
- `docs/testing/ISSUE30_PHASE2_STRUCTURAL_COVERAGE.md`
- `docs/testing/ISSUE30_PHASE2_STRUCTURAL_COVERAGE.json`

## New test selection

coverage確認後、新しい実画像が必要な primary question を最大5〜6個程度選ぶ。

「面白そうなタグ」ではなく「未検証または証拠が弱い生成能力」を選ぶ。

候補例:
- device / functional contact
- source / ownership
- exact count
- simultaneous multi-Special retention
- anatomy-changing × Negative collision
- canonical vs Alias / alternate trigger

既存128枚で十分なら新規生成しない。Specialは現在の正式データから実在IDを選択し、架空tagは禁止。

## First wave

原則:
- 5〜6 experimental questions
- 各比較は2 predetermined fixed seeds開始
- 新規生成を必要最小限にする

結果が明瞭なら終了。結果が割れた場合のみseed 3、さらにproduct decisionへ影響する場合だけseed 4を検討する。追加seed・追加実験へ自動進行しない。

## Baseline

- Forge Neo
- WAI Illustrious v17
- Euler a
- Steps 25
- CFG 5
- 1024×1344 when appropriate
- fixed paired seeds
- Hires OFF
- ADetailer OFF
- LoRA OFF
- ControlNet / regional OFF
- Forge Couple OFF

1 experiment = 1 primary question。A/B差分以外を固定する。

## Runner

`tools/issue30_calibration_pilot.py` を優先再利用する。

許可する薄い一般化:
- fixed 32-case制約除去
- external manifest対応
- variable case count
- cache reuse
- fixed-seed paired generation
- metadata/hash preservation
- review/contact sheet出力
- result summary出力

既存のForge複数起動防止、checkpoint確認、cache再利用、generation failure時STOP等の安全機構を維持する。

新runnerをゼロから作り直さない。大型GUI/dashboard/automation platformを作らない。

## Existing tools first

現在利用可能:
- Multi Prompt Slots
- built-in X/Y/Z
- Forge Neo Infinite Image Browsing
- Forge API
- existing Issue #30 runner
- WD14
- Kagami-24k
- CL Tagger v2.00

具体的な不足が証明されない限り新拡張を導入しない。Agent Scheduler等はHOLD。

## Evaluation boundary

Use:
- `A_ONLY_PASS`
- `B_ONLY_PASS`
- `BOTH_PASS`
- `BOTH_FAIL`
- `TIE`
- `UNCLEAR`
- `BLOCKED`

Taggers are assistive triage only. relation/binding/body-site/count/topologyの最終semantic truthをTaggerだけで判定しない。machine disagreementはreview候補。evaluator vocabulary不足をmodel generation failure扱いしない。

Artifact failureとexperiment-validity failureをsemantic evaluator failureから分離する。

## User burden

ユーザーへCSV編集やraw log確認を要求しない。

必要なreview assetは:
- numbered contact sheet
- A/B label
- 日本語の確認内容
- one primary question per comparison

ユーザー回答が `A / B / both / neither / tie / unclear` 程度で済む形を優先する。

## Hard prohibitions

- original 128-image pilot全再実行禁止
- 2,788-image sweep禁止
- Stage10 production A/B禁止
- production `data/**`変更禁止
- #32 verdict / canonical変更禁止
- Phase 1 evidence reinterpretation禁止
- relation/binding全面AUTO化禁止
- model-family flattening禁止
- runtime LLM dependency禁止
- unnecessary extension installation禁止

## Repository handoff

Per `PERMANENT_RULES.md`, private Issue書込みはCodexの完了条件ではない。

Codexはreview可能なbranch/commit、実装レポート、tests、protected-data確認、local-only artifact locatorをrepositoryへcommitし、remoteへpushする。

Repository report format:
- RESULT
- EVIDENCE
- DECISION
- LIMITATION
- NEXT

DEV/ChatGPTがGitHubから取得してIssue #30へcheckpointを記録する。

## First stopping point

以下まで実行する:
1. structural coverage
2. 新規テスト候補最大5〜6問
3. selected Special IDs
4. test manifest
5. expected image count / expected user-review count
6. minimal runner change
7. dry-run / tests
8. bounded first waveが仕様条件を満たす場合のみ、その第一波を実行
9. review assets / report作成
10. branch/commitをremote push
11. STOP

第一波終了後、追加テストやStage10へ自動進行しない。

最終reportには最低限:
- branch
- commit SHA
- changed files
- tests
- new generated image count
- reused image count
- blocked count
- review-required count
- local-only artifact root
- remaining uncertainty

を含める。
