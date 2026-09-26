# Issue #180 — HOME Authority Policy v1

Status: PILOT POLICY / NO PRODUCTION APPLY

Target invariant:

`official Character -> HOME_COPYRIGHT (0..1)`

This policy is derived from B001 qualifier cases and B002 50-row legacy hard-case review.

## Auto-confirm authority

A Character may become `HOME_CONFIRMED` only when exactly one HOME remains after accepted authority evaluation.

### A1 — QUALIFIER_COPYRIGHT

Accept when the Character canonical tag contains a final Copyright qualifier that resolves uniquely to an in-scope Copyright root.

Examples:
- `hibiki_(kancolle)` -> `kantai_collection`
- `nozomi_(blue_archive)` -> `blue_archive`
- `chisa_(wuthering_waves)` -> `wuthering_waves`

Alias/root normalization such as `kancolle -> kantai_collection` must be explicitly approved. An unverified alias is not A1.

### A2 — CURATED_COPYRIGHT_LIST

Accept when an official or separately approved curated Character/member list explicitly places the Character in one canonical home/root.

Examples:
- Pikachu -> Pokémon
- Gotoh Hitori -> Bocchi the Rock!
- Houshou Marine -> hololive
- Hakurei Reimu -> Touhou

Generic wiki-body links, search aliases, post co-occurrence, and old RelatedCopyright are not curated-list authority.

### A3 — CURATED_COPYRIGHT_LIST + APPROVED_ROOT_NORMALIZATION

Accept when:
1. an official/approved list proves the Character belongs to a specific subwork; and
2. a separately reviewed normalization map resolves that subwork to one stable product root.

Examples from B002:
- Fate/Grand Order or Fate/stay night -> `fate_(series)`
- Ave Mujica -> `bang_dream!`

Root normalization must never be inferred ad hoc from string similarity or co-occurrence.

### A4 — CHARACTER_IMPLICATION_INHERITANCE

Reserved for later expansion. An official Character variant may inherit HOME only from a base Character that is already `HOME_CONFIRMED`.

This authority is not sufficient to prove that the variant row itself is official; #179 owns that decision.

## Mandatory unresolved states

Do not auto-confirm HOME for:

- `NO_ACCEPTED_HOME_AUTHORITY`
- `QUALIFIER_ALIAS_UNVERIFIED`
- `CATALOG_ROOT_FALLBACK`
- legacy RelatedCopyright/co-occurrence only
- search/alias text only
- multiple accepted HOME candidates
- a root that does not exist in the current Copyright catalog

These remain `HOME_UNRESOLVED`.

## Candidate rejection

A sampled ecosystem may be explicitly rejected without yet proving the true HOME.

Example:
`elysia_(honkai_impact)` rejects Honkai: Star Rail from its canonical qualifier, but remains `HOME_UNRESOLVED` until `honkai_impact` is independently mapped to a canonical Copyright root.

## Cardinality gate

For every official Character:

`accepted_home_count <= 1`

If two accepted authorities disagree, do not choose by score or majority. Emit `HOME_UNRESOLVED` with a conflict requiring review.

## B002 calibration

B002 first pass:
- 50 rows total
- 39 HOME_CONFIRMED
- 11 HOME_UNRESOLVED

The unresolved rows are intentional precision protection, not audit failures.

No rule in this document authorizes production apply or accepted-source mutation.


## Reviewed adaptation / community exceptions

### Blue Archive The Animation

- qualifier family: `blue_archive_the_animation`
- canonical HOME: `blue_archive`
- authority: https://sh-anime.shochiku.co.jp/bluearchive-anime/news/7/
- reason: the official TV anime site explicitly identifies `ブルーアーカイブ The Animation` as based on the app game `ブルーアーカイブ -Blue Archive-`. Under the Issue #180 single-canonical-HOME policy, an adaptation qualifier does not create a second HOME root for the same Character identity.

### Futaba Channel

- qualifier family: `futaba_channel`
- automatic FAMILY_QUALIFIER HOME: prohibited
- reason: Futaba Channel is an imageboard/community rather than a canonical fictional work root. Community/net characters require identity/officiality review and must not be promoted merely because the Character qualifier equals a Copyright tag.
