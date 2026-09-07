# Stage 4 — Unified Search Decision

## Query pipeline

Prompt-level input is split only on comma/newline, then each complete query is normalized by NFKC, lowercase, trim, underscore/space equivalence, and whitespace collapse.  One GUI-independent `TagSearchEngine` searches the Stage 3 `TagKnowledgeCore` for Japanese and English alike.

## Ranking and deduplication

Rank: canonical exact, alias exact, Japanese exact, Semantic exact, prefix, partial.  Within the same quality, Special results precede other results; no count or co-occurrence value is altered.  Results for one canonical are deduplicated while retaining every observed match type, provenance, Special ID, and semantic relation.  A literal/normalized canonical exact suppresses equal-key alias fallback, preserving canonical precedence.

## Ambiguity and Semantic

Ambiguous aliases yield every candidate; they are never silently resolved.  Semantic rows remain static bridge records.  A mapped row exposes its relation beside the real candidate canonical; an `UNMAPPED` row is returned without canonical, prompt text, category, or count.

## Stage 5 interface

`TagSearchEngine.search(text)` returns one result tuple per comma/newline input item; `search_one(text)` returns ranked `SearchResult` records.  Stage 5 may consume their canonical values only after excluding `None`; this search engine owns no post index or statistics.
