# Codex Prompt — Product-Fit Verdict Integration

あなたは DanbooruTagTool の本体実装担当です。

チャット履歴を正本にせず、実装開始前に必ず GitHub live 正本を確認してください。

確認順:
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. この実装を所有する live GitHub Issue 本文と最新comment
4. `audit/special2788-product-fit-20260912` の `docs/audit/SPECIAL2788_PRODUCT_FIT_IMPLEMENTATION_CONTRACT_20260912.md`
5. 同branchの `docs/audit/SPECIAL2788_PRODUCT_FIT_VERDICT_MANIFEST_20260912.json`
6. 必要な既存 Special runtime/search/browse/recommendation 実装

重要:
- Codex自身が2,788件を再分類しない。
- manifestのID集合をそのまま実装入力にする。
- Special ID / canonical identity / Alias relation / provenance / layerは変更しない。
- 年齢、性的強度、非合意、R18G、ニッチ/過激さを理由に独自のfilterを追加しない。
- #34 の fuzzy/substring ranking 修正はこのIssueでは行わない。
- Stage10 A/Bは開始しない。

実装要求:
- manifestから `data/special2788/product_fit_verdicts.csv` を決定論的に生成する。
- 2,788行、ID 1..2788 contiguous、重複0、verdict件数 `1618 / 1133 / 12 / 25` を自動検証する。
- verdictをSpecial ID keyed sidecarとしてruntimeで取得できるようにする。
- product-facing eligibilityを中央化し、UI/search/browse/recommendation各所へ同じ判定を重複実装しない。
- `KEEP` = 通常候補。
- `KEEP_REFERENCE_ONLY` = 検索/参照/Alias資産として保持し、独立default候補としては前面に出さない。
- `OUT_OF_SCOPE_PRODUCT` = source/historyは残すが通常product-facing候補から除外。
- `REVIEW` = 参照可能だがresolved normal recommendationへ自動昇格させない。
- reference-onlyのexact/alias lookupが壊れないことをテストする。
- canonical production dictionaryが変更されていないことを確認する。

作業は最新mainから専用feature branchを作成し、テスト・実装レポートとともにcommit/pushしてください。

完了報告には最低限:
- branch / commit SHA
- changed files
- generated CSV validation counts
- tests実行結果
- product-facing挙動の変更点
- protected/canonical data未変更確認
- 未解決事項
を含めてください。

実装後はmergeせず、DEV/AUDITへ返してください。
