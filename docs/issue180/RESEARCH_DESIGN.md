# Issue #180 — Character/Copyright High-Precision Authority Research

Status: RESEARCH / NO PRODUCTION APPLY

Baseline main: `bea08712eb691ca867e218d211023d7206b6b7dc`

## Problem

The Issue #70 `RelatedCopyright` source is post co-occurrence evidence. It is useful for candidate generation, but it is not semantic ownership authority. Issue #177 therefore hides Character/Copyright relation UI while preserving the raw evidence.

The replacement authority must optimize precision before coverage:

> A missing relation is preferable to a wrong relation.

No rule in this research may force every Character row to receive a Copyright.

## Findings

### 1. Danbooru implications are not Character → Copyright ownership

Pinned Danbooru source reviewed at:

- repo: `danbooru/danbooru`
- commit: `3b18ca948b24461146399886500766bb0fa9a9af`

`TagImplication#tag_categories_are_compatible` requires antecedent and consequent tags to have the same category. Danbooru's own test explicitly rejects `hatsune_miku -> vocaloid` because Character → Copyright implication is cross-category.

Therefore:

- Character implication is useful to normalize/inherit from Character variants to a base Character.
- Copyright implication is useful to normalize Copyright hierarchy.
- Neither is direct Character → Copyright authority.

### 2. Danbooru character qualifiers can provide strong evidence, but only after category resolution

Danbooru's current `howto:character` says ambiguous copyrighted characters commonly use a `_(series)` qualifier.

Examples include Pokémon and KanColle-style names.

A suffix is accepted as ownership evidence only when the qualifier (after verified alias resolution) resolves to an in-scope Copyright tag. A parenthesized suffix by itself is never sufficient because qualifiers can also represent artists, forms, costumes, or other disambiguators.

### 3. Curated Copyright/list wiki membership is the strongest scalable source found

Danbooru maintains explicit curated membership lists, including:

- `list_of_pokemon_characters`
- `list_of_pokemon` (creatures)
- `list_of_vocaloid_characters`
- `list_of_kantai_collection_characters`
- `bocchi_the_rock!` → Characters section
- `hololive` → List of Members

This is materially different from post co-occurrence: the wiki explicitly asserts membership in the work/group.

### 4. Existing implementation prior art

`Wenaka2004/dan-emb` (reviewed at commit `373027c979da5d5b89e1569ffcda1397cf0c5901`) builds a Character/Copyright table from Danbooru wiki data.

Useful part:
- extract Character/Member/Cast links from Copyright wiki sections.

Rejected for automatic product truth:
- its fallback scans arbitrary Character wiki body links and accepts the first known Copyright link.

A Character wiki can mention crossover appearances, related works, derivatives, or See-also material. Generic body-link selection is therefore review evidence only.

## Frozen evidence model for pilot

Each accepted relation row must retain provenance.

Suggested fields:

- `character_canonical`
- `copyright_canonical`
- `evidence_kind`
- `source_ref`
- `source_revision` when available
- `direct_or_inherited`
- `confidence_class`
- `review_status`
- `notes`

### Automatic ACCEPT tiers

#### A1 — CURATED_COPYRIGHT_LIST

The Character is linked from an explicit Character/Member/Cast list that is scoped to one Copyright.

Examples:
- Gotoh Hitori in Bocchi the Rock!'s Characters section.
- Shirakami Fubuki in hololive's List of Members.
- Hatsune Miku in List of VOCALOID characters.
- Ikazuchi/Inazuma in List of Kantai Collection characters.
- Dawn in List of Pokémon characters.
- Pikachu in List of Pokémon.

List pages must themselves be explicitly scoped to the target Copyright. A generic wiki page containing a list is not enough.

#### A2 — QUALIFIER_COPYRIGHT

The final canonical Character qualifier resolves exactly to a Copyright canonical or a verified alias of one.

