# 2026-09-30 Source-driven checkpoint — FFVIII, Hasunosora Edel Note, FFXIII

- Completed three official source reviews as three root-scoped batches: Square Enix FFVIII Remastered directory (8 exact mappings to `final_fantasy_viii`), the official Hasunosora Edel Note/unit-split artist credits (2 exact mappings to `love_live!_hasu_no_sora_jogakuin_school_idol_club`), and Square Enix’s FINAL FANTASY XIII title page (7 exact mappings to `final_fantasy_xiii`). These source scopes do not extend to other franchise works or unlisted characters.
- FFXIII's `Lightning` was held at `REVIEW_REQUIRED` by the generator. Manual review accepted only `lightning_farron` because the official XIII page and catalog's unique title-qualified `lightning (ff13)` alias agree. `lightning_farron_(modern_jacket)` remains UNRESEARCHED; no variant inheritance was inferred. `Galenth Dysley` returned NO_MATCH and received no cohort decision.
- Frozen cohort 13,983; terminalized 532 (3.80%); HOME_CONFIRMED 499; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 18; POLICY_BLOCKED 6; IDENTITY_BLOCKED 8; EVIDENCE_CONFLICT 1; UNRESEARCHED 13,451. Direct join to the frozen Top500 ledger shows 311 still UNRESEARCHED. The last cached Top2000 value was 1,734; this value and root-level queue totals are stale and have not been presented as current.
- Registry: 91 sources, including 45 accepted reusable roster sources; 533 source-member rows and 523 unique cohort mappings; 482 rows belong to multi-member sources (90.43% of source-member rows). This checkpoint terminalized 17 Characters across 3 new source reviews = **5.67 terminalized per new source review**. Since the preceding `e939464b` checkpoint, cumulative work is 37 terminalized across 9 new source reviews = **4.11 per source review**.
- Missing Copyright roots: 0. Existing #180 confirmed HOME changes: 0. Candidate-root hints, popularity, co-occurrence, and RelatedCopyright were not used as HOME evidence.
- Per-source schema/scope/cardinality/root/immutable-HOME validators passed for all three batches. Focused Issue #216 tests passed 18/18 after the third batch; `git diff --check` passed. Full #180 regression, deterministic queue rebuild, final reproducibility and CI remain outstanding.
- Queue global unresolved, Top500 and source-registry summary counts were refreshed from current ledgers. The frozen #180 master and hint graph are absent from this checkout; root-level counts, Top2000/post-count joins, and queue ordering remain explicitly cached until those exact frozen inputs are available. The local post-count file alone is not used as a substitute.

# 2026-09-30 Meitantei Precure official cast batch

