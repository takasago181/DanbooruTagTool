# Issue #216 — full-cohort authority coverage checkpoint

## Baseline and current coverage

- Issue #180 authority commit: `9c0db59c0f1dc56402c955e718a37d9de1849d7e`.
- Frozen master SHA-256: `135463a5225b6501db923322284f8e309f217eb5359538088eb6de6d78b77071`.
- Baseline population: 35,890; HOME_CONFIRMED 21,907; HOME_UNRESOLVED 13,983.
- Frozen unresolved cohort: 13,983 / 13,983 accounted; cohort ID-list SHA-256 `2db82cd3640196a29015124f28ca75f849c5469ba8dede8f2bb0396c6ecf8f31`.
- Current states: HOME_CONFIRMED 52; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 0; IDENTITY_BLOCKED 0; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,931.
- Stage A Top500: 52 HOME_CONFIRMED, 448 UNRESEARCHED. Calibration Gate is **not passed**.
- Additive HOME_CONFIRMED total: 21,959 / 35,890 (61.18%). The original #180 master remains byte-identical; baseline-confirmed rows are outside this cohort and unchanged.
- HOME cardinality: at most one field/value per decision; missing references to the complete Issue #70 Copyright catalog: 0.
- Copyright source registry: 20 official sources; exact member mappings: 52; source reuse ratio: 38/52 (73.08%), with exact rosters reused across seven Limbus Company members, 15 Cinderella Girls idols, two Shiny Colors members, eight Hasunosora members, and four Aqours members.

## Revalidated members

- `neon_genesis_evangelion` — Souryuu Asuka Langley.
- `sousou_no_frieren` — Frieren.
- `spy_x_family` — Yor Briar.
- `bang_dream!` — Wakaba Mutsumi, Misumi Uika, Yahata Umiri. Ave Mujica subwork -> BanG Dream root follows the explicit existing #180 normalization.
- `metroid` — Samus Aran.
- `limbus_company` — Don Quixote, Ishmael, Faust, Hong Lu, Sinclair, Ryōshū, Yi Sang. Each was explicitly mapped from the official Sinner Owner's Manual; `project_moon` remains an identity/candidate hint, not the HOME.
- `resident_evil` — Leon S. Kennedy, Ada Wong.
- `spice_and_wolf` — Holo.
- `urusei_yatsura` — Lum.
- `persona` — Aigis. The official Persona 3 Reload profile was normalized to the stable Persona series root.

The first 19 were rechecked against first-party pages/manuals for exact identity, source scope, and one canonical root. Proposed roots were checked against the complete Issue #70 Copyright catalog and the Issue #180 root policy. Each source/member mapping and claim is recorded in `COPYRIGHT_AUTHORITY_REGISTRY_V1.csv`, `AUTHORITY_SOURCE_MEMBERS_V1.csv`, and `AUTHORITY_COVERAGE_DECISIONS_V1.csv`. The original Top500 proposal ledger remains unmodified.

An additional 17 Top500 members were verified against two official Bandai Namco rosters and recorded in `BATCH_IDOLMASTER_ROSTERS_2026-09-30.csv`: 15 Cinderella Girls idols map to `idolmaster_cinderella_girls`, and Higuchi Madoka and Mayuzumi Fuyuko map to `idolmaster_shiny_colors`. The official roster title and exact listed name establish the subseries and member mapping; the shared `idolmaster` candidate hint did not determine HOME. The batch is reproducible with `apply_reviewed_roster_batch.py`.

An additional 12 Top500 members were verified against two official Love Live! project rosters and recorded in `BATCH_LOVE_LIVE_ROSTERS_2026-09-30.csv`: eight Hasunosora members map to `love_live!_hasu_no_sora_jogakuin_school_idol_club`, and four Aqours members map to `love_live!_sunshine!!`. Each mapping records the exact Japanese roster form and its canonical Character identity.

Three more exact profiles are recorded in `BATCH_FATE_CHARACTER_PROFILES_2026-09-30.csv`: Illyasviel from the official Fate/stay night profile is normalized through the exact Issue #180 policy pair to `fate_(series)`; Miyu and Chloe are listed by the official Prisma Illya Drei profiles and map to the exact `fate/kaleid_liner_prisma_illya` Copyright root.

Kafuu Chino's full Japanese name was confirmed on the official Is the Order a Rabbit series site and mapped to `gochuumon_wa_usagi_desu_ka?`; the source record is in `BATCH_GOCHIUSA_PROFILE_2026-09-30.csv`.

## Validation

- Full cohort freeze/reconstruction from exact #180 master: PASS (13,983 rows).
- Complete Issue #70 Copyright catalog reconstruction: PASS (8,536 roots; 92,739 source rows; exact source SHA in manifest).
- Top500 first-party source revalidation: PASS (19 exact members / 13 sources).
- Idolmaster roster batch deterministic check: PASS (17 exact members; two additional sources).
- Love Live! roster batch deterministic check: PASS (12 exact members; two additional sources).
- Fate character-profile batch deterministic check: PASS (3 exact members; two additional sources).
- GochiUsa profile batch deterministic check: PASS (one exact member; one additional source).
- Authority coverage validator: structurally valid; reports `complete: false`, `UNRESEARCHED=13,931`.
- Issue #216 tests: 13 PASS.
- `git diff --check`: PASS.
- CI: not run; current GochiUsa profile addition is pending commit/push.

## Next work

Continue Stage A over every remaining member in ranks 1–500, reusing reviewed official sources only for exact mappings. Then continue by post-count priority through rank 2,000 and by Copyright-root batches across the remaining frozen cohort. Keep partial/ambiguous members open until they receive a safe terminal reason. No main merge, production apply, Picker implementation, or mutation of the #180 master is authorized by this research checkpoint.
