# Stage 3 — Tag Knowledge Core

実装日: 2026-09-05。Stage 3だけを実装。既存ファイルは変更せず、新規Python packageとpytestを追加した。

## Implemented model

`danbooru_tag_tool/models.py` のfrozen/slots dataclassでCanonicalTag、SpecialTag、Translation、SemanticCandidate、CoreTagSet、AuxiliaryTag、LoRA、PromptTagを分離した。GUI・外部依存なし。CanonicalTagは辞書由来のcurrent_post_countだけを持ち、runtime統計値を持たない。PromptTagはPromptFormatter.format_tagで生成する。

CSVを行単位で読み、必要な静的タグモデルとlookup索引だけを保持する。TRIAL巨大JSONは使用しない。このメモリ上の静的知識構造はproduction DB/index formatの決定ではなく、post indexや性能評価を含まない。

## Normalization / alias behavior

NFKC → lowercase → trim → underscoreをlookup用spaceへ変換 → whitespace collapse・端の空白除去。comma/newlineだけをPrompt入力の区切りにする。canonicalの原文は保持し、Prompt表示へのspace化はPromptFormatterだけが行う。

exact解決順はcanonical → alias → Japanese → semantic。literal canonicalは自身を優先し、正規化で複数canonicalが衝突した場合は候補を保持する。prefix/partial/fuzzyは未実装。

監査元alias索引は34,417キー、曖昧44件、canonical優先衝突140件。lookup正規化では ` nagatoro`（ijiranaide_nagatoro-san）と `nagatoro`（nagatoro_hayase）が統合されるため、実行時lookupは34,416キー、複数候補45件になる。候補をunionし、silent resolveしない。元CSVは変更していない。この差は回帰テストで固定した。

canonical名自体にセミコロンがあるため、単一alias候補はTargetCountを見て分割しない。現在の複数候補フィールドは監査CSVのセミコロン区切りを使用し、全候補の存在を検証する。

## Special / translation

正本Special CSVとverified linkageをIDで結合し、元の全列が一致することと全canonical参照・match typeを検証する。2,788件の独立したSpecialTagを保持し、2,443件のchosen canonical、未解決9件、Semantic336件を維持する。curatedな2件の選択はそのSpecial IDに限定され、一般aliasの曖昧さを上書きしない。

Specialの日本語・説明は正本のまま保持。Translationはcanonical、日本語、source、status、updated_atを独立管理でき、任意の明示的なTranslation列をTagKnowledgeCoreへ渡せる。trial seedの自動読込・統合や676件の翻訳修正はしない。

## Semantic

全336行をloadし、厳密な列、unique semantic_id、Special参照、relation/review enum、候補canonical存在、UNMAPPEDと空候補の整合性を検証する。count列は受け入れない。複数candidateは別semantic_idの別行で、同じspecial_idに紐付け可能。

semantic lookupはreview状態を含む行への参照を返すだけで、自動canonical解決しない。UNREVIEWED/REJECTEDも監査用に保持する。後続側でレビュー状態と候補を確認して扱う。mapping作成はStage 8に留保する。

## Core Tag Set

v1の5項目のみ。少なくとも1件のSpecial ID、ID/name、ISO-8601日時を検証。重複IDは拒否する。TagKnowledgeCore.create_core_set、CoreTagSet.validate、JSON入出力時にSpecial IDの存在を検証する。直接dataclassを作成する場合は構造検証のみなので、利用前にvalidateが必要。Semantic/曖昧Specialも核として保存できるが、canonicalへ捏造変換しない。

AuxiliaryTagはCanonicalTagとrole（既定other）、LoRAはname/weight/triggerの型境界のみ。CoreへAll Danbooruを昇格するAPIや推薦・LoRA出力機能はない。

## Stage 4へ渡すinterface / intentional omissions

- `TagKnowledgeCore.load(root, translations=())`: 正本・監査済みCSVの読込。
- `canonical`, `aliases`, `special`, `semantic`, `translations`: 静的モデル。
- `resolve_exact(text)`: match_type、canonical_candidates、special_ids、semantic_ids。resolved_canonicalは一意解決できる場合のみ。Semantic候補は自動解決しない。
- `create_core_set(**fields)` / `CoreTagSet.to_json(special_ids)` / `from_json(text, special_ids)`。
- `normalize_lookup`, `split_prompt_input`, `PromptFormatter.format_tag`。

Stage 4 Unified Search、UI、ranking、statistics、全post index、Candidate Aggregation runtime、全翻訳・全role分類、Prompt Builder完成、LoRA機能は実装していない。Approved Source・双方向index決定は変更しない。packed binary/mmap/full RAM/Forge同居評価はStage 5の残課題。

## Validation

Stage 3の関連pytestを実装中に実行し23件PASS。その後、正規化衝突と入力hashの回帰テスト2件を追加した。

最終full pytest: **37 passed in 1.45s**（Stage 3の25件を含む）。実行コマンド:

```powershell
& 'C:\Users\takas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest -p no:cacheprovider -q
```

初回関連テストで既存 `.pytest_cache` の書込権限警告が出たため、最終実行ではcache pluginを無効化した。テストの除外はしていない。最終実行は警告なし。

バックアップ: 既存ファイルを変更・上書きしていないため作成なし。正本hashは既存Stage 0テストで、Stage 3が使用する派生CSV・Semanticおよび676件review候補は追加hashテストで不変を確認した。

## Stage 4開始前の小修正（2026-09-05）

Stage 3の設計・入力データ・snapshot invariantは変更していない。`TagKnowledgeCore` 初期化時に `special_id -> semantic_ids` lookupを構築し、日本語exact解決でSemantic全行を走査しないようにした。Translationは空canonical、空Japanese、不明canonical、不正statusを拒否する。許可statusは既存trial seedの `UNREVIEWED_TRIAL` と `UNREVIEWED`、`REVIEWED`、`REJECTED`。

追加pytestを含む最終full pytest: **44 passed in 1.88s**。Stage 4には進んでいない。
