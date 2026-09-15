# Issue #94 Special Gap Audit — Method v1

Status: **MECHANICAL FULL SCAN COMPLETE / CANDIDATE REVIEW IN PROGRESS / NO PRODUCTION MUTATION**

Original branch base main: `05078dde8bf7964f18d2c0accfcdb66075601664`

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

The historical full-KB `Special2788=YES/blank` column is **not authoritative enough by itself** for gap detection. It misses identity relationships reachable through normalization or alias/canonical closure.

## Deterministic source modes

`scripts/issue94/special_gap_audit.py` supports two Danbooru source families. They share the same downstream identity-classification logic.

### A. Full-KB mode

Use the verified derived full knowledge base directly:

- `--full-kb <danbooru_full_tag_knowledge_base_...csv>`
- `--special <illustrious_tag_knowledge_base_2788.csv>` or the tracked profile fallback described below
- optional `--alias-map <danbooru_alias_map_34630.csv>`

This mode preserves the historical `Special2788` marker only as a diagnostic field. The marker is never authoritative for identity coverage.

### B. Canonical-source mode

Use the frozen historical canonical source:

- `--canonical-source <danbooru-2026-09-02.csv>`
- optional `--alias-index <verified normalized alias index>`
- `--special <illustrious_tag_knowledge_base_2788.csv>` or the tracked profile fallback described below

The canonical source is the same 124,016-row snapshot identified by SHA-256 `9b32d5ac0713ab252e7470ba6af9cb34de56878b6b3b13dfbbf6a4a37d82d95b`.

If `--alias-index` is provided, only uniquely resolved aliases from that verified index are admitted. If it is omitted, the scanner derives alias closure directly from the fourth column of the historical canonical source. In either case:

- aliases mapping to more than one normalized canonical are not silently assigned;
- alias surfaces colliding with a canonical identity are excluded from alias closure because canonical precedence wins;
- only one-target alias closure can prove canonical coverage.

The historical full-KB `Special2788` marker is unavailable in canonical-source mode, so `legacy_blank_but_identity_covered` is reported as `null`. This does **not** affect `PRESENT_EXACT`, `PRESENT_CANONICAL_TARGET`, `PRESENT_ALIAS_CLOSURE`, `SEMANTIC_EXACT_OVERLAP_ONLY`, or `GENERAL_ONLY_GAP` classification.

The full scan remains fail-closed on `General == 30,743` and `Special == 2,788` unless explicit test-only expected counts are supplied.

## Deterministic Special input modes

### S1. Protected Special source

Preferred when the original accepted Special CSV is available locally:

- `--special <illustrious_tag_knowledge_base_2788.csv>`

Required columns are `ID`, `Tag`, `Danbooru種別`, and `canonical_target`.

### S2. Tracked Generation Profile fallback

When the protected Special source is not mounted, use:

- `--special-profile data/generation/special2788_generation_profile.csv`

This is a fail-closed reconstruction path, not a heuristic replacement:

1. `SpecialID` + `Tag` provide all 2,788 accepted identities.
2. Semantic rows are recognized only through approved tracked semantic markers (`APPROVED_SEMANTIC_ROLE`, `SEMANTIC_SUPPORT`, or `SEMANTIC_NOT_DIRECT_CANONICAL`).
3. Semantic count must equal the frozen baseline of **336**.
4. Every non-semantic Special term is classified against the selected Danbooru snapshot as:
   - exact canonical identity;
   - unique alias -> one canonical target;
   - historical multi-target alias -> retained as ambiguous and **not** used to claim coverage of any one canonical;
   - unresolved -> hard failure.
5. The Alias layer must total **778** across unique-target and multi-target Alias rows.
6. Any truly unresolved non-semantic Special term aborts the run.

Verified reconstruction on the 2026-09-02 snapshot:

- exact canonical Special rows: **1,674**
- unique-target Alias rows: **767**
- multi-target Alias rows: **11**
- Semantic rows: **336**
- unresolved non-semantic rows: **0**
- total: `1,674 + 767 + 11 + 336 = 2,788`
- Alias baseline: `767 + 11 = 778`

The 11 preserved multi-target Alias rows are:

- `1273 cum on leg` -> `cum on body` / `cum on legs`
- `1276 cum on thighs` -> `cum on body` / `cum on legs`
- `1326 cum inside clothes` -> `cum in clothes` / `cum on clothes`
- `1327 cum inside thighhigh` -> `cum in clothes` / `cum on clothes`
- `1330 cum on hat` -> `cum on clothes` / `cum on headwear`
- `1332 cum on pantyhose` -> `cum on clothes` / `cum on legwear`
- `1334 cum on socks` -> `cum on clothes` / `cum on legwear`
- `1337 cum on thighhighs` -> `cum on clothes` / `cum on legwear`
- `1338 cum under clothes` -> `cum in clothes` / `cum on clothes`
- `1578 descensored` -> `decensored` / `uncensored`
- `2634 thighhigh` -> `single thighhigh` / `thighhighs`

