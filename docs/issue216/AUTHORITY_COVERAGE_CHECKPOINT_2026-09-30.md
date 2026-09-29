# Issue #216 — full-cohort authority coverage checkpoint

## 2026-09-30 source-driven continuation

- Source-first execution remains active; the queue was deterministically rebuilt from the frozen #180 master, structure graph, and post-count source. Candidate roots and post counts remain priority metadata only.
- Reviewed the official The Idolmaster Million Live! anime site's distinct `MILLIONSTARS` directory once as a 39-name batch, excluding adjacent 765PRO and staff sections. Exact roster matching found one unresolved cohort identity: `julia_(idolmaster)`. Its exact `ジュリア` name and the page's explicit `MILLIONSTARS` section were manually disambiguated from the separate Cowboy Bebop `julia` identity. Added one source-scoped mapping to `idolmaster_million_live!`; all other matched catalog identities were already outside the frozen unresolved cohort.
- Current cohort: 13,983 accounted; HOME_CONFIRMED 265; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 1; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,714. Terminalized 269 (1.92%); Top500 UNRESEARCHED 366; Top2000 UNRESEARCHED 1,821.
- Current sources: 34 registry rows; 268 exact member mappings (269 member rows including one ambiguous identity-review mapping); 243 reused member rows / 269 total member rows = 90.33% source reuse; 268 exact mappings / 34 reviewed source records = 7.88 mappings per source. This turn's reviewed source yielded 1 terminalized Character / 1 new source review.
- Missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflicting decisions 0. Source-driven queue: 2,668 roots; all 13,714 open rows represented. Candidate root `idolmaster` now has 119 open rows (Top500 7, Top2000 23); `limbus_company` has 51 (Top500 0, Top2000 3). Candidate-root hints were not used as HOME evidence.
- Validation: full #216 focused suite PASS (16 tests; rerun with normal filesystem permissions after sandbox ACL fixture errors); deterministic source-yield queue PASS; 8,536-root Copyright catalog reproducibility PASS; `git diff --check` PASS. No #180 baseline master, production data, or production runtime was changed.

## Baseline and current coverage

- Issue #180 authority commit: `9c0db59c0f1dc56402c955e718a37d9de1849d7e`.
- Frozen master SHA-256: `135463a5225b6501db923322284f8e309f217eb5359538088eb6de6d78b77071`.
- Baseline population: 35,890; HOME_CONFIRMED 21,907; HOME_UNRESOLVED 13,983.
- Frozen unresolved cohort: 13,983 / 13,983 accounted; cohort ID-list SHA-256 `2db82cd3640196a29015124f28ca75f849c5469ba8dede8f2bb0396c6ecf8f31`.
- Current states: HOME_CONFIRMED 264; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 1; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,715. Accounted/terminalized: 268 / 13,983 (1.92%).
- Frozen Top500: 366 UNRESEARCHED; frozen Top2000: 1,822 UNRESEARCHED. Top500 calibration remains incomplete.
- Additive HOME_CONFIRMED total: 22,171 / 35,890 (61.77%). The original #180 master remains byte-identical; baseline-confirmed rows are outside this cohort and unchanged.
- HOME cardinality: at most one field/value per decision; missing references to the complete Issue #70 Copyright catalog: 0.
- Copyright source registry: 33 records; exact member mappings: 267; source reuse ratio: 243/268 (90.67%, including one ambiguous research mapping in the member denominator); reusable accepted source records: 8. This turn added 200 roster HOME decisions (195 Idolmaster members, five additional Limbus Company Sinners), two policy terminals and one identity terminal. Source efficiency: 203 terminalized Characters / 7 new source reviews = 29.0 per source review.
- Full-cohort root-priority queue: 2,668 candidate roots, reconstructed from the frozen cohort and read-only Issue #180 master/graph. Current Top500/Top2000 open counts are based on frozen ranks. Expected safe yield is a priority estimate only; candidate roots, queue rank and post counts remain non-evidence.

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

Five 765PRO ALLSTARS members (Iori Minase, Hibiki Ganaha, Yayoi Takatsuki, Yukiho Hagiwara, and Azusa Miura) are listed by exact Japanese name under the official Million Live anime site's `765PRO ALLSTARS` directory section. The existing Issue #180 official-idol-directory normalization supports the single `idolmaster` root; the batch does not use the event/live source or candidate-root hints as HOME evidence. See `BATCH_765PRO_ROSTER_2026-09-30.csv`.

Three additional Top100 members were mapped from first-party sources: Mai Shiranui from SNK's Fatal Fury title archive to the established `fatal_fury` root; Reisalin Stout from Koei Tecmo's Atelier Ryza character directory to `atelier_(series)` under existing #180 series-root decisions; and Kana Arima from the Oshi no Ko official character profile to `oshi_no_ko`. Exact Japanese names, source scopes, claims, and normalizations are recorded in `BATCH_TOP100_CHARACTER_PROFILES_2026-09-30.csv`.

Hoto Cocoa was confirmed from the official GochiUsa Cocoa character profile. An independent Japanese character-name listing corroborates that the official profile's Cocoa is 保登心愛, solely as exact identity mapping evidence; it is not HOME authority. See `BATCH_GOCHIUSA_COCOA_PROFILE_2026-09-30.csv`.

