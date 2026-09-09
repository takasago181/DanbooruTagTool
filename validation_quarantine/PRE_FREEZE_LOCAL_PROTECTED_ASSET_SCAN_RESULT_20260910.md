# Issue #32 — pre-freeze local protected-asset completeness scan result

Date: 2026-09-10
Branch: `dict-validation/quarantine`
Task contract: `validation_quarantine/PRE_FREEZE_LOCAL_PROTECTED_ASSET_SCAN_TASK_20260910.md`
Scan input commit: `807cbf3c762be51231dfe8f211eeb2e08b7d44dd`
Production `data/**`: unchanged

## Final enum

`LOCAL_COMPLETENESS_DELTA_FOUND`

The scan found five local terms explicitly retained as same-name/unconfirmed candidates. They are not certified as missing Specials: no independent first-class Special authority, Special ID, canonical identity, or alias target was found for them. They are recorded in the quarantine-only delta ledger and are not promoted. The completed 2,788 first-pass results remain unchanged.

## Frozen Special identity used for comparison

The frozen comparison set was loaded from:

`data/generation/special2788_generation_profile.csv`

- Git blob pinned by the #32 audit snapshot: `ac6c1d24e1c6ce04b238cc0b16d788f9d0965a05`
- Local file SHA-256: `3d3b7c16bee23c34892c6ac1a40b69208ef14199c5bae749ac8a22151c8dc835`
- Rows: 2,788 data rows; unique original tags: 2,788; unique comparison keys: 2,788
- Fixed ordering was not rerun or changed.

Cross-check source:

`data/special2788/illustrious_tag_knowledge_base_2788.csv`

- Rows: 2,788 data rows
- Local SHA-256: `07584b365d5a68dbadd3f5e80859e768c2718b18746e32de02ce4b8bd60935e3`
- Prompt reference manifest records the same 2,788-row source and this SHA-256.

Normalization used only the project lookup contract: NFKC, lowercase, trim, underscore-to-space, whitespace collapse. Original spellings and source provenance were retained in the ledger/report.

## Local asset inventory

The scan ran in the workspace that contains the ignored/protected assets; absence from GitHub was not treated as absence locally.

| Actual path | Files | Bytes | Inventory role |
|---|---:|---:|---|
| `data/source/` | 1 | 3,436,154 | retained raw tag source |
| `data/derived/` | 16 | 25,336,393 | canonical, alias, Special/semantic derived assets |
| `data/generation/audit/` | 7 | 1,928,749 | generation audit/profile sidecars |
| `data/runtime/` | 1 | 2,236,277 | Japanese runtime overlay |
| `data/runtime_index/` | 11 | 2,989,206,293 | search/statistics indexes and identity overlay |
| `data/runtime_source/` | 1 | 4,088,245,636 | protected post snapshot |
| `data/special2788/` | 25 | 1,756,139 | protected Special CSV/XLSX and prompt references |
| `data/japanese/` | 5 | 14,510,223 | Japanese source/term assets |
| **`data/**` total** | **89** | **7,127,474,426** | **production data inventory** |
| `archive/` | 16 | 1,235,303 | ignored provenance Special/generation text |
| `backups/` | 1,366 | 29,720,812 | ignored historical profiles, sidecars, and test snapshots |
| `_handoff/` | 290 | 12,706,386 | ignored prior handoffs and incoming packages |
| `translation_quarantine/` | 754 | local untracked | local search/translation candidate and manifest outputs |

Pre-scan `data/**` manifest (sorted relative path, byte size, SHA-256):

`files=89; bytes=7127474426; manifest_sha256=b47148d440e433726abf7e1545629c2cce92d177495db7a1dc0d2b120784fd4f`

Post-scan PowerShell recheck: `files=89; bytes=7127474426; manifest_sha256=b47148d440e433726abf7e1545629c2cce92d177495db7a1dc0d2b120784fd4f`; identical to the pre-scan manifest.

Representative protected/ignored assets actually read and hashed:

- `data/source/danbooru-2026-09-02.csv` — SHA-256 `9b32d5ac0713ab252e7470ba6af9cb34de56878b6b3b13dfbbf6a4a37d82d95b`; 124,016 rows.
- `data/derived/danbooru_full_tag_knowledge_base_VERIFIED_124016.csv` — SHA-256 `23f951c82e3a25a1d7089711d629b4ab6bb3adad17a130e077044da8871feba0`; 124,016 data rows.
- `data/derived/danbooru_alias_normalized_index_VERIFIED_34417.csv` — SHA-256 `3f942704a10bb342ae7368024337849d392d54745061cf9259e51b9f6080a394`; 34,417 data rows.
- `data/derived/danbooru_alias_occurrences_VERIFIED_34630.csv` — SHA-256 `3e0c172227612247bc0ba89de16f79b48765b4adb81be5e168c42d0ad65ebe0b`; 34,630 data rows.
- `data/derived/ruleset2/10_MODEL_AUX_CROSSMATCH_UNIQUE_TERMS_2811.csv` — SHA-256 `bc9223d1fbcacdbc19bd41a54b7a093fad8382534707fc858e039aa656a65d81`; 2,811 data rows.
- `data/runtime_index/tags.json` — SHA-256 `b8be4780f5d21bcd938ddace58220d0a003418407e29d1563f937a60b9a867aa`; 103,198 entries.
- `data/runtime_index/canonical_overlay.json` — SHA-256 `bf9a62105740ec579ea0618721b78a0d3ccc2279cf18aabf402c3083ede05195`.
- `data/runtime/japanese_overlay.json` — SHA-256 `de1b375d79ef05f4c2477347b20b8a09115511d2ecbd39602bdebcdfa6d576dc`.
- `archive/provenance/special2788_generation/under18_censorship_COUNTS_FINAL_audit.txt` — SHA-256 `6c717d193ef3eec11148a0d76489eea18576e4eb8e99a7b0b616af12ec5df190`; local unconfirmed-candidate record.
- `_handoff/RULESET2_INCOMING_TMP/DanbooruTagTool_RULESET2_CONTINUATION_2026-09-07B/WORKING_TREE/01_SPECIAL2788_JAPANESE_COMPLETE_CANDIDATE.csv` — SHA-256 `12f6ccdc5d2dba33123cdfa97a636b2fdd49a519ed89d327d330471696762e02`; historical copy of the 2,788-row candidate.
- `translation_quarantine/one_shot_uija_remaining_20260909/source_candidate_ledger.jsonl` — SHA-256 `207fba72b0ae2b7d0617749561a0e338ca33cac652e8ca3ef19ee75f3c32e11c`; 30,629 local search/translation rows.

The local `.worktrees/` directory was preserved and not treated as an independent data authority; it is an operational duplicate area, not a missing protected-data category. No cleanup, delete, regeneration, or normalization-in-place operation was performed.

## Comparison coverage and counts

Observed identity-bearing terms were collected from actual structured fields and explicit provenance labels in:

- Special source/profile, Ruleset2 Special/semantic/alias sidecars, generation audit files;
- canonical source/dictionary, alias normalized index and alias occurrences;
- runtime tag list, canonical identity overlay, Japanese overlay and Japanese term sources;
- semantic bridge/support/recommendation assets and validation quarantine ledgers;
- local translation/search JSONL outputs;
- ignored archive provenance, historical backup copies, and `_handoff` candidate/profile copies.

Totals after NFKC/lower/underscore-space comparison:

- Observed unique normalized keys: 338,997
- Unique normalized keys outside the frozen 2,788: 336,209
- Normalized keys with non-exact underscore/space/case spellings of an existing frozen Special: 2,246; these are `NOT_SPECIAL_DUPLICATE_NORMALIZATION`, not new Special identities.

| Classification | Unique normalized keys |
|---|---:|
| `NOT_SPECIAL_AUXILIARY` | 29 |
| `NOT_SPECIAL_ALIAS_OF_EXISTING` | 65,430 |
| `NOT_SPECIAL_SEARCH_ONLY` | 139,855 |
| `NOT_SPECIAL_GENERAL_TAG` | 130,890 |
| `SPECIAL_CANDIDATE_NEEDS_EVIDENCE` | 5 |
| `GENUINE_MISSING_SPECIAL` | 0 |
| **Out-of-set total** | **336,209** |

The five candidate rows are not counted as genuine missing Specials. Their exact records are in:

`validation_quarantine/PRE_FREEZE_LOCAL_PROTECTED_ASSET_SCAN_DELTA_20260910.csv`

| Original term | Comparison key | Source record | Finding |
|---|---|---|---|
| `cervix_removal` | `cervix removal` | `under18_censorship_COUNTS_FINAL_audit.txt`, line 16, `同名未確認候補（ユニーク）` | no frozen Special, canonical, alias, Special ID, or independent first-class authority |
| `fallopian_tubes_removal` | `fallopian tubes removal` | same record | same |
| `ovaries_removal` | `ovaries removal` | same record | same |
| `spread_eagle` | `spread eagle` | same record; also `under18_censorship_TRUE_FINAL_all.txt` and `_female_common.txt` candidate sections | no frozen Special, canonical, alias, Special ID, or independent first-class authority |
| `uterus_removal` | `uterus removal` | same record | no frozen Special, canonical, alias, Special ID, or independent first-class authority |

Required semantic/risk handling for all five is conservative: reproductive-anatomy removal candidates have body-site/target semantics but no independently asserted actor, visibility, or relation authority; `spread_eagle` is a pose/exposure candidate with no independently asserted actor/target/body-site relation. All are risk `S` for identity uncertainty and generation behavior remains model-scoped `HOLD`. No generation reliability was inferred from semantic membership.

## Production integrity and stop point

- No file under `data/**` was edited, deleted, regenerated, or normalized.
- No first-pass 2,788 validation was rerun.
- No auxiliary, general, search-only, alias, or semantic support term was promoted to Special.
- No `git clean -fdx` or `git clean -fdX` command was run.
- The result and delta ledger are quarantine-only artifacts.
- Because the final enum is `LOCAL_COMPLETENESS_DELTA_FOUND`, do not close completeness or start final promotion from this report. Validate only the five evidence-pending delta rows under the applicable #32 R2 rules in a separate follow-up; do not alter the completed 2,788 results.
- After commit/push, stop. No promotion and no main merge are part of this task.