Historical prompt-reference data already records multi-target normalization for these accepted Alias identities (for example IDs 1273 and 1276 as `->複数正規化先`), so they must not be forced to one target merely to simplify #94.

The two Special modes are mutually exclusive. Final closeout records which mode produced the inventory.

## Normalization and identity closure

For comparison, use this order:

1. Unicode NFKC
2. lower/casefold
3. trim
4. `_` and space treated as equivalent for comparison only
5. collapse repeated whitespace
6. exact normalized Special Tag match
7. Special `canonical_target` match where available, or reconstructed unique target in tracked-profile mode
8. Danbooru Alias -> canonical closure
9. semantic overlap checked separately from exact identity coverage

A semantic-near-match does not automatically prove the canonical identity is already represented. Conversely, a spelling/alias difference is not a true gap if it resolves to an already represented canonical identity.

## Mechanical full-scan checkpoint

The deterministic full scan completed successfully through GitHub Actions.

- workflow: `Issue94 Special Gap Audit`
- run ID: `35011193515`
- audit branch commit: `ae770e0ce58f8b7b7fbe2c53485b010129d6f4af`
- source: pinned `2026-09-02` historical canonical CSV
- source SHA-256 verification: **PASS**
- scanner syntax validation: **PASS**
- full scanner execution: **PASS**
- artifact ID: `10413069909`
- artifact digest: `sha256:9fe8184316899b8761f7f1816c56d5e7e79352d1abb93665abd437b0e89c5608`

Danbooru alias-source facts during this run:

- embedded alias entries seen: **34,630**
- unique alias rows used: **34,231**
- ambiguous alias rows skipped: **45**
- canonical-precedence alias rows skipped: **141**

General identity result:

- General canonical scanned: **30,743**
- `PRESENT_EXACT`: **1,672**
- `PRESENT_CANONICAL_TARGET`: **50**
- `GENERAL_ONLY_GAP`: **29,021**
- distinct General canonicals currently proven Special-covered: **1,722**

The Special reconstruction has 1,674 exact canonical rows overall, while General inventory has 1,672 `PRESENT_EXACT` rows because two exact Special identities are outside Danbooru General in this snapshot: `audible internal cumshot` is Meta and `tenga` is Copyright.

The 29,021 rows are **identity gaps only**. They are not 29,021 approved Special candidates. Product-fit review is a separate stage.

`CONTENT_FILTER_USED=NO`
`PRODUCTION_FILES_CHANGED=NO`
`ISSUE70_MUTATED=NO`

## Audit classification

- `CANDIDATE`: distinct General canonical identity with no confirmed Special exact/alias/canonical closure and useful Special discovery value.
- `NEEDS_REVIEW`: likely gap, but semantic-boundary or product-fit judgment remains.
- `DUPLICATE_ALREADY_COVERED`: false gap; Special already reaches the same identity through exact normalized tag, alias, or canonical target.
- `OUTSIDE_SPECIAL_NONCONTENT`: structurally outside Special's product role for a non-content reason. This must never be used as a censorship bucket.
- `DISCOVERY_QUEUE`: promising lead whose identity closure/product-fit review is not yet complete.

## Candidate-review checkpoint

The focused review already demonstrated why legacy marker-only comparison is unsafe:

- `cleavage_cutout` looks blank in the old full-KB marker but is reachable through Special-side aliases.
- `piledriver_(sex)` normalizes to Special ID 793 `piledriver (sex)`.
- `micro_pasties` is Special ID 2439.

Strong provisional General-only candidates include:

- `skindentation`
- `ass_visible_through_thighs`
- `thigh_gap`
- `micro_bikini`

See `docs/issue94/special_gap_audit_checkpoint_v1.csv` for the human-review evidence ledger. Mechanical full-scan facts are stored separately from human candidate judgments.

## Phase-1 protection boundary

This branch must not mutate:

- accepted Special production rows
- `docs/issue64/production_candidate` accepted General data
- Issue #70 queue/source/results
- `artifacts/current/Data/catalog.db`
- `artifacts/current/UserData/user.db`

Phase 1 produces audit evidence only.

## Remaining work

The complete 30,743-General mechanical inventory now exists. Remaining Phase-1 work is:

1. prioritize the 29,021 `GENERAL_ONLY_GAP` rows for human/product-fit review without using content severity as a filter;
2. materialize the candidate subset with reasons;
3. keep explicit duplicate / non-content exclusion / needs-review evidence;
4. summarize candidate coverage by practical concept area;
5. independently spot-check the mechanical inventory before final closeout.

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
