# Special2788 Generation Profile — Phase 1 実装報告

実施日: 2026-09-06 / C:\Codex\DanbooruTagTool

## 1. 変更した項目

- 任意のGeneration Profile CSV schema、型付きread-only metadata、loader、IDによるleft joinを実装。
- `TagKnowledgeCore.load_generation_profile(path)`で元Specialとmetadataの別viewを返す。
  `TagKnowledgeCore.load()`は従来通りで、sidecarを自動読み込みしない。
- 指定14件だけのfixtureを `data/generation/special2788_generation_profile.csv` に追加。
  既存IDを使用し、元Tagは照合値として完全一致を検証する。
- S/A/B/C、score、Needs、Confidenceは根拠不足のため全fixtureで空欄。
  roleはfixture設計案。3件の定性的観察はUSER_REPORTED、他11件はUNREVIEWED。
  独立監査済み/実測値としては扱わない。
- `PromptFormatter.format_special()`は元Special.termから出力し、統計canonicalに置換しない。
- このチェックアウトにはPromptSessionが未実装だったため、既存CoreTagSetを使う
  最小の `PromptSession.from_core()` / `export_prompt()` を新規追加。
  保存・復元は既存CoreTagSet JSONを使用する。profile無しでも全Specialを選択・出力できる。
- 統計identityは既存chosen_canonicalとして別途取得。
  未解決Special IDも公開し、部分的に解決したANDをCore全体のANDと扱わないよう仕様に明記。

## 2. 変更しなかった項目

- 元Special CSV全2,788行と全フィールド、XLSX、README、data/source、既存linkage、FILE_HASHES.json。
- Tag、日本語、Layer、主/関連カテゴリ、canonical_target、post_count、意味とPrompt identity。
- 既存の検索順位・canonical exact優先、統計runtime、Candidate Aggregation、ranking。
- Auxiliary role enum、既存CoreTagSet保存schema、既存pytest、UI。
- 全2,788件の自動評価・自動記入、Prompt自動展開、weight調整、region systemは実施していない。
- 内容カテゴリによるフィルタ・除外・減点・弱体化やその設定欄は追加していない。

元CSV SHA-256（作業前後一致、既存FILE_HASHES.jsonとも一致）:

```text
07584b365d5a68dbadd3f5e80859e768c2718b18746e32de02ce4b8bd60935e3
```

## 3. 新規作成ファイル

- `danbooru_tag_tool/generation_profile.py`
- `danbooru_tag_tool/prompt_session.py`
- `data/generation/special2788_generation_profile.csv`
- `docs/GENERATION_PROFILE_SCHEMA.md`
- `tests/test_generation_profile.py`
- `docs/stage_reports/GENERATION_PROFILE_PHASE1_REPORT.md`
- 下記バックアップ2ファイル。

既存変更ファイルは `danbooru_tag_tool/knowledge.py` と
`danbooru_tag_tool/prompt_formatter.py` の2件。

## 4. バックアップ先

`C:\Codex\DanbooruTagTool\backups\generation_profile_phase1_20260906\`

- `knowledge.py`（変更前）
- `prompt_formatter.py`（変更前）

正本は書き込み対象にせず、既存hash manifestと作業前後のSHA-256で不変性を確認した。
このディレクトリはGit repositoryとして認識されなかったため、commit/diffではなく
上記ファイルバックアップを取得した。

## 5. 実施したテスト

実行Python:
`C:\Users\takas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`

- 変更前: `-m pytest -q`
- 追加テストの初回検証: `-m pytest tests/test_generation_profile.py -q -p no:cacheprovider`
- 最終全回帰: `-m pytest -q -p no:cacheprovider`

追加24件の検証対象:

- 指定14件限定、ID/Tag一致、未評価値の保持、read-only。
- 全2,788件left join、元オブジェクト保持、各SpecialのPrompt exportと統計identity分離。
- 正本byte比較と既存manifestのhash照合。
- sidecar無し、存在しないpath、空overlay、未知profile IDでも全Special保持。
- 重複ID、既知IDのTag不一致、不正列/行幅、enum、不正boolean、NaN/Inf/範囲外数値の拒否。
- 未評価と0/falseの区別。
- 日英検索結果の不変性、profile無しAlias/SemanticのCore保存・復元・export。
- descensoredがPromptではdescensored、統計ではuncensoredとして保持されること。
- S/A/B/CとExpansionHintが出力や元Specialを変更しないこと。
- 小規模post-level fixture上で、profile対象タグとprofile無しAliasの
  base_count / Candidate Aggregationが読み込み前後で不変なこと。
- 既存73件の検索、統計、snapshot guard、ranking、正本保護等の全回帰。

## 6. テスト結果

- 変更前: **73 passed**（10.72秒）。pytest cache書き込みの権限警告が1件。
- 最終: **97 passed**（10.67秒）、失敗・skip・警告なし。
  cache pluginを無効化して、テスト内容を変えずに権限警告を回避した。
- 元CSVのSHA-256は作業前後一致。既存の全protected source hashテストも成功。

## 7. 未解決事項

Phase 1の実装・fixture validation上の未解決障害はなし。
以下は次の生成監査へ残す事項であり、今回評価済みとはしない。

- クラス・score・Needs・Confidenceの実評価、測定protocol。
- 実生成画像、seed、正確なcheckpoint、生成設定、試行数の根拠収集。
- 特定モデル・組合せごとのstandalone/coexistence評価。
- PromptSessionはCoreの最小経路のみ。UI接続、Auxiliary/LoRA composer、
  ExpansionHintの適用、region conditioningはこのPhaseの対象外。
- Semantic/ambiguousの統計未解決は従来通り。profileで架空mapping/countを付けない。

## 8. 次にChatGPTへ渡す情報

本報告、`docs/GENERATION_PROFILE_SCHEMA.md`、14件のsidecar CSV、追加pytestを渡す。
schema文書には共有された12項目のPrompt設計知見と根拠の限界を保持した。

ChatGPTの追加監査では、既存IDを維持し、単独認識と複数Special共存を別々に評価する。
物理整合性、主体、対象部位、器具、姿勢、カメラ、空間割当を記録し、
矛盾した配置の失敗を元タグの低評価へ転嫁しない。
辞書identityと辞書外secondary supportを分け、ExpansionHintは任意の追加設定に限定する。
性的・ニッチ・ハードさをクラスや順位の減点理由にしない。
追加精査完了までは全2,788件への自動展開を行わない。