- Reviewed Toei/ABC’s current [Meitantei Precure official cast block](https://www.toei-anim.co.jp/tv/precure/about/) once, scoped to its four Cure/name pairs. The exact name `明智あんな` yielded one unique catalog candidate; the other three names each matched a base/civilian catalog pair and were manually reviewed against the official Cure/name pair. All seven cohort identities (`akechi_anna`, `kobayashi_mikuru`, `kobayashi_mikuru_(civilian)`, `howa_kurea`, `howa_kurea_(civilian)`, `moria_luluka`, `moria_luluka_(civilian)`) were assigned directly to the existing title-specific `meitantei_precure!` root. No `VARIANT_OF` inheritance was inferred or added; each tag has direct title roster provenance. No unlisted roster member was included.
- Since the prior checkpoint, 20 Characters were terminalized across 6 source reviews = **3.33 terminalized per source review**. This includes four safe-yield series rosters plus hololive and Danganronpa V3 reviews that returned zero eligible cohort matches. Broad `precure` family hints and post counts did not select HOME.
- Frozen cohort: 13,983; terminalized 515 (3.68%); HOME_CONFIRMED 482; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 18; POLICY_BLOCKED 6; IDENTITY_BLOCKED 8; EVIDENCE_CONFLICT 1; UNRESEARCHED 13,468. Top500 UNRESEARCHED is **316**; `moria_luluka` (rank 143) was the one Top500 member in this batch. Top2000 and post-count queue projections remain stale pending protected #180 inputs.
- Registry: 88 sources; 506 unique exact member mappings across 516 source-member rows; 465 rows belong to multi-member sources (90.12%). Missing roots 0; existing #180 confirmed HOME changed 0; conflict count 1, unchanged. Queue rows: broad `precure` 88 open / 4 Top500; `meitantei_precure!` 2 open / 0 Top500. Its Top2000/post-count fields remain stale.
- Candidate-generation and manual-review ledgers, exact roster, batch, and registry proposal are retained. Per-source validator, focused Issue #216 suite, root consistency check, and `git diff --check` PASS. Full queue reconstruction, full #180 regression, reproducibility, CI, and final clean-tree/push gate remain outstanding.

# 2026-09-30 HappinessCharge + Healin Good Precure source batches

- Reviewed Toei/ABC’s official [HappinessCharge Precure Character/Cast directory](https://lineup.toei-anim.co.jp/ja/tv/happinesscharge_precure/character/) once and accepted three unique exact cohort names (`shirayuki_hime`, `oomori_yuuko`, `gurasan_(precure)`) to `happinesscharge_precure!`. `megumi_aiino` and `cure_fortune` were outside the frozen unresolved cohort. The `リボン` candidate was not accepted: the only exact catalog row carries the conflicting canonical qualifier `ribbon_(kirby)`, so the unresolved identity remains `REVIEW_REQUIRED` and UNRESEARCHED. Raw generator output and the review override are retained separately.
- Reviewed Toei/ABC’s official [Healin Good Precure cast block](https://www.toei-anim.co.jp/tv/healingood_precure/info/) once. Seven exact unique matches (`hanadera_nodoka`, `sawaizumi_chiyu`, `hiramitsu_hinata`, `fuurin_asumi`, `rabirin_(precure)`, `pegitan_(precure)`, `nyatoran_(precure)`) were accepted to the existing `healin'_good_precure` root. The listed `ラテ` had no exact safe catalog match and was not mapped.
- Since the prior checkpoint, HappinessCharge and Healin Good terminalized 10 members across 2 new source reviews. Including the Mahou Tsukai batch and zero-yield hololive/Danganronpa directory audits: 13 terminalized / 5 new source reviews = **2.60 terminalized per source review**. Exact series roots only; broad `precure` hint and post counts did not select HOME.
- Frozen cohort 13,983; terminalized 508 (3.63%); HOME_CONFIRMED 475; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 18; POLICY_BLOCKED 6; IDENTITY_BLOCKED 8; EVIDENCE_CONFLICT 1; UNRESEARCHED 13,475. Top500 UNRESEARCHED remains **317**. Top2000 and post-count queue aggregates remain stale pending protected #180 inputs.
- Registry 87; 499 unique exact mappings across 509 source-member rows; 458 rows belong to multi-member sources (89.98%). Missing roots 0; existing #180 confirmed HOME changed 0; conflict count 1, unchanged. Queue rows: `precure` 95 open / 5 Top500; `happinesscharge_precure!` 6 open / 0 Top500 (one review-required candidate); `healin'_good_precure` 2 open / 0 Top500. Root Top2000/post-count fields remain stale.
- Batch provenance and both no-yield root audit inventories are retained. Source batch validators, focused Issue #216 tests, complete root validation, and `git diff --check` PASS; full queue rebuild, #180 regression, reproducibility, CI, and final clean-tree/push gate remain outstanding.

# 2026-09-30 Mahou Tsukai Precure roster batch + additional root audits

- Reviewed Toei/ABC’s complete original-series [Mahou Tsukai Precure Character/Cast directory](https://lineup.toei-anim.co.jp/ja/tv/mahotsukai_precure/character/) once. Exact candidate generation and title-scope review produced 3 unique still-unresolved roster members: `asahina_mirai`, `izayoi_liko`, and `hanami_kotoha`, all assigned to the existing work-specific `mahou_girls_precure!` root. Twelve other displayed surfaces had no safe catalog match; `mofurun` was outside the frozen unresolved cohort. The separate 2025 MIRAI DAYS sequel and other Precure works were explicitly excluded.
- Also audited the official [hololive all-talents directory](https://hololive.hololivepro.com/talents) and Spike Chunsoft’s [Danganronpa V3 character directory](https://www.danganronpa.com/pages/v3/character/) as source batches. Candidate generation yielded no eligible unresolved exact identity in either scope (hololive: 69 outside cohort, 4 conflicting names outside cohort, 8 no catalog match; V3: 17 outside cohort, 1 no catalog match). Their roster/candidate/source-proposal artifacts are retained; neither broad root hint was used to terminalize unlisted or ambiguous characters.
- Since the preceding checkpoint, 3 Characters were terminalized from 3 newly reviewed directory sources = **1.00 terminalized per source review**. The 08th MS Team/AHS/Liella batch remains in the immediately preceding checkpoint. No root is claimed complete.
- Frozen cohort: 13,983; terminalized 498 (3.56%); HOME_CONFIRMED 465; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 18; POLICY_BLOCKED 6; IDENTITY_BLOCKED 8; EVIDENCE_CONFLICT 1; UNRESEARCHED 13,485. Top500 UNRESEARCHED is **317** (Asahina Mirai rank 387 was the one Top500 member in this batch). Top2000 and post-count queue aggregates remain stale pending the protected #180 frequency/hint-graph inputs.
- Registry: 85 sources; 489 unique exact member mappings (499 source-member rows); 448 rows belong to multi-member reviewed sources, 89.78%; missing roots 0; existing #180 confirmed HOME changed 0; conflict count 1, unchanged. Queue rows now reflect `precure` 105 open / 5 Top500 and `mahou_girls_precure!` 7 open / 0 Top500; their Top2000/post-count fields remain stale.
- Exact roster/candidate inventories and source proposals are retained. Per-source validation and the Issue #216 focused suite PASS; `git diff --check` PASS. Full #180 regression, full queue deterministic rebuild, reproducibility, CI, and final clean-tree/push gate remain outstanding. Hololive and Danganronpa were source-reviewed with zero safe yield; no terminal states were added for their unlisted cohort members.

# 2026-09-30 AHS VOCALOID + Love Live! Superstar!! Liella! + Gundam 08th MS Team source batches

- Reviewed AHS’s complete official VOCALOID2 roster and its miki product page, the official Liella! cast-credit roster (with a second official Superstar!! roster page as scope corroboration), and the official Gundam 08th MS Team title page once each as source batches. Exact candidate generation and review produced 2 AHS HOME decisions (`kaai_yuki`, `hiyama_kiyoteru`), one AHS `POLICY_BLOCKED` (`sf-a2_miki`, multi-engine HOME is not unique), 11 Superstar!! HOME decisions, and 4 08th MS Team HOME decisions (`shiro_amada`, `aina_saharin`, `ground_gundam`, `gundam_ez8`). The source-scope inventory’s other 08th entries had no catalog match or were outside the frozen cohort; they were not inferred. No broad `vocaloid`, `love_live!`, or `gundam` hint selected HOME.
- This source group terminalized 18 Characters / 4 newly registered authority source reviews = **4.50 terminalized per new source review**. Liella! members were assigned only to the existing title-specific `love_live!_superstar!!` root; 08th members only to `gundam_08th_ms_team`; AHS’s two single-engine members only to `vocaloid`. Candidate roots and popularity were queue hints only.
- Frozen cohort: 13,983; terminalized 495 (3.54%); HOME_CONFIRMED 462; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 18; POLICY_BLOCKED 6; IDENTITY_BLOCKED 8; EVIDENCE_CONFLICT 1; UNRESEARCHED 13,488. Top500 UNRESEARCHED remains **318**; these four 08th matches do not appear in the frozen Top500. Top2000 and post-count queue aggregates remain stale pending the protected #180 input files.
- Registry: 84 source records; 486 exact member mappings; 445 reused member records / 496 total member rows = 89.72%; missing Copyright roots 0; existing #180 confirmed HOME changed 0; existing conflict 1 remains unchanged. The `gundam` broad-hint open count is reduced from 259 to 255; Top500 remains 3. No full root is claimed complete.
- Source inventories, mapping candidates, exact batches, and registry proposals are retained alongside the existing AHS/Liella artifacts. Per-source batch validation PASS; checkpoint Issue #216 tests, deterministic decision rebuild, complete root check, and `git diff --check` run before commit. Full #180 regression, reproducibility, CI, clean working tree, and pushed final gate remain outstanding.

# 2026-09-30 AHS VOCALOID + Love Live! Superstar!! Liella! source batches

- Reviewed AHS’s complete official 2009 VOCALOID2 release roster once and generated three exact catalog candidates. `kaai_yuki` and `hiyama_kiyoteru` were confirmed to the existing `vocaloid` root. AHS’s separate miki product page confirms the same `sf-a2_miki` character identity across VOCALOID and Synthesizer V; this was terminalized `POLICY_BLOCKED` under the established multi-engine rule, with HOME blank. Two terminalized Characters across the roster/profile URLs plus the policy row is 3 / 2 source reviews = **1.50 per source review**.
- Reviewed the official Love Live! Superstar!! Liella! cast-credit section once, with its 11 exact character-role credits. The generator found 11 unique catalog identities that are all in the frozen #216 cohort (including `wien_margarete`, which the collaborator’s initial cohort estimate missed; the local frozen cohort/decision files verified it as UNRESEARCHED). All 11 were mapped to the existing work-specific root `love_live!_superstar!!`; broad `love_live!` was only a routing hint. A separate official Superstar!! roster page was used as scope corroboration. This source yielded 11 HOME decisions / 1 new source URL = **11.00 per source review**.
- Current cohort: 13,983; terminalized 491 (3.51%); HOME_CONFIRMED 458; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 18; POLICY_BLOCKED 6; IDENTITY_BLOCKED 8; EVIDENCE_CONFLICT 1; UNRESEARCHED 13,492. Top500 UNRESEARCHED is recomputed exactly at **318**. Exact Top2000 remains stale until protected frozen frequency input is available.
- Registry 83 records; 482 exact member mappings; 441 reused member rows / 492 total source-member rows = 89.63%; missing Copyright roots 0; existing #180 confirmed HOME changed 0; one existing conflict remains unresolved. `vocaloid` queue: 125 open / 9 Top500; `love_live!`: 95 open / 2 Top500. The Liella source scope is fully reviewed; five source-listed cohort rows were outside the agent’s original count, so the local 11-row exact generator output supersedes that estimate.
- Existing `idolmaster` registry scopes were also audited against the open cohort (67 open; 4 Top500, 15 Top2000): exact accepted source reuse has zero open matches, and the reviewed 765 Xbox360 roster yields zero new safe mappings because its exact cohort overlaps are already HOME_CONFIRMED. #180 leaves the broad family root unresolved, so no umbrella source normalization was inferred.
- Per-source and terminal batch validators PASS; Issue #216 focused tests are rerun at checkpoint; cohort accounting remains structurally valid/incomplete as expected; `git diff --check` PASS. Exact Top2000/post-count queue reconstruction remains pending because this checkout lacks the protected #180 frozen frequency/hint-graph input files; summary JSON marks those cached aggregates stale. Full #180 regression and CI remain final-gate work. Provenance: AHS release roster/candidate, AHS miki policy batch, and Liella 11-name roster/candidate/exact-member batch files.

# 2026-09-30 Fresh Precure + Gundam AGE / Gundam 00 source batches

- Reviewed three first-party work-scoped rosters once each: Toei Fresh Precure Staff/Cast; GUNDAM AGE title landing-page CHARACTER + MECHA sections; and Mobile Suit Gundam 00 title landing-page CHARACTER + MECHA sections. Search-indexed primary pages confirmed the named roster entries and current source scope. No broad `precure` or `gundam` hint selected HOME.
- Exact candidate generation identified four unique Fresh Precure matches and four Gundam AGE matches plus four Gundam 00 matches. Two qualified display cases (`タルト` → `tart_(precure)` and `ガンダムAGE-1 ノーマル` → `gundam_age-1`) were manually reviewed because the source/catalog display surfaces differ; the reviewed source scope resolves the identity. All other displayed roster rows with NO_MATCH, OUTSIDE_COHORT, or ambiguity stayed out of decisions. HOME roots are the existing work-specific `fresh_precure!`, `gundam_age`, and `gundam_00` catalog roots. The three rosters yielded 14 terminalized Characters / 3 newly reviewed URLs = **4.67 per source review**.
- Frozen cohort: 13,983; terminalized 477 (3.41%); HOME_CONFIRMED 445; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 18; POLICY_BLOCKED 5; IDENTITY_BLOCKED 8; EVIDENCE_CONFLICT 1; UNRESEARCHED 13,506. Top500 UNRESEARCHED 325. Top2000 exact count is pending a deterministic queue rebuild; the pre-batch cache was 1,734 and must not be read as current.
- Registry 80 sources (69 accepted); exact mapping count 468; reused member records 428 / 478 total source-member records = 89.54%; 4 terminalized Characters / new source review since the previous branch checkpoint when the two-member INTERNET Co Japanese roster is included = 16 / 4 = **4.00 per source review**. Missing Copyright roots 0; existing #180 confirmed HOME changed 0; existing conflict 1 remains unresolved. `gundam` priority row now has 259 unresolved and `precure` has 108 (6 Top500); `vocaloid` has 128 (10 Top500). No full high-yield candidate root is claimed complete.
- Candidate generation and per-roster batch validation PASS; Issue #216 focused suite PASS (18/18); complete cohort accounting is valid and incomplete as expected; Top500 was recomputed against the frozen rank file; `git diff --check` PASS. Full deterministic queue reconstruction remains blocked on the protected #180 post-count and hint-graph input files, so the queue JSON explicitly marks its Top2000/post-count projections stale rather than treating frequency as authority. Full #180 regression and CI remain final-gate work.

# 2026-09-30 INTERNET Co Japanese VOCALOID roster batch

- Reused INTERNET Co.'s existing first-party Japanese character-use guideline as one complete seven-name roster; the English version had already been reviewed for the same source family, and no per-Character page lookup was made. Generated exact mapping candidates against the current Character catalog. `神威がくぽ` uniquely auto-mapped to `kamui_gakupo`; `Lily` required manual exact context review and mapped to `lily_(vocaloid)` because the official source explicitly names the VOCALOID Lily product and catalog-qualified display. `GUMI` and `CUL` were already terminal; `花響 琴`, `kokone`, and `Chika` had no safe catalog match and were not applied.
- Added two HOME decisions to the exact existing `vocaloid` root. The guideline's cross-engine GUMI context was excluded from new HOME; no candidate hint, frequency, co-occurrence, or broad franchise inference was used. The new roster source yielded 2 terminalized Characters / 1 newly reviewed source URL = **2.00 per source review**.
- Frozen cohort: 13,983; terminalized 463 (3.31%); HOME_CONFIRMED 431; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 18; POLICY_BLOCKED 5; IDENTITY_BLOCKED 8; EVIDENCE_CONFLICT 1; UNRESEARCHED 13,520. Top500 UNRESEARCHED 327; Top2000 UNRESEARCHED 1,734.
- Registry 77; exact member mappings 454; reused member records 414 / 464 total source-member records = 89.22%; missing Copyright roots 0; existing #180 HOME changed 0; preserved evidence conflict 1. `vocaloid` remains open with 128 unresolved (Top500 10; Top2000 29); both exact members are now covered by the accepted INTERNET Co roster scope.
- Fast roster batch validation PASS; focused Issue #216 tests and `git diff --check` are run at checkpoint. Complete queue reconstruction still requires the protected #180 master/hint inputs; the queue row and summaries were incrementally updated using the exact frozen ranks/post counts. Full #180 regression and CI remain final-gate work. Provenance: `SOURCE_ROSTER_VOCALOID_INTERNET_JP_CHARACTER_GUIDELINE_2026-09-30.csv`, mapping candidates, source proposal, and `BATCH_VOCALOID_INTERNET_JP_GUIDELINE_EXACT_MEMBERS_2026-09-30.csv`.

# 2026-09-30 FFVII Rebirth appearance-only source batch

- Reopened Square Enix's first-party [FINAL FANTASY VII REBIRTH character directory](https://www.square-enix.com/ffvii/en-gb/games/rebirth/characters/) as one complete 24-entry roster. The exact English headings uniquely map four still-open cohort identities: `cissnei`, `rufus_shinra`, `tseng`, and `professor_hojo`. Each is a returning identity; this directory proves appearance in Rebirth but does not prove origin HOME or a validated Issue #180 variant path. All four were terminalized `SOURCE_RESEARCHED_NO_SAFE_EVIDENCE`, with HOME left blank. This is 4 terminalized Characters / 1 newly reviewed source = **4.00 per source review**.
- Frozen cohort 13,983; terminalized 461 (3.30%); HOME_CONFIRMED 429; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 18; POLICY_BLOCKED 5; IDENTITY_BLOCKED 8; EVIDENCE_CONFLICT 1; UNRESEARCHED 13,522. Top500 UNRESEARCHED 328; Top2000 UNRESEARCHED 1,736.
- Registry 76 sources; 452 exact member mappings; 412 reusable exact mappings / 462 total source-member records = 89.18%; missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflict 1 preserved unresolved. `final_fantasy` hint queue is 201 open (Top500 6; Top2000 43); the four reviewed identities are outside Top2000. Queue counts were incrementally decremented by their exact frozen post counts (740 total); complete deterministic queue rebuild remains pending because the protected #180 master/hint graph is absent here. The source remains nonaccepted for HOME because it proves only appearance.
- Fast terminal-batch validation PASS; Issue #216 focused suite PASS (18/18); cohort accounting structurally valid/incomplete as expected; `git diff --check` PASS. Full #180 regression and CI remain final-gate work. Provenance: `BATCH_FFVII_REBIRTH_RETURNING_APPEARANCES_NO_SAFE_HOME_2026-09-30.csv` plus the retained complete roster and mapping-candidate inventory.

# 2026-09-30 Vocaloid multi-engine policy batch

- Reviewed INTERNET Co.'s first-party [English character-use guideline](https://www.ssw.co.jp/products/vocal/english_character_guideline.html) and the official INTERNET Co. [Synthesizer V AI Otomachi Una product page](https://www3.ssw.co.jp/en/products.asp?sno=68). The guideline defines GUMI as a character name and covers VOCALOID Megpoid, A.I.VOICE GUMI, A.I.VOICE 2 GUMI, and Synthesizer V AI Megpoid. The Una page explicitly identifies Otomachi Una as a character of both Synthesizer V AI Otomachi Una and VOCALOID6 AI Otomachi Una. Exact identity mappings were retained; neither product series was selected as HOME.
- `gumi` and `otomachi_una` were terminalized `POLICY_BLOCKED` under `MULTI_ENGINE_SYNTHETIC_CHARACTER_NO_SINGLE_HOME`, matching the established #180 policy precedent for synthetic characters represented across different voice/product systems. HOME remains blank. Two Characters terminalized / two newly reviewed source URLs = **1.00 terminalized Characters per new source review**.
- Frozen cohort 13,983; terminalized 457 (3.27%); HOME_CONFIRMED 429; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 14; POLICY_BLOCKED 5; IDENTITY_BLOCKED 8; EVIDENCE_CONFLICT 1; UNRESEARCHED 13,526. Top500 UNRESEARCHED 328; Top2000 UNRESEARCHED 1,736.
- Registry 75 sources; 448 exact member mappings; 408 reused exact mappings / 458 total source-member records = 89.08%; missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflict 1 preserved unresolved. `vocaloid` remains open at 130 (Top500 11; Top2000 31). The new non-HOME sources do not count as accepted reusable HOME rosters.
- The queue counts and post-count totals were incrementally adjusted for these two exact frozen-cohort decisions. A complete source-yield queue reconstruction remains pending because the protected #180 master and hint graph are not present in this checkout. Fast terminal-batch validation PASS; Issue #216 focused tests PASS (18/18); checkpoint accounting is structurally valid/incomplete as expected; `git diff --check` PASS. Full #180 regression and CI remain final-gate work. Provenance: `BATCH_VOCALOID_MULTI_ENGINE_POLICY_2026-09-30.csv`.

# 2026-09-30 GQuuuuuuX MECHA source batch

- Reviewed the official [English GQuuuuuuX MECHA directory](https://en.gundam-official.com/gquuuuuux/mecha/) and [Japanese GQuuuuuuX MECHA directory](https://gundam-official.com/gquuuuuux/mecha/) as two whole-source inventories (46 named entries each), preserving each exact roster surface and scope. Three unique title-specific unresolved identities (`gquuuuuux`, `gfred`, `red_gundam`) were confirmed to `gundam_gquuuuuux`.
- The same English source ID was reused for eight exact legacy unit names, recorded as `SOURCE_RESEARCHED_NO_SAFE_EVIDENCE` because appearance in the GQuuuuuuX directory and no validated Issue #180 variant edge do not establish their originating HOME. The generic `Gundam` surface remained identity-ambiguous (`IDENTITY_BLOCKED`). The Japanese directory's exact シャア専用ザク mapping was also researched but did not establish origin HOME. No candidate root or appearance was used as HOME evidence.
- This batch terminalized 13 Characters / 2 reviewed source URLs = 6.50 terminalized Characters per new source review. Frozen cohort: 13,983; terminalized 455 (3.25%); HOME_CONFIRMED 429; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 14; POLICY_BLOCKED 3; IDENTITY_BLOCKED 8; EVIDENCE_CONFLICT 1; UNRESEARCHED 13,528. Top500 UNRESEARCHED 330; Top2000 UNRESEARCHED 1,738.
- Registry: 73 sources; 446 exact member mappings; 408 reused exact members / 456 total member records = 89.47%; 31 reusable accepted sources; missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflicts 1 (retained unresolved). The exact `gundam_gquuuuuux` queue root is now complete and disappears from the open queue.
- Deterministic full source-yield queue reconstruction PASS (2,665 roots; 13,528 open). Issue #216 focused tests PASS (18/18); `git diff --check` PASS. The complete-cohort validator is structurally valid and correctly reports incomplete due to 13,528 UNRESEARCHED rows. Full #180 regression, final reproducibility review and CI remain final-gate work. Batch provenance: `BATCH_GUNDAM_GQUUUUUUX_MECHA_EXACT_NEW_UNITS_2026-09-30.csv` and `BATCH_GUNDAM_GQUUUUUUX_MECHA_LEGACY_NO_SAFE_2026-09-30.csv`.

# 2026-09-30 Idolmaster cross-work authority batch

- Reviewed two first-party BNEI source groups. The official AtoZto!! portal identifies the exact Jupiter roster (天ヶ瀬 冬馬, 御手洗 翔太, 伊集院 北斗); BNEI's SideM launch release says Jupiter appeared in both THE IDOLM@STER 2 and the anime. Since those sources do not select one unique canonical HOME root, all three identities were terminalized as `SOURCE_RESEARCHED_NO_SAFE_EVIDENCE` without assigning HOME. The official [20th-anniversary Dearly Stars section](https://idolmaster-official.jp/news/01_19349) ties the exact surface 秋月 涼 to THE IDOLM@STER Dearly Stars; `akizuki_ryo` was confirmed to `idolmaster_dearly_stars`.
- This source batch terminalized 4 Characters / 2 source reviews = 2.00, including one HOME confirmation and three researched no-safe-evidence decisions. Frozen cohort: 13,983; terminalized 410 (2.93%); HOME_CONFIRMED 402; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 3; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,573.
- Registry: 61 sources; 408 exact cohort member mappings; 375 reused member rows / 410 registry member rows = 91.46%; 26 reusable accepted roster sources; missing roots 0; existing #180 confirmed HOME changed 0; conflicts 0. The broad `idolmaster` queue row now has 67 unresolved (Top500 4; Top2000 17). Ryo's frozen rank is 340, so Top500 UNRESEARCHED fell by one to 337; Top2000 remains 1,770.
- The `idolmaster` queue row was incrementally updated from the four exact decisions and frozen post-counts (sum 2,256). Full deterministic queue reconstruction remains pending because the protected #180 master/graph inputs are unavailable in this worktree; queue JSON records the incremental update. Jupiter authority/research batch, Ryo exact batch, source proposals, rosters, and candidate inventories are retained. Terminal and source batch validators, Issue #216 focused suite, and `git diff --check` are checkpoint gates; full #180 regression and CI remain final-gate work.

# 2026-09-30 Wonderful Precure main-cast source batch

- Reviewed Toei Animation's first-party [Wonderful Precure series-information page](https://www.toei-anim.co.jp/tv/wonderful_precure/info/) once. Its four explicitly named main-cast identities produced four exact, unique cohort matches: `inukai_komugi`, `inukai_iroha`, `nekoyashiki_yuki`, and `nekoyashiki_mayu`.
- Accepted all four to the title-specific root `wonderful_precure!`. The broad `precure` hint, post counts, other franchise appearances, and co-occurrence were not HOME evidence. Three are in frozen Top500 (ranks 346, 388, and 389); all four are outside Top2000. Top500 UNRESEARCHED fell by 3 to 338; Top2000 remains 1,770.
- This source yielded 4 terminalized Characters / 1 new source review = 4.00. Since the Persona 3 checkpoint, two new sources yielded 10 / 2 = 5.00. Frozen cohort: 13,983; terminalized 406 (2.91%); HOME_CONFIRMED 401; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,577.
- Registry: 59 sources; 404 exact cohort member mappings; 372 reused member rows / 406 registry member rows = 91.63%; 26 reusable accepted roster sources; missing roots 0; existing #180 confirmed HOME changed 0; conflicts 0. The broad `precure` priority row now has 121 unresolved (Top500 10; Top2000 49); no high-yield root is complete.
- The `precure` queue row was incrementally adjusted from the four exact decisions and frozen post-counts (sum 4,739). Full deterministic queue reconstruction remains pending because the protected #180 master/graph inputs are unavailable in this worktree; queue JSON records the incremental update. Source proposal, exact four-name roster, mapping candidates, and batch are retained. Batch validator, Issue #216 focused suite, and `git diff --check` are checkpoint gates; full #180 regression and CI remain final-gate work.

# 2026-09-30 Gundam SEED DESTINY source batch

- Reviewed the first-party Sunrise [SEED DESTINY character directory](https://gundam-official.com/seed/destiny/character/) once. The retained 41-entry roster generated six exact, unique, still-unresolved cohort matches (`shinn_asuka`, `rey_za_burrel`, `lunamaria_hawke`, `meyrin_hawke`, `meer_campbell`, `stellar_loussier`); eight exact identities were already terminal and 27 entries had no safe catalog/cohort match. No unmatched name was inferred.
- Accepted only those six exact title-specific character identities to `gundam_seed_destiny`. The broad `gundam` hint, post counts, shared franchise appearances, and co-occurrence were not HOME evidence. All six ranks are outside Top2000, so Top500 and Top2000 open counts remain 341 and 1,770.
- This source yielded 6 terminalized Characters / 1 new source review = 6.00. Together with the Persona 3 batch, 7 Characters / 2 source reviews = 3.50. Frozen cohort: 13,983; terminalized 402 (2.88%); HOME_CONFIRMED 397; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,581.
- Registry: 58 sources; 400 exact cohort member mappings; 368 reused member rows / 402 registry member rows = 91.54%; 25 reusable accepted roster sources; missing roots 0; existing #180 confirmed HOME changed 0; conflicts 0. The broad `gundam` priority row now has 280 unresolved (Top500 5; Top2000 42); no high-yield root is complete.
- The `gundam` queue row was incrementally adjusted from the six exact decisions and frozen post-counts (sum 2,751). Full deterministic queue reconstruction remains pending because the protected #180 master/graph inputs are unavailable in this worktree; queue JSON records the incremental update. Source proposal, 41-name roster, mapping candidates, and exact member batch are retained. Batch validator, Issue #216 focused suite, and `git diff --check` are checkpoint gates; full #180 regression and CI remain final-gate work.

# 2026-09-30 Persona 3 original official-directory batch

- Reviewed the first-party ATLUS [original Persona 3 character directory](https://persona3.jp/chara/) once, scoped to its nine named profiles. Candidate generation found one exact cohort mapping (`koromaru_(persona)` from コロマル), one qualifier-alias review (`aigis_(persona)`), seven outside-cohort names, and no other safe identity. The unnamed protagonist and entries from later editions or other Persona works were excluded.
- Accepted Koromaru to the original-work root `persona_3`; the broad `persona` hint, candidate popularity, co-occurrence, and later-edition roster surfaces were not HOME evidence. Its frozen post-count rank is 5,435, so Top500 and Top2000 counts are unchanged.
- This source yielded 1 terminalized Character / 1 new source review = 1.00. Frozen cohort: 13,983; terminalized 396 (2.83%); HOME_CONFIRMED 391; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,587. Top500 UNRESEARCHED 341; Top2000 UNRESEARCHED 1,770.
- Registry: 57 sources; 394 exact cohort member mappings; 362 reused member rows / 396 terminalized rows = 91.41%; 24 reusable accepted roster sources; missing roots 0; existing #180 confirmed HOME changed 0; conflicts 0. `persona` remains open with 77 unresolved (Top500 1; Top2000 12). No high-yield root is complete.
- The `persona` row was incrementally reduced using Koromaru's exact frozen post-count of 545. Full deterministic queue reconstruction remains pending because the protected #180 master/graph inputs are unavailable in this worktree; queue JSON records the incremental update. Source proposal, roster, mapping candidates, source-scoped registry proposal, detail-surface note, and exact member batch are retained. Per-source validation and focused Issue #216 tests are checkpoint gates; full #180 regression and CI remain final-gate work.

# 2026-09-30 Witch from Mercury full directory batch

- Reviewed the complete 50-entry [official Sunrise/MBS Witch from Mercury character directory](https://gundam-official.com/witch-from-mercury/character/) and exact NAME fields from its linked profile pages as one source/root batch. Exact candidate generation yielded two unique frozen-cohort identities: `cul` (カル) and `norea_du_noc` (ノレア・デュノク). Twenty-five exact catalog identities were outside the cohort; 23 surfaces had no safe exact catalog match. No unmatched or absent directory character was terminalized.
- Accepted both unique members to the title-specific canonical root `gundam_suisei_no_majo`. The broad `gundam` hint and frequency counts were not HOME evidence. Both post-count ranks are outside Top2000; this batch did not change Top500 or Top2000 unresolved totals.
- This source yielded 2 terminalized Characters / 1 new source review = 2.00. Since branch checkpoint `fed1b0f`, six new official sources yielded 15 terminalized Characters / 6 reviews = 2.50. Frozen cohort: 13,983; terminalized 395 (2.83%); HOME_CONFIRMED 390; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,588. Top500 UNRESEARCHED 341; Top2000 UNRESEARCHED 1,770.
- Registry: 56 sources; 393 exact cohort member mappings; 362 reused member rows / 395 terminalized rows = 91.65%; 24 reusable accepted roster sources; missing roots 0; existing #180 confirmed HOME changed 0; conflicts 0. `gundam` remains open with 286 unresolved (Top500 5; Top2000 42); no high-yield root is complete.
- The broad `gundam` queue row was adjusted by the two exact terminal decisions and their frozen frequency records. Full deterministic queue reconstruction remains pending because the protected #180 master/graph inputs are unavailable in this worktree. Source proposal, complete roster, candidate inventory, detail-surface note, and exact member batch are retained. Per-source validation, focused Issue #216 tests, and `git diff --check` are checkpoint gates; full #180 regression and CI remain final-gate work.

# 2026-09-30 DokiDoki Precure cast batch

- Reviewed the first-party Toei Animation [DokiDoki Precure character/cast directory](https://lineup.toei.co.jp/ja/tv/dd_precure/character/) once, with scope restricted to ten exact named cast entries. Candidate generation found one unique unresolved cohort identity, `davi_(precure)` from the exact surface ダビィ. Five named cast members were outside the frozen cohort; Charles, Lance, and Ai-chan collided across Character identities and remain unmapped.
- Accepted ダビィ to the title-specific canonical root `dokidoki!_precure` based on the official work-specific directory. The broad `precure` candidate hint and post count were not HOME evidence. Davi's frequency record is rank 3,058, so this source did not reduce Top500 or Top2000 unresolved counts.
- This source yielded 1 terminalized Character / 1 new source review = 1.00. Since branch checkpoint `fed1b0f`, five new first-party sources yielded 13 terminalized Characters / 5 reviews = 2.60. Frozen cohort: 13,983; terminalized 393 (2.81%); HOME_CONFIRMED 388; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,590. Top500 UNRESEARCHED 341; Top2000 UNRESEARCHED 1,770.
- Registry: 55 source records; 391 exact cohort member mappings; 360 reused member rows / 393 terminalized rows = 91.60%; 23 reusable accepted roster sources; missing roots 0; existing #180 confirmed HOME changed 0; conflicts 0. This one-member source is recorded as non-reusable. The `dokidoki!_precure` queue row is now 6 open (Top500 0; Top2000 1 before this batch, unchanged Top2000 after the rank check); the broad `precure` row is 125 open (Top500 13; Top2000 49). No high-yield root is complete.
- The queue rows were incrementally updated from the exact terminal decision and frozen frequency record. Full source-input deterministic reconstruction remains pending because the protected #180 master/graph inputs are unavailable in this worktree. Source, roster, candidate output, and batch are retained. Batch validation, Issue #216 focused tests, and `git diff --check` are checkpoint gates; full #180 regression and CI remain final-gate work.

# 2026-09-30 Kimi to Idol Precure main-cast batch

- Reviewed the first-party [Toei Animation Kimi to Idol Precure information page](https://www.toei-anim.co.jp/tv/precure/info/) once. Its named main cast block gives five exact entries. Candidate generation used the five official Japanese civilian-name surfaces; `sakura_uta_(precure)` was the only unique unresolved cohort member. `aokaze_nana` and `shigure_kokoro` are outside the frozen cohort. Purirun and Meroron collide across two Character identities each and remain unmapped.
- Accepted the one exact member to title-specific root `kimi_to_idol_precure`, based on the official work title and roster entry. The broader `precure` hint, post counts, aliases without exact identity, and other cast members were not used as HOME evidence.
- This source yielded 1 terminalized Character / 1 new source review = 1.00. Since branch checkpoint `fed1b0f`, four new first-party sources yielded 12 terminalized Characters / 4 reviews = 3.00. Frozen cohort: 13,983; terminalized 392 (2.80%); HOME_CONFIRMED 387; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,591. Top500 UNRESEARCHED 341; Top2000 UNRESEARCHED 1,770.
- Registry: 54 source records; 390 exact cohort member mappings; 360 reused member rows / 392 terminalized rows = 91.84%; 23 reusable accepted roster sources; missing roots 0; existing #180 confirmed HOME changed 0; conflicts 0. The source has one exact cohort member, so it is retained as non-reusable for broader member application. No high-yield root is complete.
- The `precure` hint row was updated by the one terminalized member and its exact joined frequency record; root `kimi_to_idol_precure` source/member counters were updated. Full source-input deterministic queue reconstruction remains pending because the protected #180 master/graph inputs are unavailable in this worktree. The source page and exact search surfaces, candidate output, source proposal, roster, and batch are retained in adjacent artifacts. Batch validation PASS (392 exact mappings / 54 sources); Issue #216 tests PASS (16/16); `git diff --check` PASS. Full #180 regression and CI remain final-gate work.

## 2026-09-30 Persona 4 Animation source batch

- Reviewed the official [Persona 4 Animation character directory](https://www.p4a.jp/chara/) once as the eight-entry 自称特別調査隊 roster. Exact normalized matching found two unique unresolved cohort members: Amagi Yukiko and Kujikawa Rise. Five other exact names were outside the frozen cohort, and Shirogane Naoto was already terminal; none were changed.
- Both new HOME decisions use the existing #180 Persona 4 title/root authority and the stable `persona` root. No family hint, popularity, co-occurrence, or absence from the partial source was used.
- This source yielded 2 terminalized Characters / 1 new source review = 2.00. The three source batches in this checkpoint yielded 11 / 3 = 3.67 terminalized Characters per new source review. Frozen cohort: 13,983; terminalized 391 (2.80%); HOME_CONFIRMED 386; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,592. Top500 UNRESEARCHED 341; Top2000 UNRESEARCHED 1,771.
- Registry: 53 sources; 389 exact cohort member mappings; 360 reused mappings / 391 terminalized rows = 92.07%; 23 reusable accepted roster sources; missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflicts 0. The broad `persona` candidate-root row now has 78 open (Top500 1; Top2000 12), with one reviewed reusable roster source and no open exact candidates. No high-yield root is complete.
- Queue counts were incrementally updated for the two exact terminal rows from the frozen cohort and frequency records; full source-input deterministic reconstruction remains pending because the protected #180 master/graph inputs are unavailable in this worktree.
- Source, roster, mapping candidates, and batch are retained as `SOURCE_PROPOSAL_PERSONA_4_ANIMATION_INVESTIGATION_TEAM_DIRECTORY_2026-09-30.csv`, `SOURCE_ROSTER_PERSONA_4_ANIMATION_INVESTIGATION_TEAM_DIRECTORY_2026-09-30.csv`, `SOURCE_MAPPING_CANDIDATES_PERSONA_4_ANIMATION_INVESTIGATION_TEAM_DIRECTORY_2026-09-30.csv`, and `BATCH_PERSONA_4_ANIMATION_INVESTIGATION_TEAM_DIRECTORY_2026-09-30.csv`. Authority and batch validation PASS; Issue #216 focused tests were run for the same ledger checkpoint (16 PASS) and `git diff --check` PASS. Full #180 regression and CI remain for the final gate.

## 2026-09-30 Persona 4 Animation source batch

- Reviewed the official [Persona 4 Animation character directory](https://www.p4a.jp/chara/) once as the eight-entry 自称特別調査隊 roster. Exact normalized matching found two unique unresolved cohort members: Amagi Yukiko and Kujikawa Rise. Five other exact names were outside the frozen cohort, and Shirogane Naoto was already terminal; none were changed.
- Both new HOME decisions use the existing #180 Persona 4 title/root authority and the stable `persona` root. No family hint, popularity, co-occurrence, or absence from the partial source was used.
- This source yielded 2 terminalized Characters / 1 new source review = 2.00. The three source batches in this checkpoint yielded 11 / 3 = 3.67 terminalized Characters per new source review. Frozen cohort: 13,983; terminalized 391 (2.80%); HOME_CONFIRMED 386; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,592. Top500 UNRESEARCHED 341; Top2000 UNRESEARCHED 1,771.
- Registry: 53 sources; 389 exact cohort member mappings; 360 reused mappings / 391 terminalized rows = 92.07%; 23 reusable accepted roster sources; missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflicts 0. The broad `persona` candidate-root row now has 78 open (Top500 1; Top2000 12), with one reviewed reusable roster source and no open exact candidates. No high-yield root is complete.
- The `persona` queue row was incrementally updated using the exact frozen Top500 records and their post-counts. Full source-input deterministic reconstruction remains pending because the protected #180 master/graph inputs are unavailable in this worktree.
- Source, roster, mapping candidates, and batch are retained as `SOURCE_PROPOSAL_PERSONA_4_ANIMATION_INVESTIGATION_TEAM_DIRECTORY_2026-09-30.csv`, `SOURCE_ROSTER_PERSONA_4_ANIMATION_INVESTIGATION_TEAM_DIRECTORY_2026-09-30.csv`, `SOURCE_MAPPING_CANDIDATES_PERSONA_4_ANIMATION_INVESTIGATION_TEAM_DIRECTORY_2026-09-30.csv`, and `BATCH_PERSONA_4_ANIMATION_INVESTIGATION_TEAM_DIRECTORY_2026-09-30.csv`. Authority/batch validation PASS; focused Issue #216 tests PASS (16/16); `git diff --check` PASS. Full #180 regression and CI remain for the final gate.

## 2026-09-30 Persona 5 Royal source batch

- Reviewed ATLUS/SEGA's official [Persona 5 Royal character directory](https://p5r.jp/gad4.html) as one exact roster source. The page names the title and its numbered-game context, and gives nine named character entries. Exact normalized generation found eight unique unresolved cohort identities; the anonymous protagonist entry had no exact name and was excluded.
- Accepted eight exact members to the title-specific `persona_5` root under existing Issue #180 evidence for the P5 title root: `sakamoto_ryuji`, `takamaki_ann`, `kitagawa_yusuke`, `niijima_makoto`, `sakura_futaba`, `okumura_haru`, `akechi_goro`, and `yoshizawa_kasumi`. The official name モルガナ collided between `morgana_(league)` and `morgana_(persona_5)` and remains `REVIEW_REQUIRED`; no identity was selected.
- This source yielded 8 terminalized Characters / 1 newly reviewed source = 8.00 per source review. Together with the BanG Dream! source batch in this checkpoint: 9 / 2 = 4.50. Cohort: 13,983; terminalized 389 (2.78%); HOME_CONFIRMED 384; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,594. Top500 UNRESEARCHED 343; Top2000 UNRESEARCHED 1,773.
- Registry: 52 sources; 387 exact cohort member mappings; 358 reused mappings / 389 terminalized rows = 92.03%; 22 reusable accepted roster sources; missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflicts 0. The broad `persona` hint row remains open at 80 (Top500 3; Top2000 14); exact mapping did not use that broad hint as HOME evidence. No high-yield root is complete.
- The `persona` queue row was incrementally decremented for the eight exact batch members using the frozen Top500 ranks and source post-count inventory; full source-input reconstruction remains pending because the protected #180 master/graph inputs are unavailable in this worktree.
- Source, roster, mapping candidates, and batch are retained as `SOURCE_PROPOSAL_PERSONA_5_ROYAL_CHARACTER_DIRECTORY_2026-09-30.csv`, `SOURCE_ROSTER_PERSONA_5_ROYAL_CHARACTER_DIRECTORY_2026-09-30.csv`, `SOURCE_MAPPING_CANDIDATES_PERSONA_5_ROYAL_CHARACTER_DIRECTORY_2026-09-30.csv`, and `BATCH_PERSONA_5_ROYAL_CHARACTER_DIRECTORY_2026-09-30.csv`. Authority and batch validation PASS; Issue #216 tests PASS (16); `git diff --check` PASS. CI and full #180 regression remain final-gate work.

## 2026-09-30 BanG Dream! Hello, Happy World! source batch

- Reviewed the official [BanG Dream! 3rd Season Hello, Happy World! character directory](https://anime.bang-dream.com/3rd/character/hello-happy-world/) as one closed five-member source scope. Exact normalized roster-to-catalog generation produced one unique unresolved cohort match, Tsurumaki Kokoro (`tsurumaki_kokoro`); the other four page-listed identities were outside the frozen unresolved cohort and were not changed.
- The source identifies the exact series, group, and Japanese character name. #180 `AUTHORITY_POLICY_V1` A3 explicitly maps BanG Dream! work identities to the stable `bang_dream!` root. No broad root hint, popularity, co-occurrence, or roster absence was used.
- This source batch terminalized 1 Character / 1 newly reviewed source = 1.00 terminalized Characters per new source review. Frozen cohort: 13,983; terminalized 381 (2.72%); HOME_CONFIRMED 376; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,602. Top500 UNRESEARCHED 349; Top2000 UNRESEARCHED 1,781.
- Registry: 51 sources; 379 exact member mappings; 350 reused member mappings / 381 terminalized rows = 91.86%; 21 reusable accepted roster sources; missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflicts 0. The `bang_dream!` queue row is now 32 open (Top500 3; Top2000 4), with one reusable reviewed roster source and no open exact candidate. No high-yield root is complete.
- The queue was incrementally updated from the prior deterministic snapshot using the exact frozen Top500 row for `tsurumaki_kokoro` (rank 394; post_count 1,197) and the accepted source/member record. Full source-input deterministic reconstruction remains pending because the protected #180 master and graph are unavailable in this worktree.
- Source, roster, mapping candidates, and batch are retained as `SOURCE_PROPOSAL_BANG_DREAM_HELLO_HAPPY_WORLD_2026-09-30.csv`, `SOURCE_ROSTER_BANG_DREAM_HELLO_HAPPY_WORLD_2026-09-30.csv`, `SOURCE_MAPPING_CANDIDATES_BANG_DREAM_HELLO_HAPPY_WORLD_2026-09-30.csv`, and `BATCH_BANG_DREAM_HELLO_HAPPY_WORLD_2026-09-30.csv`. Issue #216 focused tests: 16/16 PASS; batch/authority validation and `git diff --check`: PASS. CI and full #180 regression remain for the final gate.

## 2026-09-30 Fate/Requiem collaboration source batch

- Reused the official [Fate/Requiem × Fate/Grand Order collaboration announcement](https://news.fate-go.jp/2020/requiem/) as a work-scoped source review. Its exact, unqualified event-limited character name 宇津見エリセ maps uniquely to unresolved `utsumi_erice`; the official collaboration title plus the existing #180 `fate/requiem` normalization supports `fate_(series)`. No variant inheritance or candidate hint was used. The separate FGO-wide timeline remains appearance-only for crossover entries, so its other unresolved candidates were not promoted.
- This source batch terminalized 1 Character / 1 newly reviewed source URL (1.00 per source review). Frozen cohort: 13,983; terminalized 380 (2.72%); HOME_CONFIRMED 375; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,603. Top500 UNRESEARCHED 350; Top2000 UNRESEARCHED 1,782.
- Registry: 50 records; 378 exact member mappings; 350 reused member rows / 380 terminalized rows = 92.11%; missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflicts 0. `fate_(series)` queue row now has 97 open (Top500 13; Top2000 38); highest-priority `fate/grand_order` remains 71 open (Top500 2; Top2000 8). No high-yield root is complete.
- The new batch was first checked for exact scope and cohort integrity; Issue #216 focused tests PASS (16), `git diff --check` PASS, and coverage/root/cardinality validation PASS. The cumulative queue counts were adjusted for this exact terminal row; full deterministic queue reconstruction against the frozen external #180 master/graph is still pending. The immutable source roster, generated mapping-candidate inventory, and reviewed batch are retained as `SOURCE_ROSTER_FGO_REQUIEM_COLLAB_EVENT_2026-09-30.csv`, `SOURCE_MAPPING_CANDIDATES_FGO_REQUIEM_COLLAB_EVENT_2026-09-30.csv`, and `BATCH_FGO_REQUIEM_UTSUMI_ERICE_2026-09-30.csv`.

# Issue #216 — full-cohort authority coverage checkpoint


## 2026-09-30 Love Live and Gakuen Idolmaster official directory review

- Reviewed the official [Square Enix Love Live member directory](https://www.jp.square-enix.com/lovelive-sifachm/member.php) once; it lists exact Japanese names under μ's, Aqours, and Saint Snow. The μ's names all match baseline-terminal Characters outside this frozen unresolved cohort. For the Sunshine scope, seven unique unresolved Characters were confirmed to the existing `love_live!_sunshine!!` root: `matsuura_kanan`, `kurosawa_dia`, `kunikida_hanamaru`, `ohara_mari`, `kurosawa_ruby`, `kazuno_sarah`, and `kazuno_leah`. Four other exact Sunshine entries were already terminal. The same page was not reviewed separately for its two exact group scopes.
- The separate [official Gakuen Idolmaster roster](https://gakuen.idolmaster-official.jp/idol/) lists thirteen idol-course students under the product title. All thirteen exact catalog identities are outside the frozen unresolved cohort, so no source record or new HOME decision was added from this page. The candidate root `gakuen_idolmaster` still has five unrelated unresolved rows; source absence does not resolve them.
- Together with the Fate/EXTRA Last Encore directory, this turn reviewed three new official source URLs, terminalized 10 Characters, and yielded 10 / 3 = 3.33 terminalized Characters per new source review. For the Love Live page alone: 7 / 1 = 7.00. Cumulative cohort: 13,983 accounted; HOME_CONFIRMED 374; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,604. Terminalized 379 / 13,983 (2.71%); Top500 UNRESEARCHED 351; Top2000 UNRESEARCHED 1,783.
- Registry: 49 accepted/research source records; 377 exact member mappings; 350 reused member rows / 379 terminalized rows = 92.35% source reuse. Missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflicts 0. Queue: 2,665 roots; broad `love_live!` remains 106 unresolved (Top500 8; Top2000 17), while the five `gakuen_idolmaster` open rows are not covered by the official directory identities reviewed here.
- Provenance: `BATCH_LOVE_LIVE_SQUARE_ENIX_SUNSHINE_DIRECTORY_2026-09-30.csv`, its reviewed Sunshine source/roster/candidate files, the μ's and combined-directory preflight candidate inventory, and `SOURCE_PROPOSAL_GAKUEN_IDOLMASTER_DIRECTORY_2026-09-30.csv` with its exact candidate inventory. The Gakuen page has no applied decision rows.


## 2026-09-30 Fate/EXTRA Last Encore directory batch

- Reviewed the official [Fate/EXTRA Last Encore character directory](https://fate-extra-lastencore.com/character/) as one 18-entry work roster. The existing #180 `fate/extra` normalization authorizes the established `fate_(series)` root. Exact normalized catalog matching produced three unique unresolved cohort members: `tohsaka_rin_(fate/extra)`, `rani_viii`, and `leonard_bistario_harway`; each was accepted from its exact Japanese directory name.
- Five entries remained `REVIEW_REQUIRED` (class labels, collisions, or context-only identity), eight had no safe exact catalog match, and two mapped outside the unresolved cohort. Gawain is already #180 `HOME_CONFIRMED` to `fate_(series)` and was left unchanged. No source absence was used to terminalize other Characters. The larger `fate_(series)` candidate root remains open with 98 unresolved (Top500 14; Top2000 39).
- This source batch terminalized 3 Characters / 1 newly reviewed directory = 3.00 per source review. Current cohort: 13,983 accounted; HOME_CONFIRMED 367; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,611. Terminalized 372 / 13,983 (2.66%); Top500 UNRESEARCHED 356; Top2000 UNRESEARCHED 1,789.
- Registry: 48 source records; 370 exact member mappings; 343 reused member rows / 372 terminalized rows = 92.20% source reuse; cumulative 372 terminalized / 48 source records = 7.75 per review. Missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflicts 0.
- Validation: roster batch replay/check PASS; full cohort reconstruction PASS (13,983); complete Copyright-root reconstruction PASS (8,536); queue reproducibility PASS (2,665 roots; 13,611 open); Issue #216 focused tests PASS (16); `git diff --check` PASS. Full #180 regression and CI remain final-gate work. Provenance: `BATCH_FATE_EXTRA_LAST_ENCORE_DIRECTORY_2026-09-30.csv`, `SOURCE_ROSTER_FATE_EXTRA_LAST_ENCORE_DIRECTORY_2026-09-30.csv`, and `SOURCE_MAPPING_CANDIDATES_FATE_EXTRA_LAST_ENCORE_DIRECTORY_2026-09-30.csv`.

## 2026-09-30 Fate/strange Fake roster batch

- Reaudited the current first-party [Fate/strange Fake character directory](https://fate-strange-fake.com/character/) as one 27-surface work roster. The source URL also has a prior #180 accepted review for Hansa/Jester; this #216 batch retains its own exact directory scope and reuses no other Character's decision.
- Five exact, unique unresolved identities were confirmed to the existing `fate_(series)` root under the explicit #180 `fate/strange_fake` normalization: `flat_escardos`, `kuruoka_tsubaki`, `lord_el-melloi_ii`, `orlando_reeve`, and `tine_chelc`. Class labels and catalog collisions remain `REVIEW_REQUIRED`; 10 unmatched surfaces, seven out-of-cohort identities, and all earlier terminal rows were not applied.
- This source review terminalized 5 Characters / 1 source = 5.00 per review. Cumulative cohort: 13,983 accounted; HOME_CONFIRMED 364; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,614. Terminalized 369 / 13,983 (2.64%); Top500 UNRESEARCHED 356; Top2000 UNRESEARCHED 1,789.
- Registry: 47 source records; 367 exact member mappings; 340 reused member rows / 369 terminalized rows = 92.14% source reuse. Missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflicts 0. Queue: 2,665 roots; `fate_(series)` has 98 unresearched identities (Top500 14; Top2000 39); `love_live!` has 106 unresolved (Top500 8; Top2000 17); 2,665 roots total.
- Validation: source batch PASS (13,983 decisions, 369 exact mappings, 47 sources); queue reproducibility PASS (2,665 roots; 13,614 open rows); frozen cohort PASS (13,983); complete root catalog PASS (8,536); Issue #216 tests PASS (16); `git diff --check` PASS. Full #180 regression and CI remain final-gate work. Batch/provenance: `BATCH_FATE_STRANGE_FAKE_DIRECTORY_2026-09-30.csv` and its source proposal, roster, candidate inventory, and retained registry proposal.

## 2026-09-30 Fate/Zero and Fate/Apocrypha root batch

- Processed two first-party root rosters: the [Fate/Zero official character directory](https://www.fate-zero.jp/characters/) (21 exact surfaces) and the [Fate/Apocrypha official character directory](https://fate-apocrypha.com/character/) (25 exact surfaces). Exact candidate generation and source-scope review accepted 11 Fate/Zero and 2 Fate/Apocrypha cohort identities; the already-authorized Issue #180 work-to-root normalizations map `fate/zero` and `fate/apocrypha` to `fate_(series)`.
- Fate/Zero decisions: `emiya_kiritsugu`, `hisau_maiya`, `irisviel_von_einzbern`, `kayneth_el-melloi_archibald`, `kotomine_risei`, `matou_kariya`, `sola-ui_nuada-re_sophia-ri`, `tohsaka_aoi`, `tohsaka_tokiomi`, `uryuu_ryuunosuke`, and `waver_velvet`. Fate/Apocrypha decisions: `fiore_forvedge_yggdmillennia` and `shishigou_kairi`.
- Class labels and colliding catalog identities remain `REVIEW_REQUIRED`; unmatched names, out-of-cohort identities, and previously terminal rows were not added. Each directory only covers its published work-specific roster.
- This root batch terminalized 13 Characters / 2 new source reviews = 6.50 per review. Cumulative cohort: 13,983 accounted; HOME_CONFIRMED 359; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,619. Terminalized 364 / 13,983 (2.60%); Top500 UNRESEARCHED 357; Top2000 UNRESEARCHED 1,790.
- Registry: 46 source records; 362 exact member mappings; 335 reused member rows / 364 terminalized rows = 92.03% source reuse. Missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflicts 0. Queue: 2,666 roots; `fate_(series)` has 104 still-unresearched identities (Top500 15; Top2000 40), and all three registered rosters with retained candidate inventories have been reviewed.
- Validation: both source batches PASS (13,983 decisions, 364 exact mappings, 46 sources); deterministic source-yield queue PASS (2,666 roots; 13,619 open); full cohort PASS (13,983); complete Copyright-root catalog PASS (8,536); Issue #216 tests PASS (16); `git diff --check` PASS. Full #180 regression, reproducibility review and CI remain final-gate work. Provenance: `BATCH_FATE_ZERO_DIRECTORY_2026-09-30.csv`, `BATCH_FATE_APOCRYPHA_DIRECTORY_2026-09-30.csv`, and the corresponding source proposal, roster and candidate files.

## 2026-09-30 Fate/stay night Realta Nua roster batch

- Reviewed the TYPE-MOON [Fate/stay night [Realta Nua] character directory](https://www.typemoon.com/products/fatevita/character/) once as a source-scoped roster. The page has 16 named/image character surfaces; exact catalog candidate generation and scope review accepted four unique unresolved cohort identities: Mitsuzuri Ayako, Matou Shinji, Ryuudou Issei, and Kuzuki Souichirou. Each maps to `fate_(series)` under the explicit Issue #180 Fate/stay night normalization policy, not from the broad `fate_(series)` candidate hint.
- Five class/title-like surfaces (Rin, Saber, Archer, Berserker, Caster) remain `REVIEW_REQUIRED`; Rider and unmatched/nickname spellings remain unaccepted; already terminal and out-of-cohort identities were not reapplied. The existing Illyasviel profile source was reaudited and confirmed to have one-member scope only.
- This batch terminalized 4 Characters from 1 new official source review (4.00 terminalized/source). Cumulative cohort: 13,983 accounted; HOME_CONFIRMED 346; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,632. Terminalized 351 / 13,983 (2.51%); Top500 UNRESEARCHED 362; Top2000 UNRESEARCHED 1,799.
- Registry: 44 source records; 349 exact member mappings; 322 reused member rows / 351 terminalized rows = 91.74% source reuse. Missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflicts 0. The rebuilt 2,667-root queue now records the Realta Nua source as reviewed with no remaining open exact candidates; the `fate_(series)` hint remains open for 115 other cohort identities, without treating that hint as HOME evidence.
- Validation: deterministic exact roster batch PASS (13,983 decisions, 351 exact mappings, 44 sources); source-yield queue rebuilt (2,667 roots; Top500 362; Top2000 1,799); coverage summary valid but correctly incomplete due to 13,632 unresearched rows. Issue #216 suite and checkpoint-level reconstruction are next. Provenance: `BATCH_FATE_STAY_NIGHT_REALTA_NUA_DIRECTORY_2026-09-30.csv` and retained source proposal/roster, mapping generator output, candidate inventory, and source-scoped registry proposal.

## 2026-09-30 Shiny Colors subunit batch

- Reaudited the already accepted Shiny Colors 2nd-season source scope; it lists 23 older roster members and does not cover the unresolved SHHis/CoMETIK members. Reviewed the official [SHHis roster](https://shinycolors.idolmaster-official.jp/idol/shhis/) and [CoMETIK roster](https://shinycolors.idolmaster-official.jp/idol/cometik/) once each. Their pages state the THE IDOLM@STER SHINY COLORS title and list five exact member surfaces in total; all five were unique unresolved cohort matches mapped to the exact `idolmaster_shiny_colors` root.
- The source batches resolved `nanakusa_nichika`, `aketa_mikoto`, `ikaruga_luca`, `suzuki_hana`, and `ikuta_haruki`. Two are in the frozen Top500 and all five are in Top2000. No `idolmaster` candidate hint was used as HOME evidence.
- Current cohort: 13,983 accounted; HOME_CONFIRMED 342; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,636. Terminalized 347 / 13,983 (2.48%); Top500 UNRESEARCHED 362; Top2000 UNRESEARCHED 1,800.
- Current source metrics: 43 source records; 345 exact member mappings; 318 reused member rows / 347 terminalized rows = 91.64% source reuse. This batch terminalized 5 Characters / 2 new official source reviews = 2.50 per reviewed source.
- Missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflicts 0. Queue: 2,667 remaining roots; broad `idolmaster` hint now has 71 unresolved (Top500 5; Top2000 17).
- Validation: both exact source batches PASS (full-cohort rows 13,983; exact mappings 347; source records 43); source-yield queue rebuild/check PASS (2,667 roots; 13,636 open rows); Issue #216 focused suite PASS (16 tests); `git diff --check` PASS. Full #180 regression and CI remain final-gate work. Batch/provenance: `BATCH_SHINY_COLORS_SHHIS_ROSTER_2026-09-30.csv`, `BATCH_SHINY_COLORS_COMETIK_ROSTER_2026-09-30.csv`, with raw and reviewed candidate inventories retained.

## 2026-09-30 SideM source batch

- Audited the full official [THE IDOLM@STER SideM anime CHARACTER directory](https://imas-sidem.com/character/) once and retained all 50 published name surfaces. Exact normalized catalog matching generated 46 unique cohort candidates; manual review accepted 43 exact identities to the specific `idolmaster_side-m` Copyright root.
- Three exact matches remain `REVIEW_REQUIRED`: Akizuki Ryo and Jupiter's Hokuto Ijuin and Shota Mitarai are also associated with earlier Idolmaster products, so this SideM directory alone does not resolve one unique HOME/origin. Three surfaces had no exact safe catalog match; one producer label matched outside the frozen cohort. No fuzzy spelling repair or root-hint inference was used.
- Current cohort: 13,983 accounted; HOME_CONFIRMED 337; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,641. Terminalized 342 / 13,983 (2.45%); Top500 UNRESEARCHED 364; Top2000 UNRESEARCHED 1,805.
- Current source metrics: 41 source records; 340 exact member mappings; 313 reused member rows / 342 terminalized rows = 91.52% source reuse. This source batch terminalized 43 Characters / 1 new source review and added 43 exact mapped identities from one official directory.
- Missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflicts 0. SideM's broad `idolmaster` hint was not treated as evidence; the official directory itself names SideM and lists each accepted identity.
- Queue: 2,667 remaining roots, rebuilt from frozen cohort and #180 master/graph; `idolmaster` remains 76 unresolved (Top500 7; Top2000 22) and the next source batch must further narrow its broad candidate hint. Expected safe yield remains priority-only.
- Validation: SideM deterministic roster batch PASS (13,983 cohort rows; 342 exact mappings; 41 sources); source-yield queue reproducibility PASS (2,667 roots; 13,641 open rows); Issue #216 focused suite PASS (16 tests); `git diff --check` PASS. Full #180 regression and CI remain final-gate work.
- Batch/provenance: `BATCH_IDOLMASTER_SIDEM_ANIME_CHARACTER_DIRECTORY_2026-09-30.csv`; raw generator output and manual `REVIEW_REQUIRED` dispositions are retained alongside it.

## 2026-09-30 KiraKira root batch

- Reconstructed the Copyright-root queue from the complete frozen cohort. `kirakira_precure_a_la_mode` had 13 unresolved Characters and is now complete (13/13); all decisions came from three first-party, work-specific Toei sources. The character/cast directory yielded nine unique unresolved identities; the official series cast page yielded the four exact Cure-form identities; a dedicated Pikario profile resolved the final member. The directory batch also safely covered `kenjou_akira` under the same explicitly named work even though its broad hint was `precure`.
- No broad `precure` hint, popularity field, co-occurrence, RelatedCopyright relation, or unvalidated variant inheritance was treated as HOME evidence. Seven already terminal cohort surfaces were not re-applied and two out-of-cohort labels were excluded.
- At KiraKira root close, the cohort had 13,983 accounted; HOME_CONFIRMED 294; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,684. Terminalized 299 / 13,983 (2.14%); Top500 UNRESEARCHED 364; Top2000 UNRESEARCHED 1,806.
- At that checkpoint, source metrics were 40 source records; 297 exact member mappings; 270 reused member rows / 299 terminalized rows = 90.30% source reuse. That root batch terminalized 14 Characters from three new reviewed sources: 4.67 terminalized Characters / new source review, with 4.67 newly mapped Characters per source.
- Missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflicts 0. Candidate generation, source scope and root completion were checked against the immutable cohort and Issue #180 root graph.
- Validation: all three source batches passed deterministic batch validation; source-yield queue rebuild/check PASS (2,667 roots; Top500 364; Top2000 1,806; UNRESEARCHED 13,684); Issue #216 focused suite PASS (16 tests); `git diff --check` PASS. Full #180 regression and CI remain final-gate work.
- Sources: [Toei KiraKira character/cast directory](https://lineup.toei-anim.co.jp/ja/tv/precure_alamode/character/), [official KiraKira series cast page](https://www.toei-anim.co.jp/tv/precure_alamode/info/), and [Toei Pikario profile](https://www.toei-anim.co.jp/tv/precure_alamode/character/chara11.php). Batch records: `BATCH_KIRAKIRA_PRECURE_DIRECTORY_2026-09-30.csv`, `BATCH_KIRAKIRA_PRECURE_CAST_2026-09-30.csv`, and `BATCH_KIRAKIRA_PIKARIO_PROFILE_2026-09-30.csv`.

## 2026-09-30 source-driven continuation

- Rebuilt the 2,668-root queue from frozen #180 inputs. Corrected `expected_safe_yield`: it now counts only open `AUTO_MAPPING_CANDIDATE` rows from a retained candidate inventory whose accepted source ID, URL, and exact scope still match. A roster elsewhere at the same root no longer implies coverage of every open Character. The queue separately marks ambiguous matches, unreviewed registered scopes, and reviewed sources with no open exact matches.
- Reused the official Million Live anime site's distinct `MILLIONSTARS` directory once as a 39-name batch, excluding adjacent 765PRO and staff sections. Exact roster matching yielded `julia_(idolmaster)`; its exact `ジュリア` name under the explicit MILLIONSTARS heading was manually disambiguated from the separate Cowboy Bebop `julia` identity. Added one source-scoped mapping to `idolmaster_million_live!`.
- Reused the official Fate/kaleid liner Prisma Illya Drei character directory as a 26-surface batch (13 Japanese and 13 English official name surfaces). Three exact unique cohort mappings were accepted: `erica_ainsworth`, `luviagelita_edelfelt`, and `bazett_fraga_mcremitz`, all normalized to the existing #216 Prisma Illya root policy. The directory's `Angelica` entry gives no surname; because the exact name collided with other catalog identities and the official context did not uniquely prove the frozen identity, `angelica_ainsworth` was terminalized `IDENTITY_BLOCKED` with HOME empty.
- Reviewed the [official Mobile Suit Gundam SEED character directory](https://gundam-official.com/seed/seed/character/) as a 38-name batch scoped only to the original SEED television series. Exact catalog matching yielded 11 unique unresolved cohort members mapped to `gundam_seed`; 26 names had no safe cohort match, and `アイシャ` collided with three Character identities, so it was not accepted. The source scope excludes SEED DESTINY, Stargazer, and other Gundam works.
- Reviewed the official [Fate/Grand Order all-years servant timeline](https://www.fate-go.jp/trajectory/servant/) as one source-driven roster. After filtering class/rank labels and one UI image label, 471 exact character surfaces were retained. Exact matching yielded eight unique cohort candidates; manual source/root review accepted only `beni-enma` to `fate/grand_order`. Seven other unique-name candidates were held for identity/origin review, including cross-work name collisions and #180 variant relations that remain unvalidated. Fifty-one additional rows require identity review; none were inferred from FGO appearance alone.
- Current cohort: 13,983 accounted; HOME_CONFIRMED 280; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,698. Terminalized 285 (2.04%); Top500 UNRESEARCHED 364; Top2000 UNRESEARCHED 1,814.
- Current sources: 37 registry rows; 283 exact member mappings; 257 reused member rows / 285 total member rows = 90.18% source reuse; 283 exact mappings / 37 reviewed source records = 7.65 mappings per source. This continuation reviewed three new roster pages and terminalized 16 Characters (15 HOME, 1 identity block): 5.33 terminalized Characters / new source review.
- Missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflicting decisions 0. The queue shows no unreviewed registered source with measured exact yield. The broad `idolmaster` candidate root remains 119 open (Top500 7, Top2000 23); `limbus_company` remains 51 open (Top500 0, Top2000 3). Root hints, popularity, and post counts remain priority metadata only.
- Validation: Issue #216 focused suite PASS (16 tests); full cohort reconstruction PASS (13,983); exact source-batch and terminal-batch checks PASS; deterministic source-yield queue PASS; Copyright catalog reproducibility PASS (8,536 roots). No #180 baseline master, production data, or production runtime was changed.

## Baseline and current coverage

- Issue #180 authority commit: `9c0db59c0f1dc56402c955e718a37d9de1849d7e`.
- Frozen master SHA-256: `135463a5225b6501db923322284f8e309f217eb5359538088eb6de6d78b77071`.
- Baseline population: 35,890; HOME_CONFIRMED 21,907; HOME_UNRESOLVED 13,983.
- Frozen unresolved cohort: 13,983 / 13,983 accounted; cohort ID-list SHA-256 `2db82cd3640196a29015124f28ca75f849c5469ba8dede8f2bb0396c6ecf8f31`.
- Current states: HOME_CONFIRMED 374; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,604. Accounted/terminalized: 379 / 13,983 (2.71%).
- Frozen Top500: 351 UNRESEARCHED; frozen Top2000: 1,783 UNRESEARCHED. Top500 calibration remains incomplete.
- Additive HOME_CONFIRMED total: 22,281 / 35,890 (62.08%). The original #180 master remains byte-identical; baseline-confirmed rows are outside this cohort and unchanged.
- HOME cardinality: at most one field/value per decision; missing references to the complete Issue #70 Copyright catalog: 0.
- Copyright source registry: 49 records; exact member mappings: 377; source reuse ratio: 350/379 = 92.35%; exact mappings per source record: 7.69. This turn reviewed three new official source URLs and terminalized 10 Characters, or 3.33 per reviewed source. Cumulative throughput: 379 terminalized Characters / 49 registry records = 7.73 per record.
- Full-cohort root-priority queue: 2,665 candidate roots, reconstructed from the frozen cohort and read-only Issue #180 master/graph. Current Top500/Top2000 open counts are based on frozen ranks. Expected safe yield is a priority estimate only; candidate roots, queue rank and post counts remain non-evidence. Missing roots 0; existing #180 HOME changed 0; conflicts 0.

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
- Source-yield queue deterministic reconstruction: PASS (2,668 roots; Top500 open 364; Top2000 open 1,814; 13,698 open cohort rows).
- FGO exact-roster batch deterministic check: PASS (one HOME mapping; seven unique exact-name candidates held for identity/origin review; FGO appearance not treated as HOME evidence for crossover/variant identities).
- Authority coverage validator: structurally valid; reports `complete: false`, `UNRESEARCHED=13,698`.
- Issue #216 focused tests: 16 PASS.
- Full frozen Top500 cohort rebuild could not be checked from this worktree because its script hardcodes the absent local master path; the full 13,983 unresolved cohort was independently reconstructed using the explicit read-only master path and passed.
- `git diff --check`: PASS.
- CI: not run; this remains a research-only branch checkpoint.

## Next work

Continue by source-yield order: resolve the remaining exact members available from registered source scopes, then discover/review high-density official directories and rosters as Copyright-root batches. Treat Top500 and Top2000 completion as cross-checks of those batches rather than sequential Character work. Send ambiguous, policy-ineligible or insufficient-evidence results to an explicit valid terminal state only after authority review; otherwise leave them `UNRESEARCHED`. Continue through all 13,983 cohort rows to zero UNRESEARCHED. No main merge, production apply, Picker implementation, or mutation of the #180 master is authorized by this research checkpoint.

# 2026-09-30 Precure title-specific official roster batches

- Reviewed two title-scoped first-party Toei Animation source surfaces under the existing broad `precure` candidate-root family: the Delicious Party Precure series-information page and the Hirogaru Sky Precure series-information/cast page. Broad `precure` was only a discovery hint; HOME uses each explicitly named show root.
- Delicious Party: the official page names nine core cast/character surfaces. Eight exact unique unresolved cohort matches were confirmed to `delicious_party_precure`; Rosemary matched outside the frozen unresolved cohort and was retained as OUTSIDE_COHORT, not added to coverage.
- Hirogaru Sky: the official cast lists five names. Three exact unique unresolved cohort matches were confirmed to `hirogaru_sky!_precure`; Sora mapped outside the unresolved cohort and Princess Elle had no safe catalog match, so neither was accepted.
- New yield: 11 terminalized cohort Characters / 2 reviewed source scopes = 5.50 terminalized Characters per new source review. HOME_CONFIRMED increased by 11. Source/member/batch inputs and generated candidate inventories are preserved as one roster batch per official page.
- Frozen cohort: 13,983; terminalized 421 (3.01%); HOME_CONFIRMED 413; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 3; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,562. Registry: 63 sources; 419 exact member mappings; 386 source-reused member rows; source reuse ratio 91.69%. Missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflicts 0.
- Top500 UNRESEARCHED remains 337; neither batch member set intersects the frozen Top500 cohort. The queue's previous Top2000 open count was 1,770, but the protected #180 ranking/graph inputs needed to recalculate per-character Top2000 membership and full candidate-root aggregates are not present in this checkout; retain that value as the last verified snapshot, not as a post-batch count. The next full queue rebuild must use the verified read-only authority inputs when available.
- Authority coverage validator: structurally valid, incomplete as expected, deterministic state counts updated in the checkpoint JSON; Issue #216 focused suite: 16/16 PASS; both source roster compile/apply checks PASS; `git diff --check` PASS. No main merge, production apply, or #180 baseline mutation.

# 2026-09-30 FINAL FANTASY XVI official character-directory batch

- Reviewed Square Enix's official FINAL FANTASY XVI character directory: https://na.finalfantasyxvi.com/characters. Its title and nine profile headings are directly scoped to FFXVI; the broad `final_fantasy` candidate hint did not determine HOME.
- Exact English display names were matched to the existing canonical Character tags by the standard exact whitespace-to-underscore slug. Seven unresolved cohort identities were uniquely accepted to `final_fantasy_xvi`: Barnabas Tharmr, Benedikta Harman, Cidolfus Telamon, Clive Rosfield, Dion Lesage, Jill Warrick, and Joshua Rosfield. Torgal and Hugo Kupka had no safe catalog match and remain unresolved.
- This source yielded 7 terminalized Characters / 1 new source review = 7.00 per source review. Clive Rosfield is frozen Top500 rank 433; Top500 UNRESEARCHED decreased to 336.
- Cohort: 13,983; terminalized 428 (3.06%); HOME_CONFIRMED 420; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 3; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,555. Registry: 64 sources; 426 exact cohort member mappings; source-reused member rows 393; reuse ratio 91.82%. Missing roots 0; existing #180 confirmed HOME changed 0; conflicts 0.
- Candidate-generator gap fixed: exact official English name surfaces now also test the corresponding existing canonical tag slug (whitespace only -> underscore). This remains exact lookup; partial/fuzzy strings do not produce candidates. Focused source-mapping tests: 3/3 PASS. Full Issue #216 suite: 17/17 PASS; FFXVI batch validator and `git diff --check` PASS.
- Top2000's last full queue snapshot was 1,770 before the previous 11 Precure decisions. This batch confirms one further Top2000 member (Clive rank 433), so 1,769 is an upper bound; the exact current Top2000 count and root/post-count aggregates remain unavailable without the protected #180 graph/ranking input.

# 2026-09-30 source preflight and Tales of Arise batch follow-up

- Gundam root source preflight: reviewed the complete official GUNDAM SEED character page (`https://gundam-official.com/seed/seed/character/`) as one 38-name source. Candidate generation found 11 already-terminal catalog identities, 26 NO_MATCH surfaces, and one REVIEW_REQUIRED surface colliding among `aisha_(last_origin)`, `aisha_(saga)`, and `aisha_landar`. There was no safe unresolved-cohort identity to add, so the proposal/roster/candidates are retained as preflight evidence and no source/member/decision was added to the accepted registry.
- Tales of Arise English title-page preflight had eight short-name surfaces and no safe catalog matches; it was not accepted. The official Japanese Tales Channel+ base-title page (`https://tales-ch.jp/titles/toarise/`) lists seven exact Japanese Character surfaces. It yielded two exact cohort mappings to `tales_of_arise`: テュオハリム → `dohalim_il_qaras` and, after explicit source-scope disambiguation of the REVIEW_REQUIRED フルル surface, フルル → `hootle_(tales)`. The catalog identity `hootle_(tales)` carries the exact title qualifier フルル(TOARISE); the competing unqualified catalog search surface belongs to a different work and is out of the source scope. The manual mapping evidence records this review.
- Since the FFXVI checkpoint, 9 cohort Characters were terminalized across 4 reviewed source scopes (FFXVI: 7, Gundam SEED: 0, Tales of Arise English preflight: 0, Tales of Arise Japanese directory: 2) = 2.25 terminalized Characters per new source review. Two sources were accepted into the main registry; the zero-yield scopes were not.
- Current cohort: 13,983; terminalized 430 (3.08%); HOME_CONFIRMED 422; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 3; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,553. Registry: 65 sources; 428 exact member mappings; 395 source-reused member rows; reuse ratio 91.86%. Missing roots 0; existing #180 confirmed HOME changed 0; conflicts 0.
- Top500 UNRESEARCHED: 336, with Clive Rosfield at frozen rank 433 confirmed. Exact Top2000 open count cannot be reconstructed without the protected per-character ranking input: the last full queue count was 1,770 before the 20 total recent decisions, of which one Top500/Top2000 row (Clive) is known. Current Top2000 open is therefore bounded at 1,750–1,769; the queue JSON retains 1,770 as the last full snapshot and records the bound.
- Full Issue #216 focused suite: 17/17 PASS. FFXVI and Tales of Arise reviewed batch validators PASS; authority coverage validator reports structurally valid/incomplete; `git diff --check` PASS. The exact-slug candidate generator regression is included. Full #180 regression, final reproducibility, CI, and final Gate remain pending.

# 2026-09-30 additional root-source preflights

- Re-audited the existing pending COVER/hololive official talent directory from one bilingual, 160-surface roster (81 English and 79 additional Japanese surfaces; duplicate AZKi and IRyS spellings were deduplicated). Exact candidate generation returned 139 OUTSIDE_COHORT, 17 NO_MATCH, and four REVIEW_REQUIRED collisions against hololive-summer outfit tags; it returned no AUTO_MAPPING_CANDIDATE. The page establishes talent membership, but none of those collisions safely identifies an unresolved cohort row or proves a validated variant inheritance path. No source/member/decision was added to the accepted registry.
- Reviewed the first-party Spike Chunsoft [New Danganronpa V3 character directory](https://www.danganronpa.com/pages/v3/sp/character/) once as an 18-entry source, explicitly excluding Monokuma and Monokumers from HOME inference because the page establishes their V3 appearance but not origin. Candidate generation returned 17 OUTSIDE_COHORT and one NO_MATCH, with zero safe unresolved cohort mappings. The source proposal and exact roster are retained as preflight evidence; the accepted registry and decisions are unchanged.
- Since the FFXVI checkpoint, the four applied/proposed source scopes (FFXVI, Gundam SEED, Tales of Arise English, Tales of Arise Japanese) plus these two additional directory reviews have terminalized 9 Characters across 6 reviewed scopes = 1.50 terminalized Characters per reviewed scope. Five were new source reviews (one already-pending Hololive source was re-audited, not counted as a new source); the accepted Tales of Arise roster and FFXVI directory account for the nine decisions. Zero-yield scopes remain outside the accepted registry.
- Current cohort remains 13,983; terminalized 430 (3.08%); HOME_CONFIRMED 422; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 3; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,553. Accepted source registry: 65; exact member mappings: 428; reused mappings: 395; source reuse ratio: 91.86%. Missing roots 0; existing #180 confirmed HOME changed 0; conflicts 0.
- Top500 UNRESEARCHED remains 336. Top2000 remains bounded at 1,750–1,769 because protected per-Character ranking input is unavailable in this checkout. Candidate-root counts remain the full-cohort priority snapshot; no absent #180 master/graph/ranking data was fabricated or replaced with popularity evidence.
- Danganronpa and bilingual Hololive candidate generation completed successfully; the full Issue #216 focused suite was rerun after these preflights and passed 17/17. No decision data changed in these preflights. Final #180 regression, deterministic full reconstruction, final reproducibility, CI, and final Gate remain pending.
- Continued the `final_fantasy` high-density source batch with Square Enix's complete 24-name [FINAL FANTASY VII REBIRTH Characters directory](https://www.square-enix.com/ffvii/en-gb/games/rebirth/characters/). Exact candidate generation produced four unique unresolved-cohort identity candidates (`cissnei`, `rufus_shinra`, `tseng`, and `professor_hojo`), ten outside-cohort names, and ten no-match names. The page establishes appearance in Rebirth but not the four returning characters' origin HOME, so all four remain unassigned and the source stays a pending preflight rather than entering the accepted registry. No existing decision changed.
- Since the FFXVI checkpoint, 9 Characters were terminalized across 6 new source reviews (FFXVI, Gundam SEED, Tales of Arise English, Tales of Arise Japanese, Danganronpa V3, and FFVII Rebirth; the Hololive source was an existing-source re-audit and is excluded) = 1.50 terminalized Characters per new source review. Two sources were accepted into the main registry; all no-yield or appearance-only source proposals remain outside it.

# 2026-09-30 source-driven queue rebuild and Yamaha VOCALOID roster batch

- Rebuilt the Copyright-root research queue from the hash-verified frozen #180 master and structure graph plus the hash-verified Issue #70 full post-count snapshot. The queue covers 2,665 roots and all 13,983 frozen cohort identities; 13,881 have joined post-count evidence, with 102 unavailable. Post counts are priority-only and are never HOME evidence.
- Recomputed exact popularity cross-checks from the frozen source: Top500 UNRESEARCHED is 334; Top2000 UNRESEARCHED is 1,748. These are outputs of root/source processing, not sequential character queues. Top500 rank-ordered processing remains calibration-only.
- Queue rows now include unresolved, Top500, Top2000, sum/max post counts, official/reusable/reviewed sources, existing exact mappings, remaining unmapped rows, exact/review-required candidate counts, and expected safe yield. Yield counts only AUTO_MAPPING_CANDIDATE rows from an accepted source with matching source ID, URL, and scope. It is a priority estimate only.
- Re-audited the accepted Yamaha VOCALOID guideline inventory. The accepted registry has canonical source ID `src-5fba3d484bc86e60f39c`; reconciled the retained roster and candidate inventory to that exact accepted source. The source lists 29 Yamaha-scoped VOCALOID characters. Only exact unique VY1 and VY2 names were accepted to the existing Issue #180 `vocaloid` root; the other roster names were not generalized to similarly named cohort Characters. VY1 and VY2 are outside Top2000. This batch terminalized 2 Characters / 1 new source review = 2.00.
- Current cohort: 13,983; terminalized 432 (3.09%); HOME_CONFIRMED 424; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 3; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,551. Accepted source registry: 66; exact member mappings: 430; reused member rows: 397; source reuse ratio: 91.90%. Missing Copyright roots: 0; existing #180 confirmed HOME changed: 0; conflicts: 0.
- The top of the newly rebuilt queue is `fate/grand_order` (71 unresolved, 2 Top500, 8 Top2000; 7 review-required candidate identities), `vocaloid` (132 unresolved, 12 Top500, 33 Top2000; registered roster fully re-audited, no remaining exact candidate), `fate_(series)` (97; 13/38), `persona` (77; 1/11), and `idolmaster` (67; 4/15). Broad roots remain priority hints and are not HOME evidence.
- No protected #180 input, production data, or confirmed HOME decision was changed. Full Issue #216 and #180 regression, deterministic reconstruction/reproducibility, CI, final Gate, and remaining source-driven cohort processing are pending.

# 2026-09-30 frozen Issue #180 conflict-path reuse

- Audited frozen #180 master reasons against its protected validated graph and evidence ledger. The 13,983-row cohort has exactly one baseline `EVIDENCE_CONFLICT`: `fu_hua_(phoenix)`. The ledger records both a validated structural variant inheritance path to `honkai_(series)` and a separately validated official battlesuit-specific `DIRECT_HOME` path to `honkai_impact_3rd`.
- Reused those two exact validated paths, their evidence IDs, source URL, and input hashes into an additive #216 evidence file and registry entries. Set the #216 state to `EVIDENCE_CONFLICT`, preserving both roots and leaving HOME empty. No #180 master, graph, ledger, existing confirmed HOME, or production data was edited.
- Added `APPROVED_REPO_EVIDENCE` as a source registry type already recognized by the validator's authority taxonomy, with a focused test proving it still requires an exact mapping, accepted root, and normal HOME validation. Issue #216 focused tests: 18/18 PASS.
- This terminalized one Character using two reused validated authority paths and zero new external source lookups; the requested terminalized-per-new-source-review ratio is therefore not applicable for this reuse-only checkpoint. It does not claim source discovery efficiency.
- Current cohort: 13,983; terminalized 433 (3.10%); HOME_CONFIRMED 424; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 3; POLICY_BLOCKED 3; IDENTITY_BLOCKED 2; EVIDENCE_CONFLICT 1; UNRESEARCHED 13,550. Accepted source registry: 68; exact member mappings: 432; reused member rows: 397; reuse ratio: 91.47%. Missing Copyright roots: 0; existing #180 confirmed HOME changed: 0; conflicts remain explicitly unresolved as HOME.
- Rebuilt the full queue: 2,665 roots; Top500 UNRESEARCHED 334; Top2000 UNRESEARCHED 1,747. Queue reproducibility PASS from the hash-verified protected inputs. Final full #180 regression, deterministic full reconstruction/reproducibility, CI, final Gate, and source-driven processing to UNRESEARCHED=0 remain pending.

# 2026-09-30 Fate/Grand Order ambiguous roster terminal batch and validated variants

- Reused the already-reviewed official FGO servant timeline as one narrow source scope for its seven open `REVIEW_REQUIRED` roster identities. Two entries (`phantas-moon`, `archetype_earth`) establish appearance but no safe original-work HOME and were terminalized as `SOURCE_RESEARCHED_NO_SAFE_EVIDENCE`. Five entries (Rance Uesugi Kenshin, Final Fantasy Vrtra, and three class/variant identities with only candidate #180 links) were terminalized as `IDENTITY_BLOCKED`. No FGO appearance was promoted to HOME.
- One existing FGO page scope review terminalized 7 Characters = 7.00 terminalized Characters per reviewed scope, with zero new external source lookups. The root queue retains 64 other open Characters under `fate/grand_order`; this source batch does not claim that root complete.
- Separately, audited every open-cohort row against the protected #180 graph for a `VALIDATED VARIANT_OF` edge whose base has one `HOME_CONFIRMED` master root and no competing validated root. Exactly two rows qualify: `cyrene_(demiurge)_(honkai:_star_rail)` inherits `honkai:_star_rail`, and `kei_(aris)_(blue_archive)` inherits `blue_archive`. Both exact evidence paths were reused as `APPROVED_REPO_EVIDENCE`; candidate-only variant links remain untouched. Both are in frozen Top500, so Top500 UNRESEARCHED fell by two.
- Current cohort: 13,983; terminalized 442 (3.16%); HOME_CONFIRMED 426; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 5; POLICY_BLOCKED 3; IDENTITY_BLOCKED 7; EVIDENCE_CONFLICT 1; UNRESEARCHED 13,541. Source registry: 71; exact member mappings: 434; source-reused member rows: 397; reuse ratio: 89.62%. The ratio includes seven explicit ambiguous/rejected member records from the FGO terminal scope. Missing Copyright roots: 0; existing #180 confirmed HOME changed: 0.
- Full rebuilt queue: 2,665 roots; Top500 UNRESEARCHED 332; Top2000 UNRESEARCHED 1,742; source-yield reproducibility PASS. Issue #216 focused tests: 18/18 PASS; `git diff --check` PASS. Final #180 regression, final deterministic reconstruction/reproducibility, CI, final Gate, and all remaining source-driven batches are pending.


## Source-driven continuation checkpoint — 2026-09-30

Continued on `codex/issue216-unresolved-coverage-7073`, preserving the frozen cohort and existing #180 HOME assignments. Three new official sources and one existing accepted source batch produced 15 exact HOME decisions: FGO THE STAGE - Solomon (Romani Archaman and the explicitly gendered male/female Fujimaru Ritsuka identities); two title-qualified Fate/Zero identities from the already accepted Fate/Zero directory; Chidori from the official Persona 3 Reload roster; and nine exact Endwalker Patch 6.0 Key Characters from the official Japanese FFXIV page. The Endwalker batch used three machine-generated exact candidates and six manually reviewed unique Japanese-name/catalog matches. The FGO raw Gilgamesh candidate was rejected because its only exact catalog match is a Final Fantasy identity. Endwalker `クルル` was not assigned because its exact collision maps to an unrelated outside-cohort Character; `光に佇む淑女` remains unmapped because the official page does not establish the canonical identity.

The source registry re-audit covered all 48 accepted reusable roster sources. Retained candidate inventories were matched on source ID, URL and exact scope. No safe unmapped exact candidate remained in those inventories; one raw FGO Gilgamesh AUTO candidate was explicitly rejected. Report: `SOURCE_REGISTRY_REAUDIT_2026-09-30.csv`.

| Measure | Current |
|---|---:|
| Frozen baseline cohort | 13,983 |
| Terminalized | 547 (3.91%) |
| HOME_CONFIRMED | 514 |
| SOURCE_RESEARCHED_NO_SAFE_EVIDENCE | 18 |
| POLICY_BLOCKED | 6 |
| IDENTITY_BLOCKED | 8 |
| EVIDENCE_CONFLICT | 1 |
| UNRESEARCHED | 13436 |
| Coverage | 3.91% |
| Source registry / accepted reusable rosters | 94 / 48 |
| Exact source-member rows / unique exact mappings | 548 / 538 |
| Reuse rows / source-member rows | 496 / 548 (90.51%) |
| Top500 / Top2000 still UNRESEARCHED | 306 / 1688 |
| Missing Copyright roots / changed existing #180 HOME / new conflicts | 0 / 0 / 0 |
| Terminalized Characters / new source reviews since prior pushed checkpoint | 15 / 3 = 5.00 |

The exact frozen #180 master and `structure_graph_v3.csv` are absent both in this checkout and the primary repository path. Per-root unresolved/Top500/Top2000/post-count values and the root priority order therefore remain cached and explicitly marked; no replacement hint graph was inferred. The hash-verified post-count snapshot permits cohort-wide Top500 and Top2000 open counts to be recomputed without treating frequency as evidence.

Validation: all four reviewed batch inputs in this continuation passed the source-batch validator; the authority coverage ledger validates; `python -m pytest tests/issue216 -q` passed 18/18; `git diff --check` passed. Existing #180 confirmed HOME changes: 0; missing roots: 0; current conflicting decisions: 1 (unchanged). This is a continuing checkpoint, not completion.


## Membership-driven continuation checkpoint — 2026-09-30

The research flow now projects only accepted exact membership evidence onto the frozen cohort. Added `MEMBERSHIP_RESEARCH_POLICY_V1.md`, deterministic membership-table generation, safe bulk-decision projection, and regressions for exact curated roster reuse, candidate-root-only rejection, competing roots, fuzzy mappings, scope leakage, deterministic output, and existing HOME preservation. The Kotori regression is in the accepted 765PRO staff directory batch: the work-level roster is enough to validate `otonashi_kotori`; its character-specific interview is no longer required by the decision. The exact Persona terminal qualifier rule already validated in #180 was reused for 11 open `_(persona)` tags; `mortis_(persona)_(bang_dream!)` was excluded because its outer qualifier conflicts. Issue #216 tests pass 25/25.

All 97 current registry records were joined back to the full cohort using accepted source/member IDs, exact URL/scope, and recorded candidate-review dispositions. The retained source inventories have 0 safe open exact candidates and 0 open review candidates. The only raw AUTO candidate in that re-audit was FGO-stage `ギルガメッシュ -> gilgamesh_(final_fantasy)`; the recorded wrong-identity rejection is honored. Roster-root audits found no newly supportable open exact members for Touhou, Project Moon/Limbus, BanG Dream, Vocaloid, or Fate. Their existing validated scopes/root policies remain available for reuse. No candidate hints were promoted to membership evidence.

| Measure | Current |
|---|---:|
| Frozen baseline cohort / accounted | 13,983 / 13,983 |
| Terminalized / coverage | 562 / 4.02% |
| HOME_CONFIRMED | 528 |
| SOURCE_RESEARCHED_NO_SAFE_EVIDENCE | 18 |
| POLICY_BLOCKED | 6 |
| IDENTITY_BLOCKED | 9 |
| EVIDENCE_CONFLICT | 1 |
| UNRESEARCHED | 13,421 |
| Membership action mix (AUTO_ACCEPT / FAST_REVIEW / DEEP_RESEARCH / terminal blocked) | 0 / 13,421 / 0 / 34 |
| Character-specific Deep Research count / rate | 0 / 0.00% |
| Source registry / accepted reusable sources | 97 / 50 |
| Exact mapped Characters / source-member rows | 553 / 564 |
| Reused member rows / reuse ratio | 510 / 564 (90.43%) |
| Mean mapped Characters per registered source | 5.70 |
| Top500 / Top2000 still UNRESEARCHED | 305 / 1,684 |
| Missing Copyright roots / changed existing #180 HOME / conflicts | 0 / 0 / 1 (the same explicit conflict) |
| New terminalized Characters / reviewed scopes since pushed-base delta | 30 / 6 = 5.00 |
| New terminalized Characters / external URL reviews | 30 / 4 = 7.50 |
| Latest exact-qualifier batch yield | 11 / 1 reused policy evidence review; 0 external URL lookups |

Top500 and Top2000 counts were recomputed from the frozen cohort and SHA-256-verified Issue #70 post-count snapshot; frequency was used only for ranking. Post counts join 13,881 cohort rows, leaving 102 rows without a count. The per-root queue remains explicitly cached because the frozen #180 master and `structure_graph_v3.csv` are unavailable in this checkout; no substitute graph or candidate-root evidence was inferred. The source reuse re-audit, deterministic membership projection, cohort validator, and `git diff --check` are checkpoint gates; the final full #180 regression, full reproducibility, CI, clean pushed branch, and `UNRESEARCHED = 0` remain pending. No #180 confirmed HOME or production data changed.


## Validated exact-root qualifier bulk checkpoint — 2026-09-30

Reused the 10 `root_review=PASS` rows in the existing Issue #180 `exact_root_semantic_authority_batch02.csv` together with the frozen Issue #180 policy A1. A deterministic exact-suffix join found 266 currently open canonical Character keys, all with the matching terminal Copyright qualifier and no earlier nested qualifier segment. This is semantic membership from the canonical tag qualifier plus an already validated normalization rule; candidate-root hints, fuzzy name matches, and character-specific searches were not used. The batch generated ten scoped `APPROVED_REPO_EVIDENCE` source entries and 266 exact member mappings. Validator accepted the entire batch; no competing accepted root, missing catalog root, or existing HOME overwrite was found.

| Measure | Current |
|---|---:|
| Frozen baseline / accounted | 13,983 / 13,983 |
| Terminalized / coverage | 828 / 5.92% |
| HOME_CONFIRMED | 794 |
| SOURCE_RESEARCHED_NO_SAFE_EVIDENCE / POLICY_BLOCKED / IDENTITY_BLOCKED / EVIDENCE_CONFLICT | 18 / 6 / 9 / 1 |
| UNRESEARCHED | 13,155 |
| AUTO_ACCEPT / FAST_REVIEW / DEEP_RESEARCH / terminal blocked | 0 / 13,155 / 0 / 34 |
| Character-specific Deep Research count / rate | 0 / 0.00% |
| Source registry / reusable accepted sources | 107 / 60 |
| Exact mapped Characters / source-member rows | 819 / 830 |
| Reused member rows / source reuse ratio | 776 / 830 (93.49%) |
| Top500 / Top2000 still UNRESEARCHED | 297 / 1,632 |
| New terminalized Characters / validated membership scopes in this batch | 266 / 10 = 26.60 |
| New external URL reviews for this batch | 0 |
| Missing roots / existing #180 HOME changes / conflicts | 0 / 0 / 1 unchanged |

The full 107-record registry was rejoined to cohort decisions and exact source scopes. A separate exact-key scan of existing accepted #180 curated Character-list files found no additional open cohort member: those roster identities are already terminal or outside the cohort. Its retained exact candidate inventories contain no open safe matches after recorded source-scope/candidate disposition. The 266 qualifiers reduce the outstanding cohort, but no precision rule was relaxed. Root-level unresolved aggregates remain cached because the frozen #180 master/structure graph are still absent; frequency-derived global Top500/Top2000 counts are recomputed separately and are not evidence. Focused tests and full cohort validation are next for this checkpoint.


## Membership reuse checkpoint — 2026-09-30

Rejoined all 111 registered sources against the full frozen cohort and their exact URL/scope candidate inventories. The prior audit projection counted only `canonical_character` and missed possible identities carried in `competing_tags`; the corrected audit finds **0 open AUTO candidates and 31 REVIEW_REQUIRED source surfaces involving 29 unresolved Characters**. The 29 exact ambiguous identities are now surfaced as `DEEP_RESEARCH`; candidate rows remain routing/review metadata and never become HOME evidence. This corrects earlier checkpoint prose that said no open review candidates remained.

Applied 11 bulk membership decisions since the pushed base: 2 FFIV DFFOO official-roster exact members and 9 exact Cure identities from Toei's series-filtered official store selector. Toei's single URL is represented by three root-bounded source scopes (Hirogaru Sky: 4, DokiDoki: 1, Kimi to Idol: 4). For those 9, exact Japanese selector surfaces uniquely match catalog display names, while existing PASS #180 evidence supplies the title-specific root policy. Eleven other store candidates remain open because their root normalization is not validated; broad `precure` inference was not used. Kotori remains grounded in the accepted 765PRO work-level roster and has no individual-interview requirement.

| Measure | Current |
|---|---:|
| Frozen cohort / accounted | 13,983 / 13,983 |
| Terminalized / coverage | 839 / 6.0001% |
| HOME_CONFIRMED / no-safe-source / policy / identity / conflict | 805 / 18 / 6 / 9 / 1 |
| UNRESEARCHED | 13144 |
| AUTO_ACCEPT / FAST_REVIEW / DEEP_RESEARCH / terminal blocked | 0 / 13115 / 29 / 34 |
| Character-specific Deep Research candidates | 29 (0.207% of cohort); no new per-character web lookups in this checkpoint |
| Source registry / reusable accepted sources | 111 / 63 |
| Exact source-member mappings / unique exact mapped Characters / source-member rows | 830 / 828 / 841 |
| Reused member rows / source reuse ratio | 786 / 841 (93.46%) |
| Characters per registered source | 7.46 |
| Open exact AUTO candidates / ambiguous REVIEW_REQUIRED surfaces | 0 / 31 (29 distinct open Characters) |
| Top500 / Top2000 still UNRESEARCHED | 297 / 1626 |
| New terminalized / external URL reviews | 11 / 2 = 5.50 |
| New terminalized / validated source scopes | 11 / 4 = 2.75 |
| Missing roots / existing #180 HOME changes / conflicts | 0 / 0 / 1 unchanged |

The per-root queue remains cached, not current: this checkout lacks the frozen #180 master and `structure_graph_v3.csv`. Its current global unresolved count, source registry size, post-count join, and Top500/Top2000 counters are refreshed in `SOURCE_YIELD_QUEUE_SUMMARY_V1.json`; stale per-root aggregates are explicitly marked. Frequency remains ranking metadata only.

Validation: source registry re-audit rebuilt from all 111 sources; deterministic membership projection reports 816 validated evidence rows; full cohort authority validator passed its invariants (expected incomplete while UNRESEARCHED remains). Focused Issue #216 suite passed 26/26. Existing #180 confirmed HOME changes: 0; missing roots: 0; current conflict count: 1 unchanged. Final full #180 regression, reproducibility, CI, clean pushed branch, and `UNRESEARCHED = 0` remain pending.


## Exact approved qualifier reuse checkpoint — 2026-09-30

Continued source/membership-driven processing after the roster batch. A deterministic join over all 158 PASS rows in the existing #180 `FAMILY_QUALIFIER` policy found two exact terminal canonical-qualifier matches in the still-open cohort: `megurine_luka_(toeto)` → `toeto_(vocaloid)` and `yoshi_(nagatoro)` → `ijiranaide_nagatoro-san`. Both use the exact final qualifier, have unique PASS root mappings and existing catalog roots, and have no earlier nested qualifier. The two records are `APPROVED_REPO_EVIDENCE` (not rosters); the registry flag now correctly records `exact_roster_available=false`. No member-level web lookup was added.

| Measure | Current |
|---|---:|
| Baseline / accounted | 13,983 / 13,983 |
| Terminalized / coverage | 841 / 6.0144% |
| HOME_CONFIRMED / no-safe-source / policy / identity / conflict | 807 / 18 / 6 / 9 / 1 |
| UNRESEARCHED | 13142 |
| AUTO_ACCEPT / FAST_REVIEW / DEEP_RESEARCH / terminal blocked | 0 / 13113 / 29 / 34 |
| Character-specific Deep Research candidates | 29 (0.207% of cohort) |
| Registry / reusable accepted sources | 113 / 63 |
| Exact member mappings / unique exact Characters / source-member rows | 832 / 830 / 843 |
| Reused member rows / reuse ratio | 786 / 843 (93.24%) |
| Characters per registered source | 7.35 |
| Source audit: open exact AUTO / REVIEW_REQUIRED surfaces | 0 / 31 (29 distinct Characters) |
| Top500 / Top2000 still UNRESEARCHED | 297 / 1626 |
| Since pushed base: terminalized / new URLs / validated scopes | 13 / 2 / 6; 6.50 per URL, 2.17 per scope |
| Missing roots / existing #180 HOME changes / conflicts | 0 / 0 / 1 unchanged |

The six validated scopes are DFFOO FFIV, three Toei Precure title-filter scopes on one URL, and the two already validated Issue #180 qualifier-policy scopes. Root-level queue counts remain cached because the exact #180 master and structure graph are unavailable. Updated global summary confirms Top500/Top2000 priority counts use the frozen cohort and verified post-count snapshot only.

Checkpoint gates: deterministic membership rebuild, all-source exact-scope re-audit, cohort authority validator, and focused Issue #216 tests are recorded below after the current source batch. `UNRESEARCHED = 0`, full #180 regression, reproducibility, CI, and final clean pushed branch remain pending.


Final checkpoint validation after the qualifier-policy batch: `python -m pytest tests/issue216 -q -p no:cacheprovider` passed 26/26; deterministic membership reconstruction passed; all-source re-audit covered 113/113 registry records; the authority validator accepted all invariants and reports incomplete only because 13,142 rows remain UNRESEARCHED; `git diff --check` and Python syntax compilation passed.


## Title-scoped Cinderella Girls source checkpoint — 2026-09-30

Reviewed the official TV anime [Character directory](https://imas-cinderella.com/character/) once as a complete series source, then exact-joined its 62 named page surfaces to the Character catalog and frozen cohort. The deterministic generator found three unresolved unique exact identities: Senkawa Chihiro, Executive Mishiro, and Aoki Sei (Veteran Trainer). All three map to the existing `idolmaster_cinderella_girls` root, which is separately PASS-validated in #180 by Shibuya Rin. The page also surfaced Rookie Trainer only as a role/search alias (`aoki_kei`), so that identity remains Deep Research. Anastasia's same-work exact identity was already HOME_CONFIRMED and its prior source/provenance was preserved; no redundant mapping was written.

The reused Million Live roster was reviewed for its ambiguous `Producer` role. The official page shows a generic Producer role and Chief Producer with no unique canonical mapping; `p-head_producer` is now `IDENTITY_BLOCKED` without HOME. The Cinderella Girls anime producer candidate was marked outside the Million Live source scope. Four other retained FGO candidate surfaces were explicitly excluded from that source's scope (Disney Hercules, Mobile Suit Nemo, Project Moon Roland, and Tenkaichi Fuma Kotaro). These scope dispositions remove false source edges, and none is used as HOME evidence.

| Measure | Current |
|---|---:|
| Baseline cohort / accounted | 13,983 / 13,983 |
| Terminalized / coverage | 845 / 6.0431% |
| HOME_CONFIRMED / no-safe-source / policy / identity / conflict | 810 / 18 / 6 / 10 / 1 |
| UNRESEARCHED | 13138 |
| AUTO_ACCEPT / FAST_REVIEW / DEEP_RESEARCH / terminal blocked | 0 / 13114 / 24 / 35 |
| Character-specific Deep Research candidates | 24 (0.172% of cohort) |
| Source registry / reusable accepted sources | 114 / 64 |
| Exact source-member mappings / unique exact Characters / source-member rows | 835 / 833 / 847 |
| Reused member rows / source reuse ratio | 789 / 847 (93.15%) |
| Characters per registered source | 7.31 |
| All-source audit: open AUTO / REVIEW_REQUIRED surfaces | 0 / 27 |
| Top500 / Top2000 still UNRESEARCHED | 296 / 1624 |
| Since pushed checkpoint: terminalized / URL reviews / source scopes | 4 / 2 / 2 = 2.00 per URL and per scope |
| Missing roots / existing #180 HOME changes / conflicts | 0 / 0 / 1 unchanged |

Root-level unresolved aggregates remain cached because the frozen #180 master and `structure_graph_v3.csv` are absent from this checkout; current global counts and the source-registry re-audit are refreshed. Popularity remains ranking-only.

## Membership reuse follow-up checkpoint — 2026-09-30

Reused validated source scopes to resolve the remaining exact work-level identities without Character-specific Deep Research. The official Cinderella Girls anime directory contributes three new exact HOME memberships. Its `Rookie Trainer` surface is only a role label and does not identify the catalog `aoki_kei` entry, so that row is `IDENTITY_BLOCKED` with no HOME. The accepted Gundam SEED directory's exact `アイシャ` entry was contextually resolved to `aisha_landar`; same-name candidates from Last Origin and Saga were explicitly excluded from the SEED scope. `otonashi_kotori` continues to rely on the accepted 765PRO roster membership; its creator interview is not a required authority.

The complete 765PRO ALLSTARS section on the already reviewed Million Live page was also exact-joined against the cohort. Its 13 identities were all already terminal or outside the frozen unresolved cohort, so it added no duplicate source registration or decision. The current 114-source exact URL/scope re-audit yields 0 open AUTO candidates and 24 open REVIEW_REQUIRED surfaces covering 21 unresolved Characters. New source-scope dispositions removed false cross-work collision candidates from Character-specific Deep Research.

| Measure | Current |
|---|---:|
| Frozen baseline / accounted | 13,983 / 13,983 |
| Terminalized / coverage | 847 / 6.0588% |
| HOME_CONFIRMED / no-safe-source / policy / identity / conflict | 811 / 18 / 6 / 11 / 1 |
| UNRESEARCHED | 13,136 |
| AUTO_ACCEPT / FAST_REVIEW / DEEP_RESEARCH / terminal blocked | 0 / 13,115 / 21 / 36 |
| Character-specific Deep Research / cohort rate | 21 / 0.1502% |
| Source registry / accepted reusable sources | 114 / 64 |
| Exact member rows / unique exact Characters / all source-member rows | 836 / 834 / 849 |
| Reused source-member rows / source reuse ratio | 790 / 849 (93.05%) |
| Exact Characters per registered source | 7.32 |
| Top500 still UNRESEARCHED | 295 |
| Top2000 still UNRESEARCHED | Last verified 1,624 before this checkpoint; stale until the exact post-count snapshot is available |
| Since pushed HEAD: terminalized / new external URL reviews / source scopes | 6 / 1 / 3 |
| Terminalized per external URL review / per source scope | 6.00 / 2.00 |
| Missing Copyright roots / existing #180 HOME changed / conflicts | 0 / 0 / 1 unchanged |

The validated membership projection reports 822 evidence rows and identifies 21 remaining Deep Research candidates. Source registry re-audit, exact mapping schema/scope/root/cardinality and immutable-HOME checks passed. The cohort validator accepts all invariants and remains incomplete only because 13,136 rows are UNRESEARCHED. Focused Issue #216 tests pass 26/26, deterministic membership reconstruction matches, Python syntax compilation and `git diff --check` pass. Root-level expected-yield counts and the current Top2000 value remain unavailable because this checkout does not contain the exact frozen #180 master, structure graph, or post-count snapshot. Full #180 regression, final reproducibility, CI, clean pushed branch, and `UNRESEARCHED = 0` remain pending.

## Reused Fate membership checkpoint — 2026-09-30

Reused the already accepted, exact-scope Fate/Apocrypha official directory and its validated `fate_(series)` root. The exact roster name ジャンヌ・ダルク was resolved to `janne_d'arc`; the same-name Azur Lane identity was explicitly excluded from this source scope. No character-specific source search was needed. The Fate/stay night and Fate/Zero directories were also rejoined to the cohort; their exact Tohsaka Rin entries do not cover the distinct Honkai: Star Rail identity, so those candidate edges were excluded from both source scopes.

The existing Million Live official source scope was replayed across its full 39-member MILLIONSTARS roster. It yielded no new unresolved cohort identity: the exact roster surfaces were already terminal or outside the frozen cohort. The complete source surface list, exact candidate projection, and collision dispositions are retained; no duplicate source or HOME decision was added.

| Measure | Current |
|---|---:|
| Frozen baseline / accounted | 13,983 / 13,983 |
| Terminalized / coverage | 848 / 6.0659% |
| HOME_CONFIRMED / no-safe-source / policy / identity / conflict | 812 / 18 / 6 / 11 / 1 |
| UNRESEARCHED | 13,135 |
| AUTO_ACCEPT / FAST_REVIEW / DEEP_RESEARCH / terminal blocked | 0 / 13,116 / 19 / 36 |
| Character-specific Deep Research / cohort rate | 19 / 0.1359% |
| Source registry / accepted reusable sources | 114 / 64 |
| Exact member rows / unique exact Characters / all source-member rows | 837 / 835 / 850 |
| Reused source-member rows / source reuse ratio | 791 / 850 (93.06%) |
| Exact Characters per registered source | 7.32 |
| Top500 still UNRESEARCHED | 295 |
| Top2000 still UNRESEARCHED | Last verified 1,624 before this checkpoint; stale until the exact post-count snapshot is available |
| Since pushed HEAD: terminalized / new external URL reviews / reused scopes | 1 / 0 / 1 |
| Terminalized per reused membership scope | 1.00 |
| Missing Copyright roots / existing #180 HOME changed / conflicts | 0 / 0 / 1 unchanged |

All 114 source records were rejoined to the exact-scope inventories: 0 open AUTO candidates and 21 open REVIEW_REQUIRED surfaces involving 19 unresolved Characters. Deterministic membership reconstruction and the cohort authority validator pass all invariants; the cohort remains incomplete only because 13,135 rows are UNRESEARCHED. Focused Issue #216 tests pass 26/26. Root-level expected-yield counts and current Top2000 are still unavailable without the exact frozen #180 master, structure graph, and post-count snapshot. Full #180 regression, final reproducibility, CI, clean pushed branch, and `UNRESEARCHED = 0` remain pending.


## Accepted curated Touhou membership reuse checkpoint — 2026-09-30

Reused the already reviewed #180 Danbooru/Safebooru curated Touhou Character list. Its exact linked entries establish Chen under Perfect Cherry Blossom, Aki Shizuha and Aki Minoriko under Mountain of Faith, Tanned Cirno under Embodiment of Scarlet Devil, and Goutokuji Mike under Unconnected Marketeers. The batch scope enumerates only those five exact identities. Existing #180 `touhou` root normalization applies; no candidate root, post count, co-occurrence, or RelatedCopyright edge was treated as membership evidence. `otonashi_kotori` remains supported by the accepted 765PRO roster; no character-specific interview lookup was required.

This checkpoint added 5 HOME decisions across 2 exact membership scopes reusing an already reviewed URL: 5 terminalized / 0 new external URL reviews / 2 membership scopes. Character-specific Deep Research remains an exception path at 19 unresolved Characters (0.1359% of the frozen cohort).

| Measure | Current |
|---|---:|
| Frozen cohort / accounted | 13,983 / 13,983 |
| Terminalized / coverage | 853 / 6.1003% |
| HOME_CONFIRMED / no-safe-source / policy / identity / conflict | 817 / 18 / 6 / 11 / 1 |
| UNRESEARCHED | 13130 |
| AUTO_ACCEPT / FAST_REVIEW / DEEP_RESEARCH / terminal blocked | 0 / 13111 / 19 / 36 |
| Character-specific Deep Research / cohort rate | 19 / 0.1359% |
| Source registry / accepted reusable roster sources | 116 / 65 |
| Exact member mappings / unique exact Characters / source-member rows | 842 / 840 / 855 |
| Reused member rows / source reuse ratio | 795 / 855 (92.98%) |
| Characters per registered source | 7.24 |
| Top500 / Top2000 still UNRESEARCHED | 290 / 1618 |
| New terminalized / new external URL reviews / validated membership scopes | 5 / 0 / 2 |
| Missing roots / existing #180 HOME changed / conflicts | 0 / 0 / 1 unchanged |

All 116 registry sources were rejoined to their exact URL/scope inventories: 0 open AUTO candidates and 21 REVIEW_REQUIRED surfaces remain, covering 19 unresolved identities. Top500 and Top2000 counts were recomputed from the frozen cohort and hash-verified post-count snapshot; counts are routing priority only. Per-root queue counts/order remain cached because the frozen #180 master and structure graph are unavailable.

The focused #216 suite, deterministic membership projection, full source re-audit, complete cohort validator, #180 immutable-HOME check, and `git diff --check` are run for this checkpoint below. Full #180 regression, final reproducibility/CI, clean pushed branch, and `UNRESEARCHED = 0` remain pending.


Checkpoint validation: `python -m pytest tests/issue216 -q -p no:cacheprovider` PASS (26/26); `python -m pytest tests/issue180 -q -p no:cacheprovider` PASS (60/60); deterministic membership projection PASS; exact-scope audit covers 116/116 sources (0 open AUTO, 21 REVIEW_REQUIRED surfaces across 19 unresolved identities); cohort validator passes all invariants and reports incomplete only for 13,130 UNRESEARCHED rows; Python syntax compilation and `git diff --check` PASS. Existing #180 confirmed HOME mutation count remains 0.


## Core Danganronpa curated membership batch — 2026-09-30

Reused the explicit Danbooru curated [Danganronpa character list](https://shima.donmai.us/wiki_pages/list_of_danganronpa_characters), which groups exact linked Character entries by debut game. A single scoped source batch enumerated 46 surfaces from the complete Trigger Happy Havoc and Goodbye Despair headings. Deterministic exact matching produced 27 unique unresolved cohort identities and all 27 were accepted to the already validated `danganronpa_(series)` root: 27 terminalized / 1 new source review = **27.00 per source review**. The other source surfaces were retained as candidate outcomes only: 10 outside cohort, 8 without safe catalog match, and the repeated `Togami Byakuya` identity surface was left REVIEW_REQUIRED. No neighboring game/spinoff/crossover section or unlisted identity was extended into scope.

| Measure | Current |
|---|---:|
| Frozen cohort / accounted | 13,983 / 13,983 |
| Terminalized / coverage | 880 / 6.2934% |
| HOME_CONFIRMED / no-safe-source / policy / identity / conflict | 844 / 18 / 6 / 11 / 1 |
| UNRESEARCHED | 13103 |
| AUTO_ACCEPT / FAST_REVIEW / DEEP_RESEARCH / terminal blocked | 0 / 13084 / 19 / 36 |
| Character-specific Deep Research / cohort rate | 19 / 0.1359% |
| Source registry / reusable accepted roster sources | 117 / 66 |
| Exact member mappings / unique mapped Characters / source-member rows | 869 / 867 / 882 |
| Reused member rows / source reuse ratio | 822 / 882 (93.20%) |
| Characters per registered source | 7.41 |
| Top500 / Top2000 still UNRESEARCHED | 279 / 1594 |
| New terminalized / new external URL reviews / new source scopes | 27 / 1 / 1 |
| Missing roots / existing #180 HOME changed / conflicts | 0 / 0 / 1 unchanged |

The full registry re-audit now covers 117 sources: 0 open AUTO candidates and 21 REVIEW_REQUIRED surfaces across 19 unresolved identities. Candidate roots and post counts remain priority-only. No high-yield Copyright root is declared complete from this partial two-game batch.


Checkpoint validation for the curated Danganronpa batch: `python -m pytest tests/issue216 -q -p no:cacheprovider` PASS (26/26); `python -m pytest tests/issue180 -q -p no:cacheprovider` PASS (60/60); deterministic membership reconstruction PASS; all-source audit covers 117/117 sources (0 open AUTO and 21 REVIEW_REQUIRED surfaces across 19 identities); cohort validator passes all invariants and reports incomplete only for 13,103 UNRESEARCHED rows; `git diff --check` PASS.


## 2026-09-30 Fate curated membership batch — resume checkpoint

- Reviewed the explicit Danbooru curated [Fate series Character list](https://safebooru.donmai.us/wiki_pages/list_of_fate_series_characters) once. Its named work headings group exact linked identities by first appearance. The batch scope was limited to five unique exact catalog matches explicitly listed under Fate/Hollow Ataraxia, Fate/Unlimited Codes, Fate/Extra, and Fate/Extra CCC: `caren_hortensia`, `magical_ruby`, `kishinami_hakuno_(female)`, `saber_lily`, and `sessyoin_kiara`. Existing #180 Fate-family normalization supports their unique `fate_(series)` HOME. Prisma Illya's separately normalized root, FGO appearance/crossover entries, ambiguous class labels, all unreviewed headings, and unlisted identities were excluded.
- This is one accepted curated membership source reviewed once and joined against exact catalog identities; no Character-specific external research was performed. The batch terminalized 5 Characters / 1 newly reviewed source URL = **5.00 terminalized per external source review** and 5 / 1 source-scope review. All five are in frozen Top500; Top500 unresolved fell 279→274 and Top2000 1,594→1,589.
- Frozen cohort 13,983 / accounted 13,983; terminalized **885** (6.3291%); HOME_CONFIRMED 849; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 18; POLICY_BLOCKED 6; IDENTITY_BLOCKED 11; EVIDENCE_CONFLICT 1 (unchanged); UNRESEARCHED **13,098**. Membership routing: AUTO_ACCEPT 0; FAST_REVIEW 13,080; DEEP_RESEARCH 18; terminal blocked 36. Character-specific Deep Research remains 18 / 13,983 (0.1287%).
- Registry 118 sources, 67 accepted reusable roster sources; exact member mappings 874; source-member rows 887; source reuse ratio 93.2356%; 7.52 source-member rows per registered source. Reaudit: 118/118 sources; 0 open exact AUTO candidates; 20 REVIEW_REQUIRED surfaces across 19 identities. No high-yield root is declared complete.
- Missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflict count 1 unchanged. Root-level queue counts/order remain explicitly cached because the exact frozen #180 master and `structure_graph_v3.csv` are unavailable in this checkout; cohort-wide Top500/Top2000 counts were independently recomputed using the frozen cohort and hash-verified Issue #70 post-count snapshot strictly for priority.
- Batch application validator, deterministic membership-table rebuild/check, membership-batch check, source registry re-audit, `tests/issue216` (26/26), `tests/issue180` (60/60), cohort/root/cardinality validation, and `git diff --check` PASS.
- Retained artifacts: `PROPOSED_SOURCE_FATE_CURATED_CHARACTER_MEMBERSHIP_2026-09-30.csv`, `MAPPING_CANDIDATES_FATE_CURATED_CHARACTER_LIST_PREFLIGHT_2026-09-30.csv`, and `BATCH_FATE_CURATED_CHARACTER_MEMBERSHIP_2026-09-30.csv`.


## 2026-09-30 Hololive curated mascot membership batch — resume checkpoint

- Reviewed the explicit Danbooru curated [Hololive mascots list](https://safebooru.donmai.us/wiki_pages/list_of_hololive_mascots) once. Exact linked Character targets under their named current/former Hololive talents matched 12 unresolved cohort identities: `takodachi_(ninomae_ina'nis)`, `don-chan_(usada_pekora)`, `bibi_(tokoyami_towa)`, `bloop_(gawr_gura)`, `pekomon_(usada_pekora)`, `chattino_(raora_panthera)`, `35p_(sakura_miko)`, `friend_(nanashi_mumei)`, `mr._squeaks_(hakos_baelz)`, `ssrb_(shishiro_botan)`, `sukonbu_(shirakami_fubuki)`, and `crow_(la+_darknesss)`. The list explicitly scopes its mascot entries to Hololive Production talents; the parent talent-to-`hololive` path reuses accepted #180 membership. No talent, tag co-occurrence, popularity, or Character-specific profile search supplied membership evidence.
- `pekomama` and `kurokami_fubuki` were not present as exact identities in this reviewed mascot list, so they remain UNRESEARCHED. Other list entries were outside this source-scope batch.
- This one source review terminalized 12 Characters / 1 new URL = **12.00 terminalized per external source review**. All 12 are in frozen Top500; Top500 unresolved fell 274→262 and Top2000 1,589→1,577.
- Frozen cohort 13,983 / accounted 13,983; terminalized **897** (6.4150%); HOME_CONFIRMED 861; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 18; POLICY_BLOCKED 6; IDENTITY_BLOCKED 11; EVIDENCE_CONFLICT 1 (unchanged); UNRESEARCHED **13,086**. Membership routing: AUTO_ACCEPT 0; FAST_REVIEW 13,068; DEEP_RESEARCH 18; terminal blocked 36. Character-specific Deep Research remains 18 / 13,983 (0.1287%).
- Registry 119 sources, 68 reusable roster sources; exact member mappings 886; source-member rows 899; source reuse ratio 93.3259%; 7.55 source-member rows per registered source. Reaudit: 119/119 sources; 0 open exact AUTO candidates; 20 REVIEW_REQUIRED surfaces across 19 identities. No high-yield root is declared complete.
- Missing Copyright roots 0; existing #180 confirmed HOME changed 0; conflict count 1 unchanged. Root-level queue counts/order remain explicitly cached because the exact frozen #180 master and `structure_graph_v3.csv` are unavailable in this checkout; cohort-wide Top500/Top2000 counts were independently recomputed from the frozen cohort and hash-verified Issue #70 post-count snapshot for priority only.
- Batch validator, deterministic membership-table rebuild/check, membership-batch check, source registry re-audit, `tests/issue216` (26/26), `tests/issue180` (60/60), cohort/root/cardinality validation, and `git diff --check` PASS.
- Retained artifacts: `PROPOSED_SOURCE_HOLOLIVE_CURATED_MASCOT_MEMBERSHIP_2026-09-30.csv`, `MAPPING_CANDIDATES_HOLOLIVE_CURATED_MASCOT_LIST_PREFLIGHT_2026-09-30.csv`, and `BATCH_HOLOLIVE_CURATED_MASCOT_MEMBERSHIP_2026-09-30.csv`.

## 2026-09-30 curated VOCALOID membership checkpoint

- Batch: reviewed the explicit linked-member section `List of VOCALOID products` in the accepted curated Danbooru list. Exact catalog mapping generated for 118 listed surfaces; 32 exact unique cohort matches were reviewed as one source batch.
- Outcomes: 21 HOME_CONFIRMED to the validated `vocaloid` root; 11 POLICY_BLOCKED for exact identities whose same roster entry explicitly spans multiple engine/franchise memberships. Ambiguous/no-match entries were not inferred from.
- Batch yield: 32 terminalized Characters / 1 new membership-source review = 32. The source was reviewed once; its exact mappings are reusable across the cohort.
- Baseline cohort 13,983; terminalized 929; HOME_CONFIRMED 882; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 18; POLICY_BLOCKED 17; IDENTITY_BLOCKED 11; EVIDENCE_CONFLICT 1; UNRESEARCHED 13,054; coverage 6.641%.
- Registry 120 (69 reusable accepted rosters); exact member mappings 918 over 931 source-member rows; 916 unique exact mapped cohort identities; reused-source ratio 93.56%; 7.63 exact mapped Characters per registered source.
- Source re-audit: all 120 registered sources rejoined; 0 open AUTO candidates, 29 REVIEW_REQUIRED surfaces across 25 identities. Source inventory remains scope-limited; no unlisted member was terminalized.
- Top500 UNRESEARCHED 256. Top2000 is retained as the previous 1,577 priority snapshot and is explicitly stale after this batch because its exact rank input is unavailable in this checkout. Candidate-root queue counts/order remain cached for the same missing frozen #180 master/graph inputs.
- Missing Copyright roots 0; existing #180 confirmed HOME changed 0; new conflicts 0 (one pre-existing conflict remains). Focused #216 tests 26/26 PASS; full #180 regression 60/60 PASS; deterministic membership rebuild and `git diff --check` PASS. Production unchanged.
- Deep Research queue: 24 identities (0.1716% of baseline). AUTO_ACCEPT 0 outstanding; FAST_REVIEW 13,030; terminal blocked 47. Source-specific deep research was not expanded for exact unique curated members.
- Branch remains `codex/issue216-unresolved-coverage-7073`; checkpoint follows after commit/push.
