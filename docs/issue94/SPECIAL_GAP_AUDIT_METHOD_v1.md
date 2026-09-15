# Issue #94 Special Gap Audit — Method v1

Status: **IN PROGRESS / PARTIAL CHECKPOINT / NO PRODUCTION MUTATION**

Branch base main: `05078dde8bf7964f18d2c0accfcdb66075601664`

## Purpose

Audit the current Danbooru canonical vocabulary against accepted Special 2,788 and identify **true Special expansion candidates** without changing production data during Phase 1.

This audit is content-neutral. Adult/explicit/fetish/BDSM/body-fluid/gore/taboo content is **not** a reason to exclude, downgrade, or suppress a candidate. Candidate decisions are based on identity coverage, semantic overlap, product usefulness, and duplication only.

## Source baseline

Danbooru snapshot: `2026-09-02`

- canonical rows: 124,016
- General: 30,743
- Artist: 48,313
- Character: 35,890
- Copyright: 8,536
- Meta: 534
- source SHA-256: `9b32d5ac0713ab252e7470ba6af9cb34de56878b6b3b13dfbbf6a4a37d82d95b`

Accepted Special baseline:

- total: 2,788
- Core: 759
- Extended: 915
- Alias: 778
- Semantic: 336
- source identity SHA-256: `07584b365d5a68dbadd3f5e80859e768c2718b18746e32de02ce4b8bd60935e3`

The historical full-KB `Special2788=YES/blank` column is **not authoritative enough by itself** for gap detection. It misses some identity relationships that are reachable through normalization or alias/canonical closure.

## Deterministic source modes

`scripts/issue94/special_gap_audit.py` supports two Danbooru source modes. They share the same downstream identity-classification logic.

### A. Full-KB mode

Use the verified derived full knowledge base directly:

- `--full-kb <danbooru_full_tag_knowledge_base_...csv>`
- `--special <illustrious_tag_knowledge_base_2788.csv>` or the tracked profile fallback described below
- optional `--alias-map <danbooru_alias_map_34630.csv>`

This mode preserves the historical `Special2788` marker only as a diagnostic field. The marker is never authoritative for identity coverage.

### B. Protected canonical-source mode

When the derived full-KB file is not available in the active checkout, use the protected source-of-truth inputs already present in the local repository:

- `--canonical-source data/source/danbooru-2026-09-02.csv`
- `--alias-index data/derived/danbooru_alias_normalized_index_VERIFIED_34417.csv`
- `--special <illustrious_tag_knowledge_base_2788.csv>` or the tracked profile fallback described below

The canonical source is the same 124,016-row snapshot identified by SHA-256 `9b32d5ac0713ab252e7470ba6af9cb34de56878b6b3b13dfbbf6a4a37d82d95b`.

In this mode the scanner reconstructs alias closure from the verified normalized alias index and admits **only uniquely resolved aliases**. `AMBIGUOUS_ALIAS` entries are not silently assigned to a canonical. Canonical-precedence aliases are also excluded from alias closure because the canonical identity wins by definition.

The historical full-KB `Special2788` marker is unavailable in this mode, so `legacy_blank_but_identity_covered` is reported as `null`. This does **not** affect `PRESENT_EXACT`, `PRESENT_CANONICAL_TARGET`, `PRESENT_ALIAS_CLOSURE`, `SEMANTIC_EXACT_OVERLAP_ONLY`, or `GENERAL_ONLY_GAP` classification.

The full scan remains fail-closed on `General == 30,743` and `Special == 2,788` unless explicit test-only expected counts are supplied.

## Deterministic Special input modes

The scanner now also supports two Special source modes.

### S1. Protected Special source

Preferred when the original accepted Special CSV is available locally:

- `--special <illustrious_tag_knowledge_base_2788.csv>`

Required columns are `ID`, `Tag`, `Danbooru種別`, and `canonical_target`. This is the direct historical path.

### S2. Tracked Generation Profile fallback

When the protected Special source is not mounted in the active execution environment, use the tracked 2,788-row generation profile:

- `--special-profile data/generation/special2788_generation_profile.csv`

This is **not** a looser heuristic replacement. It is a fail-closed reconstruction path:

