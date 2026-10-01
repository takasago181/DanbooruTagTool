# Issue #223 — Copyright HOME → Browse Group → Character

Implementation base: live main `84a4ac467cc534d44f322d02989f23d12933974f`.
Branch: `dev/issue223-browse-groups`. Production apply and main merge require final review.

## Census and selection

`HOME_CENSUS_V1.csv` ranks all 7,616 Copyright roots, including zero-member roots.
3,342 roots have an EffectiveBrowseHome member; 32,942 Characters have a HOME;
2,336 remain unresolved. Census uses only the frozen #216 HOME projection.
It never uses #70 co-occurrence relationships as ownership or membership evidence.

Largest roots: Pokémon 1,878; Fate 1,286; Kantai Collection 808; Azur Lane 798;
Arknights 713; Fire Emblem 689; Hololive 637; Nijisanji 541; Umamusume 532;
Blue Archive 482. The complete ranking includes every HOME, not only example IPs.

Selection requires ≥100 HOME Characters, ≥2 groups with ≥3 exact members, and
≥20 grouped members. Once a HOME qualifies, smaller evidenced groups are also
retained. Size alone does not justify a new classification. Ship types, nations,
schools, VTuber generations and similar classifications without reviewed exact
membership in the selected evidence remain deferred. Small roots keep direct lists.

| HOME | HOME Characters | Groups | Grouped | Other / unclassified |
|---|---:|---:|---:|---:|
| Pokémon | 1,878 | 9 | 1,022 | 856 |
| Fate | 1,286 | 10 | 598 | 688 |
| Fire Emblem | 689 | 16 | 418 | 271 |
| Gundam | 220 | 3 | 102 | 118 |
| JoJo | 178 | 9 | 162 | 16 |
| Final Fantasy | 146 | 12 | 34 | 112 |
| Project Moon | 142 | 5 | 131 | 11 |
| **Total** | **4,539** | **64** | **2,467** | **2,072** |

Representative groups: Fate/Grand Order, stay night, EXTRA, Zero, Apocrypha;
Fire Emblem Awakening, Fates, Three Houses, Engage; Pokémon species generations
I–IX; Gundam UC, Witch from Mercury, 00; JoJo parts; Final Fantasy numbered works;
Project Moon Lobotomy Corporation, Library of Ruina, Limbus Company.

THE iDOLM@STER already has separate HOME roots for Cinderella Girls, Million Live,
SideM, Shiny Colors etc. No HOME unification was performed. Many Gundam SEED/00
characters already have a title-specific HOME, so they must not be pulled into the
umbrella Gundam list. The umbrella's 00 group has only one exactly evidenced member.
The new group layer never expands its root's population.

## Evidence and conservative review

The offline builder reuses exact canonical work qualifiers, reviewed #180/#216
work-scoped roster CSVs and #216's retained curated wiki snapshots. Additional
Gundam work rosters and the Pokémon species list are frozen under `snapshots/`.
The manifest pins every input and output SHA256. Review contract is literal
canonical Character links in explicit roster list/table rows, with work scope
validated before exact identity intersection with HOME. No fuzzy mapping or
Japanese-name-only membership. No automatic costume/base-character inheritance.

Pokémon uses only numbered base species rows. Named individuals, clones, regional
forms and other unnumbered entries remain unclassified. Fate's retained character
list explicitly states that entries are listed at their first appearance; broad
Multiple Games, crossover headings and unapproved title sections are excluded.
UC merges only local display groups for reviewed UC work rosters.

21 competing-work identities are retained in `HOLD_V1.csv` and unclassified,
including Anna, Tamamo-no-Mae, Bahamut and Dio. HOLD is an overlapping subset of
unclassified, not an additional population. Unknown or insufficient evidence has
no membership row; absence is not evidence. The input snapshots and metadata are
research/build inputs and are never rebuilt or downloaded during app startup.

Source pages used for new frozen research include the curated
[Pokémon species list](https://danbooru.donmai.us/wiki_pages/list_of_pokemon),
[Gundam 00 roster](https://danbooru.donmai.us/wiki_pages/gundam_00),
[Mobile Suit Gundam roster](https://danbooru.donmai.us/wiki_pages/mobile_suit_gundam),
[Zeta Gundam roster](https://danbooru.donmai.us/wiki_pages/zeta_gundam),
and [Witch from Mercury roster](https://danbooru.donmai.us/wiki_pages/gundam_suisei_no_majo).
Exact snapshot title/id/update time and full text are preserved with hashes.

## Contract and runtime

Definitions: `home_copyright, group_id, group_label_ja, sort_order`.
Memberships: `home_copyright, group_id, character_canonical, evidence_kind,
evidence_ref, review_status`. IDs are stable, HOME-local, and independent of label.
Only REVIEWED rows are imported. Unknown HOME/group, duplicate memberships,
cross-HOME members, conflicting definitions and empty definitions fail closed.

Optional `CatalogEntry.BrowseGroup` is a separate display metadata record.
FormalHomeCopyright, ReviewedBrowseHome and their precedence are unchanged.
The importer runs after #179 and #216 in the accepted full build; ordinary-only
builds are unaffected. Metadata is baked into catalog.db JSON. Older catalogs
without the optional property remain usable. Repeated definitions share one
runtime object. HOME and group lists are preindexed; HOME/group-scoped search
filters documents before relevance suppression so unrelated exact hits cannot
hide a valid local result. Normal startup needs no CSV/research source.

## UI

Opening a grouped Copyright shows its groups and counts first. Buttons wrap and
scroll in a bounded panel without ellipsis. Group selection opens the usage-sorted
Character list; Other/unclassified is a real disjoint view. Root search covers the
whole HOME; selected-group search covers HOME + group. The banner shows HOME →
group. All Characters, Back to groups, Back, and clear-related navigation are
explicit. Group-less HOME opens the existing direct Character list. Metadata never
inserts Prompt tags or writes HOME authority, #179 overlays, #70 source, or UserData.

## Verification and review stop

Results and portable/Windows/performance evidence are recorded in `VALIDATION.json`.
No main merge or production apply is part of this branch. No legacy/data path is
moved or deleted. Existing #180/#216/#179 work and research are retained unchanged.