Amate Yuzuriha, Yoshida Yuuko, and Shirogane Naoto were confirmed from their official GQuuuuuuX, Machikado Mazoku, and Persona 4 profiles respectively. Amate's specific `gundam_gquuuuuux` root was selected from the named official work; the broad `gundam` candidate hint was not used. Persona 4 was normalized through the existing Issue #180 `persona` root authority. See `BATCH_TOP100_OFFICIAL_PROFILES_2026-09-30.csv`.

Super Sonico was researched through the official biography and terminalized as `POLICY_BLOCKED`: the official page establishes an event-mascot origin and a broad cross-product career, while the #180 single-HOME policy does not permit promoting an event or company tag alone to fictional HOME. No HOME was assigned. See `BATCH_SUPER_SONICO_POLICY_REVIEW_2026-09-30.csv`.

The source-driven execution layer now includes a deterministic full-cohort `SOURCE_YIELD_QUEUE_V1.csv/.json`, exact normalized roster-to-catalog candidate generation, ambiguity/no-match statuses, and reviewed batch compilation. Re-auditing already registered official rosters yielded 195 exact Idolmaster identities in two batch applications without per-Character page lookups. An additional five Limbus Company Sinners were confirmed from the already reviewed first-party Sinner Owner's Manual; the prior seven-member source scope remains unchanged, and the 12-name scope is registered separately at the same URL. The official page names the complete Sinner roster, but only five previously unresolved cohort members were newly mapped in this batch. See `BATCH_LIMBUS_SINNER_OWNER_MANUAL_SCOPE_REUSE_2026-09-30.csv`.

The official Hololive talent directory was reviewed as one 81-name source batch. Exact catalog matching produced no safely unique unresolved cohort identity; 63 names required review due to catalog search surfaces or multiple variants, 16 had no safe catalog match, and two mapped outside the frozen cohort. The sole unresolved cohort alias collision, `yorick_(shiori_novella)`, is now `IDENTITY_BLOCKED`: the directory proves Shiori Novella is a talent but does not prove the catalog's Yorick identity is that same Character. No HOME was assigned. Proposal, roster, candidate and terminal batch records are preserved in the `SOURCE_*_HOLOLIVE_DIRECTORY_2026-09-30` and `BATCH_HOLOLIVE_DIRECTORY_IDENTITY_BLOCK_2026-09-30.csv` files. The #180 confirmed base roster did not provide a validated variant path for any additional unresolved Hololive cohort row, so no inheritance was applied.

The terminal-state path was also exercised for Kasane Teto and Yuzuki Yukari after reviewing their official cross-product voice lineups. Both are `POLICY_BLOCKED` under the current single-HOME rule; no HOME or source-member mapping was added for them. The unresolved cohort is now 13,716, and no state was assigned from candidate-root, popularity, co-occurrence or absence from a partial source.

## Validation

- Full cohort freeze/reconstruction from exact #180 master: PASS (13,983 rows).
- Complete Issue #70 Copyright catalog reconstruction: PASS (8,536 roots; 92,739 source rows; exact source SHA in manifest).
- Top500 first-party source revalidation: PASS (19 exact members / 13 sources).
- Idolmaster roster batch deterministic check: PASS (17 exact members; two additional sources).
- Love Live! roster batch deterministic check: PASS (12 exact members; two additional sources).
- Fate character-profile batch deterministic check: PASS (3 exact members; two additional sources).
- GochiUsa profile batch deterministic check: PASS (one exact member; one additional source).
- 765PRO ALLSTARS roster batch deterministic check: PASS (five exact members; one official source).
- Top100 character-profile batch deterministic check: PASS (three exact members; three official sources).
- GochiUsa Cocoa profile batch deterministic check: PASS (one exact member; one official source; independent mapping reference recorded).
- Top100 official-profile batch deterministic check: PASS (three exact members; three official sources).
- Super Sonico terminal research batch deterministic check: PASS (one policy-blocked result; no HOME root assigned).
- Existing-source Idolmaster reuse batches deterministic check: PASS (195 exact members).
- Limbus 12-name roster scope extension batch deterministic check: PASS (five new exact members; prior seven-member scope preserved; evidence-only correction preserved the same HOME and source identity).
- Hololive directory identity-terminal batch deterministic check: PASS (one `IDENTITY_BLOCKED`, no HOME).
- Source-yield queue deterministic reconstruction: PASS (2,668 roots; Top500 open 366; Top2000 open 1,822).
- Authority coverage validator: structurally valid; reports `complete: false`, `UNRESEARCHED=13,715`.
- Issue #216 focused tests: 16 PASS.
- Full frozen Top500 cohort rebuild could not be checked from this worktree because its script hardcodes the absent local master path; the full 13,983 unresolved cohort was independently reconstructed using the explicit read-only master path and passed.
- `git diff --check`: PASS.
- CI: not run; the GochiUsa Cocoa, Top100 profile, and policy-terminal batches are pending commit/push.

## Next work

Continue by source-yield order: resolve the remaining exact members available from registered source scopes, then discover/review high-density official directories and rosters as Copyright-root batches. Treat Top500 and Top2000 completion as cross-checks of those batches rather than sequential Character work. Send ambiguous, policy-ineligible or insufficient-evidence results to an explicit valid terminal state only after authority review; otherwise leave them `UNRESEARCHED`. Continue through all 13,983 cohort rows to zero UNRESEARCHED. No main merge, production apply, Picker implementation, or mutation of the #180 master is authorized by this research checkpoint.
