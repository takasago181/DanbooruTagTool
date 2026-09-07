# FEATURE_PRIORITY.md

## MUST — v1の存在理由

1. Special2788を主役として選べる
2. 複数SpecialをCore Tag Setとして扱える
3. 日本語/英語/混在検索
4. canonical/alias安全解決
5. true multi-tag AND
6. Candidate Aggregation
7. raw co-occurrence counts/rates
8. runtime snapshot整合性
9. reliability-aware recommendation
10. 必要時のみAll Danbooruへ拡張
11. Core / Auxiliary / LoRAを分離
12. Prompt出力
13. pytest継続
14. Forge同時利用を意識したRAM

## SHOULD — v1内で余力があれば

- Core Set保存/呼出
- role別Auxiliary表示
- Semantic Bridgeの有用mapping拡充
- UIで統計snapshot/current count snapshotを確認可能
- 小規模manual generic noise list

## LATER

- 全124,016タグの完全role分類
- advanced fuzzy
- LoRA folder crawler
- incremental index update
- Core Set version history
- nested templates
- cloud sync
- plugin manager
- automatic AI prompt rewrite
