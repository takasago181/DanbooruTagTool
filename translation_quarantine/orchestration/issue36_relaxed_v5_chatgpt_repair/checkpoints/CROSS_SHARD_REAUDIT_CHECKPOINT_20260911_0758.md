# Issue #36 V5 Cross-Shard Re-audit Checkpoint — 2026-09-11 07:58Z

Branch: `ui-ja/issue36-relaxed-v5-chatgpt-repair`

## Current state

- Source rows: 30,629 / 30,629 reviewed
- Source shards: 31 / 31 complete
- V5 override rows: 10,559
- Materialized applied overrides: 10,559 / 10,559
- Production modified: NO
- Status: `SOURCE_REVIEW_COMPLETE_CROSS_SHARD_REAUDIT_IN_PROGRESS`

## Deterministic validation

Latest materialization report: PASS

- canonical uniqueness: PASS
- canonical identity preserved: PASS
- canonical order preserved: PASS
- non-display columns preserved: PASS
- `display_ja` nonempty: PASS
- V4 `old_display_ja` match: PASS
- duplicate override canonicals: 0

Latest language sanity: PASS

- HANGUL: 0
- RAW_ENGLISH_WRAPPER: 0
- CONTROL_CHAR: 0
- ASCII candidates: 1,635
- ASCII-only: 616
- ASCII-mixed: 1,019
- priority `ASCII_SUSPICIOUS`: 458

`ASCII_SUSPICIOUS` is a review queue, not a defect count. Proper names, acronyms, brands, model identifiers and legitimate mixed Japanese/Latin labels are expected to remain.

## Important repair to the V5 materialization route

During resumed cross-shard review, a fail-open gap was found between the scanner and materializer: the scanner treated all override CSVs as reviewed, while `materialize_v5.py` only applied `audit_shard_*.csv`. This meant newly-created `cross_shard_*.csv` could be marked as already overridden without changing the materialized table.

Fixed in commit `4ed144de9e5866bb81b621c14c9922a0a8e1966e` by explicitly materializing both namespaces through the same fail-closed validation path:

- `audit_shard_*.csv`
- `cross_shard_*.csv`

All subsequent cross-shard batches update the override CSV and `progress.json` atomically, then require deterministic materialization PASS before continuing.

## Cross-shard repair policy used

Continue to repair only clear defects. Do **not** chase ASCII count to zero.

Examples of accepted corrections:
- machine-composed Japanese/English seams (`アルファベット・blocks` -> `アルファベット積み木`)
- scope-loss (`SFWイラスト` for `negative_space_oral_(meme)` -> meaning-preserving composition label)
- exact official/source Japanese where established (`eye_of_senri` -> `闡裡の瞳（連縁）`, `Raizen High School` -> `来禅高校`)
- exact-definition repairs (`tan_tattoo` -> `タトゥー状の日焼け跡`)
- explicit ambiguity preservation (`hair_branch` -> `hair branch（曖昧タグ）`) instead of guessing

Proper names/codes/acronyms may remain in Latin script when that is the clearest UI label.

## Boundaries

- no production `data/**` write
- no canonical English identity rewrite
- no search-ranking change (#34 remains separate)
- no #32 verdict/generation metadata change
- no #35 / `CURRENT_DEV_TASK.md` change
- no Stage10 production A/B
- no production-promotion authorization inferred from this checkpoint

Next: continue bounded evidence-backed review of the remaining `ASCII_SUSPICIOUS` queue; leave valid Latin-script labels untouched and leave ambiguous semantics explicit/fail-closed.
