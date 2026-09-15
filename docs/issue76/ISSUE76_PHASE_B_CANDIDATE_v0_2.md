# Issue #76 Phase B candidate v0.2 — full 2,788 projection + bounded review queues

Status: **DESIGN EVIDENCE / NOT PRODUCTION AUTHORITY / NO WPF OR CANONICAL MUTATION**

## Result

The accepted Issue #56 full browse mapping was projected across all **2,788 Special IDs** into the current Issue #76 v2 candidate axes:

- `種類から探す` — one coarse semantic home
- `部位から探す` — zero or more body-site facets
- `テーマから探す` — zero or more cross-cutting theme facets

All 2,788 rows are accounted for. Among v1-resolved rows, the projection produced **0 unhandled/no-kind rows**.

This is still a candidate migration. It is intentionally not written into production taxonomy or WPF.

## Candidate kind distribution

| Kind | Rows |
|---|---:|
| 行為・接触 | 901 |
| 衣服・露出 | 503 |
| 身体・状態 | 319 |
| 道具・物 | 288 |
| 体液・排泄 | 273 |
| ポーズ・構図・場面 | 154 |
| 人物・関係 | 123 |
| 異形・変形 | 118 |
| 表現・メタ | 66 |
| v1 REVIEW_REQUIRED / fail-closed | 43 |

The largest shelf remains `行為・接触` at 901. This alone is not evidence that visible action subgenres should return. The next UX test should first evaluate broad-shelf browsing with ordinary search/sort and body/theme routes.

## Body-site route distribution

Counts remain conservative because they are derived from accepted v1 primary/secondary paths rather than a new semantic tagger.

| Body-site facet | Rows |
|---|---:|
| 乳房・乳首 | 257 |
| 男性器 | 234 |
| 口・口内 | 174 |
| 女性器 | 173 |
| 臀部・肛門（暫定） | 111 |
| 尿道 | 20 |

Body-site multiplicity:
- 0 facets: 1,843
- 1 facet: 921
- 2 facets: 24

The old `BODY_ANATOMY>BUTTOCK_ANUS` route is not assumed to mean “anal” for every row. Rows using that mixed route are separately queued for a naming/split audit.

## Theme route distribution

| Theme facet | Rows |
|---|---:|
| 拘束・BDSM | 366 |
| 損傷・R18G | 66 |
| 生殖・妊娠・授乳 | 25 |

Theme multiplicity:
- 0 facets: 2,332
- 1 facet: 455
- 2 facets: 1

Combined body/theme facet multiplicity:
- 0 facets: 1,502
- 1 facet: 1,146
- 2 facets: 140
- 3+ facets: 0

This remains lightweight enough for a shallow browse model.

## Projection status

| Status | Rows | Meaning |
|---|---:|---|
| `AUTO_CANDIDATE` | 2,724 | deterministic route-based v2 candidate |
| `REVIEW_V1_UNRESOLVED` | 43 | already unresolved in accepted v1; stays fail-closed |
| `REVIEW_MIXED_FAMILY` | 21 | `CHASTITY_CONTROL` mixes device/state/control concepts and should not be blindly frozen as one kind |

There are **no additional `REVIEW_NO_KIND` rows** among v1-resolved entries.

## Bounded review queues

The generated review queue has **126 rows** total across three distinct concerns:

- 43 `REVIEW_V1_UNRESOLVED` — blocking, inherited from v1
- 21 `REVIEW_MIXED_FAMILY` — focused family review for `CHASTITY_CONTROL`
- 62 `SITE_FACET_AUDIT` — non-blocking audit for rows that relied on the old mixed `BODY_ANATOMY>BUTTOCK_ANUS` route

The 62 site rows are not “unclassified”. They already have candidate homes; only the body-site label/split is intentionally provisional.

## Sanity checks

The motivating cases project naturally:

- ID 266 `anal beads` -> `道具・物` + `臀部・肛門（暫定）`
- ID 267 `anal tail` -> `道具・物` + `臀部・肛門（暫定）`
- ID 268 `butt plug` -> `道具・物` + `臀部・肛門（暫定）`
- ID 264 `vibrator in anus` -> `道具・物` + `臀部・肛門（暫定）`
- ID 209 `urethral beads` -> `道具・物` + `尿道`
- ID 208 `cum in urethra` -> `体液・排泄` + `尿道`
- ID 219 `urethral sounding` -> `行為・接触` + `尿道`
- ID 270 `dildo gag` -> `道具・物` + `口・口内` + `拘束・BDSM`
- ID 1814 `ball gag` -> `道具・物` + `口・口内` + `拘束・BDSM`
- ID 1828 `handcuffs` -> `道具・物` + `拘束・BDSM`
- ID 1838 `shackles` -> `道具・物` + `拘束・BDSM`
- ID 2190 `pregnant` -> `身体・状態` + `生殖・妊娠・授乳`
- ID 2164 `blood` -> `体液・排泄` + `損傷・R18G`

## Reproducibility

`tools/issue76_build_v2_candidate.py` regenerates:

- `docs/issue76/generated/issue76_v2_candidate_mapping_v0_2.csv`
- `docs/issue76/generated/issue76_v2_review_queue_v0_2.csv`
- `docs/issue76/generated/issue76_v2_candidate_meta_v0_2.json`

The generator consumes the accepted Issue #56 source/mapping and validates exact `1..2788` coverage before writing output.

## What this does not decide yet

- `臀部・肛門` final naming/split is not frozen.
- the 21 chastity/control rows are not frozen to `道具・物` merely because the v1 shelf was device-heavy.
- the 43 v1 unresolved rows are not force-fit.
- `行為・接触` is not split merely because it is large.
- no production browse sidecar or WPF tree has been changed.

## Next gate

Before WPF implementation, resolve the two new bounded semantic questions:

1. `BODY_ANATOMY>BUTTOCK_ANUS` 62-row site audit: decide whether one broad `尻・肛門` facet is actually clearer than separate `尻` / `肛門` facets.
2. `CHASTITY_CONTROL` 21-row family audit: assign device/state/control rows to natural kinds while retaining `拘束・BDSM` as the cross-cutting theme.

Then run a practical browse test against the 901-row `行為・接触` shelf. Only restore any visible subcategory if the broad-shelf test actually fails.

Verdict: **FULL_2788_V2_CANDIDATE_MATERIALIZED / BOUNDED_REVIEW_POOL_CREATED / PRODUCTION_UNCHANGED**
