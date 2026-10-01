# Artist-qualified Browse review

Base: `8789c41b8e1b4b96bc770a908f0dffd3dc865910`.

One bounded pass reviewed all 1,092 previously unresolved subjects carrying
`ARTIST_QUALIFIED_ORIGINAL_OR_DERIVATIVE_IDENTITY`. This is an independent
Browse overlay. No formal HOME, VARIANT_OF, alias or source authority is promoted.

| Disposition | Count |
| --- | ---: |
| Fan derivative with origin Browse HOME | 48 |
| Explicit authored-work character with Browse HOME | 8 |
| Creator original / independent / avatar, unresolved | 556 |
| Ambiguous, unresolved | 480 |
| Total | 1,092 |

The CSV combines the first two as `DERIVATIVE_OR_WORK_SCOPED` (56), with a
separate pattern distinguishing published creator-work membership. An authored
work character is not described as a fan derivative merely because its tag is
artist-qualified.

## Patterns

- Exact nested work qualifiers: the work scope takes precedence over the artist
  qualifier for Browse. These remain provisional product judgments.
- Borrowed Character identity: chibi/animalization/genderswap/alternate design
  of recognizable Touhou, Blue Archive, Vocaloid and other work Characters.
- Explicit in-universe fan design: Pokemon trainers/personifications, Splatoon
  fan Characters, and authored depictions of game-world player Characters.
  These are fan identities, not official cast certification.
- Explicit named work: descriptions such as "Character in ..." or "Main
  character of ..." rescue creator-qualified manga Characters without requiring
  an official roster. Eight such assignments were made.
- Standalone creator OC: own-page original/creator descriptions establish this
  bucket. Artist qualifier or candidate `original` alone does not establish it.
- VTuber, artist avatar and self-insert contexts are kept separate from fictional
  work cast. This pass does not transfer a former agency or guest IP to them.
- Loose resemblance, cosplay, inspiration, see-also links and crossover context
  do not establish a HOME. Old Man (Guin Guin), Little Blue and British Admiral
  have multiple or independent contexts and remain unresolved. Game-inspired
  Baphomet and Melusoy are not forced into their associated games.
- Empty or absent wiki titles and unclear descriptions remain ambiguous. Of
  the 480 ambiguous subjects, 434 have no nonempty own-page description.

## Results across the overlay

| Metric | Before | After |
| --- | ---: | ---: |
| Reviewed Browse HOME | 7,495 | 7,551 |
| Unresolved | 2,607 | 2,551 |
| Top2000 unresolved | 157 | 148 |
| Top500 unresolved | 10 | 10 |

All 10,102 overlay subjects remain accounted once. Only the 1,092 selected
subjects receive updated review notes; all other rows remain unchanged. All 56
assignments are additions to previously unresolved Browse rows, not replacements.

## Evidence and reconstruction

Reused 59 exact cached own pages and obtained 677 more pages with 13 exact-title
bulk requests, each requesting up to 80 tags, using at most three concurrent
requests. No individual Character search, deep research or broad wiki recrawl.
The 356 absent exact titles are recorded without treating absence as negative
membership proof. Among the 736 available own pages, 658 have nonempty bodies.

Raw inputs, endpoint URLs, requested titles, fetch times, wiki IDs and update
timestamps are retained in `BROWSE_ARTIST_REVIEW_WIKI_INPUTS_V1.json.gz`.
Human shared-pattern choices are in `scripts/issue216/review_artist_qualified_browse.py`.
Rebuild outputs with that script without network access.

Outputs:

- `BROWSE_ARTIST_QUALIFIER_REVIEW_V1.csv`: all 1,092 dispositions and evidence excerpts.
- `BROWSE_ARTIST_QUALIFIER_GROUPS_V1.csv`: shared pattern/root totals.
- `REVIEWED_BROWSE_HOME_V2.csv`: complete independent overlay after this pass.
- `BROWSE_ARTIST_QUALIFIER_CHECKPOINT_V1.json`: counts and input hashes.

Data checks: accounting, uniqueness, assigned-root existence, deterministic
output byte equality, unchanged rows outside this population, and unchanged
formal ledgers / prior overlays. No local unit tests added or regression suite
run for this data audit. Branch CI validates existing formal authority.

Formal #180/#216 decisions, previous overlay versions and protected local data
are retained. No main merge or production apply. All results are
`formal_authority_eligible=NO`.
