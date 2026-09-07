# Root Layout Reorganization Report

実施日: 2026-09-06

## 目的と境界

ルート直下を現在の開発・実行・Codex運用に必要なファイルへ限定し、設計資料、decision、Stage報告、過去handoffを用途別フォルダへ移動した。
データ、Special2788正本、実装意味、統計、仕様の意味、Git前提は変更していない。
削除は行っていない。移動前に `backups/root_layout_20260906_0105/` へ対象のコピーを作成した。

## 整理前 → 整理後

|整理前|整理後|区分|
|---|---|---|
|`IMPLEMENTATION_BASELINE.md`|`docs/architecture/IMPLEMENTATION_BASELINE.md`|architecture|
|`INDEX_ARCHITECTURE_DECISION.md`|`docs/architecture/INDEX_ARCHITECTURE_DECISION.md`|architecture|
|`RUNTIME_INDEX_DECISION.md`|`docs/architecture/RUNTIME_INDEX_DECISION.md`|architecture|
|`SEARCH_ENGINE_DECISION.md`|`docs/architecture/SEARCH_ENGINE_DECISION.md`|architecture|
|`TAG_KNOWLEDGE_CORE_DECISION.md`|`docs/architecture/TAG_KNOWLEDGE_CORE_DECISION.md`|architecture|
|`DATA_SOURCE_DECISION.md`|`docs/decisions/DATA_SOURCE_DECISION.md`|decision|
|`RECOMMENDATION_RANKING_DECISION.md`|`docs/decisions/RECOMMENDATION_RANKING_DECISION.md`|decision|
|`STAGE4_REVIEW_RESULTS.md`|`docs/stage_reports/STAGE4_REVIEW_RESULTS.md`|Stage report|
|`STAGE5_POST_AUDIT.md`|`docs/stage_reports/STAGE5_POST_AUDIT.md`|Stage report|
|`RECOMMENDATION_RANKING_EVALUATION.md`|`docs/stage_reports/RECOMMENDATION_RANKING_EVALUATION.md`|Stage report|
|`USER_RANKING_REVIEW.md`|`docs/stage_reports/USER_RANKING_REVIEW.md`|Stage report|
|`GENERATION_PROFILE_PHASE1_REPORT.md`|`docs/stage_reports/GENERATION_PROFILE_PHASE1_REPORT.md`|Stage report|
|`DanbooruTagTool_Stage3_GPT_Handoff.zip`|`docs/handoff_archive/DanbooruTagTool_Stage3_GPT_Handoff.zip`|past handoff|
|`DanbooruTagTool_Stage4_GPT_Handoff.zip`|`docs/handoff_archive/DanbooruTagTool_Stage4_GPT_Handoff.zip`|past handoff|
|`DanbooruTagTool_Stage5_GPT_Handoff.zip`|`docs/handoff_archive/DanbooruTagTool_Stage5_GPT_Handoff.zip`|past handoff|
|`CHATGPT_HANDOFF/`|`docs/handoff_archive/CHATGPT_HANDOFF_generation_profile_phase1/`|past handoff copy|
|`CHATGPT_HANDOFF.zip`|`docs/handoff_archive/CHATGPT_HANDOFF_generation_profile_phase1.zip`|past handoff ZIP|

移動前後に、上表のファイル16件と過去handoff内11ファイルのSHA-256を照合し一致した。
表中の一部文書は、移動後の参照pathだけを更新しているため、その更新後の内容は移動前バックアップと異なる。意味・データ・判断の変更はない。

## ルートに残したもの

- `AGENTS.md`: Codexのプロジェクト運用指示。
- `README_最初に読む.txt`: 初回利用者の入口。
- `FIRST_CODEX_REQUEST.txt`: READMEから参照される初回Codex指示。現在の運用入口なので保持。
- `FILE_HASHES.json`、`PACKAGE_MANIFEST.json`: source/packageの既存manifest。
- `pytest.ini`、`requirements-dev.txt`: test実行設定。
- `danbooru_tag_tool/`、`data/`、`tests/`、`tools/`、`backups/`: 実装、正本・派生物、test、運用tool、保全。
- 既存の `archive/`、`benchmarks/`、`references/`、`templates/`: 既存の役割を保つディレクトリ。
- `_handoff/`: 現在のChatGPT受け渡し専用。

## 更新した参照

- `AGENTS.md` と `docs/CHATGPT_CODEX_HANDOFF.md`: current handoffを `_handoff/CHATGPT_HANDOFF/`、ZIPを `_handoff/CHATGPT_HANDOFF.zip` に統一。
- `docs/CODEX_IMPLEMENTATION_SPEC_JA_v1.3.md`、`docs/FLOWCHARTS.md`、`FIRST_CODEX_REQUEST.txt`: Stage成果物の新relative path。
- `tools/build_user_ranking_review.py`、`tools/stage5_post_audit_report.py`、`tools/stage6_decision_audit.py`、`benchmarks/stage6/decision_audit.json`: reportの入出力・監査対象の新relative path。
- 移動したStage報告・decision文書内の関連参照: 新relative path。
- `FILE_HASHES.json`: path更新済みの `AGENTS.md` と `FIRST_CODEX_REQUEST.txt` のbytes/SHA-256のみ同期。

旧handoff絶対pathは、過去資料として退避した `docs/handoff_archive/` とbackupを除き、アクティブなプロジェクト内容から除去した。

## 検証

- 移動前backup: `backups/root_layout_20260906_0105/`（移動対象16ファイルと旧handoff一式）。
- 移動時SHA-256照合: 16ファイルおよび旧handoff内11ファイルが一致。
- root file inventory、active reference search、existing protected-source tests、全pytest、current handoff ZIPのmanifest照合を実施した。

最終pytest: **97 passed in 11.18s** (`-p no:cacheprovider`)。
current handoff ZIPは、manifestの列挙対象と `HANDOFF_MANIFEST.md` 自身がすべて含まれること、ZIP自身およびcache/build/仮想環境が含まれないことを照合した。

## 未解決事項

なし。archive内の過去handoffは作成時点の記録として保持し、current handoffとは混在させない。
