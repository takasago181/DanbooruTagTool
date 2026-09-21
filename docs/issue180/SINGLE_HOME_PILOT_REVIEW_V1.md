# Issue #180 — Single Home Pilot Review v1

Status: RESEARCH / PILOT ONLY / NO PRODUCTION APPLY

Target model:

`official Character -> HOME_COPYRIGHT (0..1)`

Pilot result: **12/12 can be represented with exactly one canonical home Copyright.**

Important design finding: for this product, the stable **canonical home IP/root Copyright** is a better parent than every title/subseries in which a Character originates or appears. A Character must not acquire extra parents from sequels, adaptations, collaborations, guest appearances, or subseries membership.

| Character | Proposed HOME_COPYRIGHT | State | Authority | Note |
|---|---|---|---|---|
| `dawn_(pokemon)` | `pokemon` | HOME_CONFIRMED | QUALIFIER_COPYRIGHT + official Pokémon character page | Hikari/Dawn is a Pokémon character. Do not create additional homes for individual games/anime appearances. |
| `pikachu` | `pokemon` | HOME_CONFIRMED | official Pokémon Pokédex | Franchise-root home is stable across many game/anime appearances. |
| `lapras` | `pokemon` | HOME_CONFIRMED | official Pokémon site | Species appears across many titles; one Pokémon home avoids title-by-title duplication. |
| `hatsune_miku` | `vocaloid` | HOME_CONFIRMED | official Piapro Characters page + catalog fallback-root policy | Official source identifies Hatsune Miku as a Crypton virtual-singer software character. No `piapro_characters` Copyright was found in the repository catalog search, so `vocaloid` is the current in-catalog stable root. Keep this provenance explicit. |
| `kaito_(vocaloid)` | `vocaloid` | HOME_CONFIRMED | QUALIFIER_COPYRIGHT + official Piapro Characters page | Same in-catalog root policy as Hatsune Miku. |
| `ikazuchi_(kancolle)` | `kantai_collection` | HOME_CONFIRMED | QUALIFIER_COPYRIGHT | Explicit `kancolle` qualifier resolves to the canonical Kantai Collection Copyright. |
| `inazuma_(kancolle)` | `kantai_collection` | HOME_CONFIRMED | QUALIFIER_COPYRIGHT | Explicit `kancolle` qualifier resolves to the canonical Kantai Collection Copyright. |
| `shimakaze_(kancolle)` | `kantai_collection` | HOME_CONFIRMED | QUALIFIER_COPYRIGHT + official DMM Kantai Collection page | Official DMM page explicitly presents Shimakaze as a Kanmusu. |
| `gotoh_hitori` | `bocchi_the_rock!` | HOME_CONFIRMED | official Bocchi the Rock! character page | Character is explicitly listed by the work's official site. |
| `shirakami_fubuki` | `hololive` | HOME_CONFIRMED | official hololive talent roster/profile | Unit memberships such as 1st Generation/GAMERS are not additional Copyright homes. |
| `irys_(hololive)` | `hololive` | HOME_CONFIRMED | QUALIFIER_COPYRIGHT + official hololive talent profile | Promise/Project: HOPE-style unit history is not an additional home. |
| `gawr_gura` | `hololive` | HOME_CONFIRMED | official hololive talent/alumni profile | hololive English/Myth is a subgroup, not a second product home. Alumni status does not change origin ownership. |

## Evidence URLs

- Pokémon Pokédex — Pikachu: https://zukan.pokemon.co.jp/detail/0025
- Pokémon official — Lapras: https://www.pokemon.co.jp/ex/sun_moon/pokemon/160826_01.html
- Pokémon official — Hikari/Kouki: https://www.pokemon.co.jp/ex/bdsp/ja/character/210818_03/
- Piapro Characters: https://piapro.net/pages/character
- Kantai Collection official DMM page: https://www.dmm.com/netgame/feature/kancolle.html
- Bocchi the Rock! official character page: https://bocchi.rocks/tv/character/
- hololive official talents: https://hololive.hololivepro.com/talents
- Shirakami Fubuki: https://hololive.hololivepro.com/talents/shirakami-fubuki/
- IRyS: https://hololive.hololivepro.com/talents/irys/
- Gawr Gura: https://hololive.hololivepro.com/talents/gawr-gura/

## Pilot acceptance finding

The 0..1 relation model is viable for these five ecosystems.

However, the earlier wording "prefer the most specific origin Copyright" is too narrow for the user's intended product. The next #180 schema revision should instead prefer one **canonical home/root IP** suitable for stable Character browsing, while preserving more-specific title/subseries information only as evidence or secondary metadata, never as additional home ownership.

No production/runtime/source data was changed by this review.
