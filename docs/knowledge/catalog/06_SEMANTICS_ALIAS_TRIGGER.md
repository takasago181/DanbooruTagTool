# 06 — Semantics / Alias / Trigger

## 5つの別レイヤー

1. **Danbooru canonical identity**
2. **Alias/history**
3. **Implication/hierarchy**
4. **UI日本語表示・検索語**
5. **model trigger surface / generation support**

これらを相互に勝手に上書きしない。

## Danbooru

現在のDanbooru Wiki + active Alias/ImplicationがDanbooru意味の最優先。

- Alias = identity mapping
- Implication = hierarchy/包含関係
- related/co-occurrence = synonymではない
- `Tag what you see` 原則はvisual semanticの重要背景

## e621

Danbooru canonicalを置き換えないsecondary source。

特にNoobAIで有用:
- nonhuman/anatomy/fetish vocabulary
- alternate trigger仮説
- training-surface history
- relation/topology decomposition

現在のe621表記が学習cutoff時点でも存在したとは限らないためhistory確認が必要。

## Gelbooru / Anima

AnimaにはGelbooru formを優先するauthor guidanceがあるため、Danbooru canonicalとは別に**model trigger候補**として保持する。

canonicalを書き換えず、exact-model alternate surfaceとしてテストする。

## trigger drift

タグrename/alias変更後:
- 現canonical
- historical alias
- training-time surface
- model-specific trigger
が分離する可能性がある。

そのため「canonicalで出ない = concept未学習」と即断しない。

## UI-JAとの境界

日本語表示/検索語はcanonical意味を表現するレイヤーであり、意味の再定義権限を持たない。

翻訳scope mismatchはまずtranslation REVIEW。独立canonical evidenceと構造意味が同時成立不能な時だけ本当のCONTRADICTION候補。

## 原本

- `research/DANBOORU_WIKI_SEMANTIC_AUDIT_20260909.md`
- `research/E621_WIKI_SEMANTIC_TRIGGER_AUDIT_20260909.md`
- `research/HF_MODEL_DISCUSSIONS_AUDIT_20260909.md`
- `research/SOURCE_AUTHORITY_MATRIX_20260909.md`
- Issue #38 KNOWLEDGE response
- `docs/ruleset2/39_ALIAS_TWO_AXIS_POLICY_v3.0.md`