Examples:
- `dawn_(pokemon)` → `pokemon`
- `ikazuchi_(kancolle)` → alias `kancolle` → `kantai_collection`

Do not infer from an unresolved qualifier.

### Automatic propagation tiers

#### P1 — CHARACTER_ALIAS_CANONICALIZATION

Resolve verified/active aliases before mapping.

Example:
- legacy `hikari_(pokemon)` resolves to canonical `dawn_(pokemon)`.

Aliases change identity lookup; they do not independently assert Copyright membership.

#### P2 — CHARACTER_IMPLICATION_INHERITANCE

A Character variant may inherit verified relations from a base Character only when a current same-category Character implication links the variant to that base.

This is useful for costumes/forms while respecting Danbooru's category model.

#### P3 — COPYRIGHT_IMPLICATION_NORMALIZATION

A Copyright may be normalized through current same-category Copyright implications to a parent franchise if the product contract wants franchise-level browse.

Keep the original direct Copyright provenance as well as the normalized parent.

### REVIEW ONLY tiers

#### R1 — CHARACTER_WIKI_BODY_REFERENCE

A Character wiki body links to a Copyright, but the link is not inside a trusted relation structure.

Use only to generate a candidate for review.

#### R2 — COOCCURRENCE

Issue #70 co-occurrence / current `RelatedCopyright` / Danbooru related-tag ranking.

Use only to:
- propose candidates,
- measure disagreement,
- find likely missing mappings.

Never promote a relation solely because co-occurrence is high.

## Pilot acceptance contract

Pilot families:

1. Pokémon
2. VOCALOID
3. Kantai Collection
4. Bocchi the Rock!
5. hololive

The pilot must include both positive and negative gold rows.

Minimum acceptance before any broad regeneration:

- zero known cross-franchise false positives in the gold set,
- every accepted row has provenance,
- no co-occurrence-only row can be ACCEPT,
- unresolved characters are allowed,
- alias normalization is tested,
- Character variant inheritance is tested separately from direct ownership,
- old Issue #70 source/runtime assets remain unchanged.

Coverage is a secondary metric. Precision failure blocks promotion even when coverage is high.

## Runtime design direction

Do not overwrite `RelatedCopyright` in the accepted Issue #70 assets.

If the pilot passes, create a new overlay/authority with a distinct field or load stage, for example:

- `VerifiedCopyright`
- or `CharacterCopyrightAuthority`

The UI should read only the new verified authority when relation browsing is eventually re-enabled.

The old co-occurrence relation remains preserved for diagnostics/candidate generation, not product truth.

## UI semantics to decide after pilot

If multiple verified copyrights exist, do not silently collapse them to a fabricated single “origin work”.

Prefer wording such as `関連作品` unless the evidence schema explicitly distinguishes an origin/primary franchise relation.

## Sources reviewed

Danbooru source:
- https://github.com/danbooru/danbooru/blob/3b18ca948b24461146399886500766bb0fa9a9af/app/models/tag_implication.rb
- https://github.com/danbooru/danbooru/blob/3b18ca948b24461146399886500766bb0fa9a9af/test/unit/bulk_update_request/command/create_implication_command_test.rb

Danbooru wiki:
- https://safebooru.donmai.us/wiki_pages/howto%3Acharacter
- https://safebooru.donmai.us/wiki_pages/list_of_pokemon_characters
- https://safebooru.donmai.us/wiki_pages/list_of_pokemon
- https://safebooru.donmai.us/wiki_pages/list_of_vocaloid_characters
- https://safebooru.donmai.us/wiki_pages/list_of_kantai_collection_characters
- https://safebooru.donmai.us/wiki_pages/bocchi_the_rock!
- https://safebooru.donmai.us/wiki_pages/hololive

Prior art:
- https://github.com/Wenaka2004/dan-emb/blob/373027c979da5d5b89e1569ffcda1397cf0c5901/build_char_copyright.py
