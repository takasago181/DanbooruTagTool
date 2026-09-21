# Issue #180 — Single canonical home pilot

Status: RESEARCH / NO PRODUCTION APPLY

Baseline main: `bea08712eb691ca867e218d211023d7206b6b7dc`

## Goal

Test the product target:

`official Character -> HOME_COPYRIGHT (0..1)`

against representative Character rows from:

- Pokémon
- VOCALOID
- Kantai Collection
- Bocchi the Rock!
- hololive

The pilot intentionally includes rows whose preserved Issue #70 `related_copyright` contains multiple appearance/co-occurrence candidates.

## Result

12 Character rows were reviewed.

- HOME_CONFIRMED: **12**
- HOME_UNRESOLVED: **0**
- NOT_OFFICIAL_CHARACTER: **0**
- old RelatedCopyright entries across these rows: **36**
- retained canonical home links: **12**
- rejected non-home relation candidates: **24**

Every pilot row had three historical RelatedCopyright candidates. The single-home model reduced every row to exactly one canonical home without needing multi-home ownership.

## Proposed homes

| Ecosystem | Characters | Home Copyright |
| --- | ---: | --- |
| Pokémon | 3 | `pokemon` |
| VOCALOID | 2 | `vocaloid` |
| Kantai Collection | 3 | `kantai_collection` |
| Bocchi the Rock! | 1 | `bocchi_the_rock!` |
| hololive | 3 | `hololive` |

See `SINGLE_HOME_PILOT.csv` for row-level evidence and rejected historical relations.

## What the pilot falsified

Historical co-occurrence is unsuitable as ownership authority.

Examples in preserved source data:

- Hatsune Miku: `vocaloid | utau | pokemon`
- Gotoh Hitori: `bocchi_the_rock! | pokemon | chainsaw_man`
- Ikazuchi: `kantai_collection | pokemon | youtube`
- Shirakami Fubuki: `hololive | hololive_english | pokemon`
- Gawr Gura: `hololive | hololive_english | reflect_(gawr_gura)`

The extra entries are appearances, subgroup/context labels, derivative works, or unrelated co-occurrence—not additional homes.

## Authority behavior that worked

### 1. QUALIFIER_COPYRIGHT

Strongest deterministic case when the Character canonical qualifier resolves to an existing Copyright row.

Examples:
- `dawn_(pokemon)` -> `pokemon`
- `kaito_(vocaloid)` -> `vocaloid`
- `ikazuchi_(kancolle)` -> `kantai_collection`
- `irys_(hololive)` -> `hololive`

### 2. Official franchise/work/talent pages

Useful for unqualified Character tags.

Examples:
- `pikachu`, `lapras` -> official Pokémon surfaces
- `hatsune_miku` -> Piapro official Character page
- `gotoh_hitori` -> Bocchi the Rock! official Character page
- `shirakami_fubuki`, `gawr_gura` -> hololive official talent pages

## Rule correction discovered by the pilot

Do **not** define HOME_COPYRIGHT as merely the most specific media appearance or organizational subdivision.

Instead:

> HOME_COPYRIGHT is the one stable official parent Copyright that best represents where the Character canonically belongs in this product.

Therefore:
- Pokémon species/characters do not move between individual game/anime Copyrights.
- hololive talents do not get multiple homes for hololive / hololive English / generation or unit.
- adaptation Copyrights do not replace the original stable home.
- collaboration/crossover/event Copyrights never create an additional home.
- if a Character canonical qualifier resolves to a valid Copyright, that is strong evidence for the stable home.
- subwork/subunit metadata may be retained separately, but is not ownership.

A specific subwork may still be HOME_COPYRIGHT when it is itself the stable canonical origin and no broader product parent is the intended ownership surface. This must be proven rather than inferred from co-occurrence.

## Fanwork noise observed simultaneously

The relation pilot independently reproduced search-noise families that belong to #179 cleanup:

- `ミクの日` — fan/event term
- `初音ミクイラスト` — fanart/search hashtag style
- `ぼ喜多` — pairing
- `絵フブキ` — fanart hashtag
- `コハヒカ / サトヒカ / シロヒカ / ポチャヒカ` — pairing terms
- `雷ちゃんマジ天使`, `なにこれぜかましい` — fandom/meme-style terms

These should not affect HOME_COPYRIGHT proof.

## Decision

The 0..1 cardinality is viable for this pilot and materially cleaner than preserved co-occurrence relations.

This is **not** yet proof that all 35,890 Character rows can be resolved automatically. The next relation step should measure:
1. how many rows resolve by verified qualifier;
2. how many unqualified rows resolve from curated/official lists;
3. how many remain HOME_UNRESOLVED;
4. precision on a clean control sample before any runtime relation is rebuilt.

Production and accepted Issue #70 source remain unchanged.
