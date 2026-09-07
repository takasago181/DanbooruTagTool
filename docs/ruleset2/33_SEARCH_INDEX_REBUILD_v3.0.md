# Ruleset v2 Search Index Rebuild

`検索キー` is derived search data, not the human-readable Japanese glossary and not curated semantic ownership.

Deterministic components:
1. source `Tag`
2. underscore/space alternate form when applicable
3. current human-readable `日本語` gloss
4. `canonical_target` and its underscore/space alternate when present

Explicitly excluded:
- 主カテゴリ / 関連カテゴリ / 元カテゴリ
- 性別スコープ
- audit status / risk policy / severity

This prevents metadata migrations from polluting search terms while keeping source and canonical lexical forms retrievable.
