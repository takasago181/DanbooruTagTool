# Issue #216 — full-cohort authority coverage checkpoint

## Baseline and current coverage

- Issue #180 authority commit: `9c0db59c0f1dc56402c955e718a37d9de1849d7e`.
- Frozen master SHA-256: `135463a5225b6501db923322284f8e309f217eb5359538088eb6de6d78b77071`.
- Baseline population: 35,890; HOME_CONFIRMED 21,907; HOME_UNRESOLVED 13,983.
- Frozen unresolved cohort: 13,983 / 13,983 accounted; cohort ID-list SHA-256 `2db82cd3640196a29015124f28ca75f849c5469ba8dede8f2bb0396c6ecf8f31`.
- Current states: HOME_CONFIRMED 19; SOURCE_RESEARCHED_NO_SAFE_EVIDENCE 0; POLICY_BLOCKED 0; IDENTITY_BLOCKED 0; EVIDENCE_CONFLICT 0; UNRESEARCHED 13,964.
- Stage A Top500: 19 HOME_CONFIRMED, 481 UNRESEARCHED. Calibration Gate is **not passed**.
- Additive HOME_CONFIRMED total: 21,926 / 35,890 (61.09%). The original #180 master remains byte-identical; baseline-confirmed rows are outside this cohort and unchanged.
- HOME cardinality: at most one field/value per decision; missing references to the complete Issue #70 Copyright catalog: 0.
- Copyright source registry: 13 official sources; exact member mappings: 19; source reuse ratio: 7/19 (36.84%), from the seven exact Limbus Company Sinners covered by one source.

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

All 19 were rechecked against first-party pages/manuals for exact identity, source scope, and one canonical root. Proposed roots were compared with the existing HOME-root set. Each source/member mapping and claim is recorded in `COPYRIGHT_AUTHORITY_REGISTRY_V1.csv`, `AUTHORITY_SOURCE_MEMBERS_V1.csv`, and `AUTHORITY_COVERAGE_DECISIONS_V1.csv`. The original Top500 proposal ledger remains unmodified.

## Validation

- Full cohort freeze/reconstruction from exact #180 master: PASS (13,983 rows).
- Complete Issue #70 Copyright catalog reconstruction: PASS (8,536 roots; 92,739 source rows; exact source SHA in manifest).
- Top500 source revalidation deterministic rebuild: PASS (19 exact members / 13 sources).
- Authority coverage validator: structurally valid; reports `complete: false`, `UNRESEARCHED=13,964`.
- Issue #216 tests: 13 PASS.
- `git diff --check`: PASS.
- CI: not run; current root-catalog correction is pending commit/push.

## Next work

Continue Stage A over every remaining member in ranks 1–500, reusing reviewed official sources only for exact mappings. Then continue by post-count priority through rank 2,000 and by Copyright-root batches across the remaining frozen cohort. Keep partial/ambiguous members open until they receive a safe terminal reason. No main merge, production apply, Picker implementation, or mutation of the #180 master is authorized by this research checkpoint.