1. `SpecialID` + `Tag` provide all 2,788 accepted identities.
2. Semantic rows are recognized only through approved tracked semantic markers (`APPROVED_SEMANTIC_ROLE`, `SEMANTIC_SUPPORT`, or `SEMANTIC_NOT_DIRECT_CANONICAL`).
3. The semantic count must equal the frozen baseline of **336**.
4. Every non-semantic Special term must resolve either to an exact canonical identity in the selected Danbooru snapshot or to exactly one alias target in the selected alias closure.
5. Alias-target reconstructions must total the frozen Alias baseline of **778**.
6. Any unresolved or ambiguous non-semantic Special term aborts the run. It is never guessed or silently downgraded to a gap.

With the 2,788 total, 336 semantic, and 778 alias-target checks satisfied, the remaining 1,674 rows are canonical Core + Extended identities, matching the frozen `759 + 915` baseline.

The fallback reconstructs canonical-target evidence from the same selected Danbooru alias closure before General gap classification, so a Special alias does not become a false `GENERAL_ONLY_GAP` merely because the protected `canonical_target` column is unavailable.

The two Special modes are mutually exclusive. Final closeout should record which mode produced the inventory.

## Normalization and identity closure

For comparison, use this order:

1. Unicode NFKC
2. lower/casefold
3. trim
4. `_` and space treated as equivalent for comparison only
5. collapse repeated whitespace
6. exact normalized Special Tag match
7. Special `canonical_target` match where available, or fail-closed reconstructed target in tracked-profile mode
8. Danbooru Alias -> canonical closure
9. semantic overlap checked separately from exact identity coverage

A semantic-near-match does not automatically prove the canonical identity is already represented. Conversely, a spelling/alias difference is not a true gap if it resolves to an already represented canonical identity.

## Audit classification

- `CANDIDATE`: distinct General canonical identity with no confirmed Special exact/alias/canonical closure and useful Special discovery value.
- `NEEDS_REVIEW`: likely gap, but semantic-boundary or product-fit judgment remains.
- `DUPLICATE_ALREADY_COVERED`: false gap; Special already reaches the same identity through exact normalized tag, alias, or canonical target.
- `OUTSIDE_SPECIAL_NONCONTENT`: structurally outside Special's product role for a non-content reason. This must never be used as a censorship bucket.
- `DISCOVERY_QUEUE`: promising lead whose count, alias closure, or canonical-target closure is not yet complete.

## Current partial checkpoint

The first focused pass has already demonstrated why legacy marker-only comparison is unsafe:

- `cleavage_cutout` looks blank in the old full-KB marker but is reachable through Special-side aliases such as `cleavage window` / `heart cleavage cutout`.
- `piledriver_(sex)` normalizes to current Special ID 793 `piledriver (sex)`.
- `micro_pasties` is current Special ID 2439.

At the same time, several current General canonicals remain strong gap candidates after exact current-Special checks, including `skindentation`, `ass_visible_through_thighs`, `thigh_gap`, and `micro_bikini`.

See `docs/issue94/special_gap_audit_checkpoint_v1.csv` for the current evidence ledger.

## Phase-1 protection boundary

This branch must not mutate:

- accepted Special production rows
- `docs/issue64/production_candidate` accepted General data
- Issue #70 queue/source/results
- `artifacts/current/Data/catalog.db`
- `artifacts/current/UserData/user.db`

Phase 1 produces audit evidence only.

## Not yet claimed

This checkpoint is **not** a completed scan of all 30,743 General canonicals. Final counts such as `GENERAL_ONLY_GAPS`, `CANDIDATE_COUNT`, and `NEEDS_REVIEW_COUNT` must not be frozen until deterministic full closure has been run and independently spot-checked.

## Required final closeout fields

`RESULT`
`LIVE_MAIN`
`DANBOORU_SOURCE`
`SPECIAL_SOURCE_MODE`
`TOTAL_CANONICAL_SCANNED`
`SPECIAL_PRESENT`
`ALIAS_OR_SEMANTIC_OVERLAP`
`GENERAL_ONLY_GAPS`
`CANDIDATE_COUNT`
`NEEDS_REVIEW_COUNT`
`EXCLUDED_NONCONTENT_COUNT`
`CONTENT_FILTER_USED=NO`
`PRODUCTION_FILES_CHANGED=NO`
`ISSUE70_MUTATED=NO`
`NEXT`
