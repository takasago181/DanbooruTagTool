# Protected data recovery delta closure — 2026-09-10

## Verdict

`FUNCTIONALLY_RESTORED_WITH_AUDITED_NEW_METADATA`

The remaining `+1,192` bytes are explained by the surviving pre-freeze
record's group accounting and line-ending/working-tree representation. No
content-level corruption, alternate snapshot use, unique local loss, or
unexpected protected-data modification was found.

The known Special README difference is separate: `+40` bytes. Therefore the
full post-extra delta is `+1,232` bytes, exactly as follows:

```text
+2,979  omitted data/generation root + data/semantic versus the scan table's implied subtotal
-1,787  data/generation/audit current bytes versus the scan table's recorded subtotal
+   40  known Special README difference
-------
+1,232  current minus accident-before reference
```

The pre-freeze scan preserved the complete manifest digest and group total,
but did not preserve a per-file list for `data/generation/` root files or
`data/semantic/`. It did preserve `data/generation/audit/` as one aggregate
row. Consequently, the `+1,192` residual is an accounting/representation
delta, not an independently assignable corrupted file.

## Scope and safety

- Protected data was read and hashed only during this audit.
- No protected file was deleted, regenerated, normalized, or overwritten.
- The unexpected ThetaCursed Parquet remains excluded from the production
  comparison and was not used.
- No alternate snapshot was used.
- No `git clean`, merge to `main`, #35 completion, or #49 start was performed.

## Evidence sources

1. `validation_quarantine/PRE_FREEZE_LOCAL_PROTECTED_ASSET_SCAN_RESULT_20260910.md`
   - scan input commit: `807cbf3c762be51231dfe8f211eeb2e08b7d44dd`
   - accident-before: 89 files, 7,127,474,426 bytes
   - manifest SHA-256:
     `b47148d440e433726abf7e1545629c2cce92d177495db7a1dc0d2b120784fd4f`
2. `docs/recovery/PROTECTED_DATA_RECOVERY_20260910.md`
   - exact source and runtime recovery evidence, including current hashes.
3. `docs/recovery/PROTECTED_DATA_FINAL_RECOVERY_20260910.md`
   - final 89-file comparison after excluding the one unexpected extra.
4. `docs/stage_reports/GENERATION_PROFILE_V2_1_REPORT.md`
   - canonical generation-profile inputs and current production hashes.
5. Git tree/blob evidence at `807cbf3`
   - tracked generation-root and semantic content, compared after CRLF to LF
     normalization without changing the working tree.

## Group comparison

The current row excludes only
`data/source/danbooru2026_clean.parquet` (3,940,643,859 bytes), which is the
already-audited unexpected ThetaCursed snapshot.

| group | accident-before files | accident-before bytes | current files | current bytes | delta | evidence |
|---|---:|---:|---:|---:|---:|---|
| `data/source/` | 1 | 3,436,154 | 1 | 3,436,154 | 0 | exact retained source |
| `data/derived/` | 16 | 25,336,393 | 16 | 25,336,393 | 0 | exact current inventory |
| `data/generation/audit/` | 7 | 1,928,749 | 7 | 1,926,962 | -1,787 | only aggregate accident-before row survived |
| `data/generation/` root | omitted | omitted | 3 | 566,300 | not independently assignable | tracked content matches scan-input commit after EOL normalization |
| `data/runtime/` | 1 | 2,236,277 | 1 | 2,236,277 | 0 | exact runtime overlay |
| `data/runtime_index/` | 11 | 2,989,206,293 | 11 | 2,989,206,293 | 0 | group total and exact rebuild hashes |
| `data/runtime_source/` | 1 | 4,088,245,636 | 1 | 4,088,245,636 | 0 | exact pinned source SHA |
| `data/special2788/` | 25 | 1,756,139 | 25 | 1,756,179 | +40 | known README only |
| `data/japanese/` | 5 | 14,510,223 | 5 | 14,510,223 | 0 | exact source group |
| `data/semantic/` | omitted | omitted | 19 | 255,241 | not independently assignable | tracked content matches scan-input commit after EOL normalization |
| **total** | **89** | **7,127,474,426** | **89** | **7,127,475,658** | **+1,232** | after extra exclusion |

The scan-listed rows sum to 67 files and 7,126,655,864 bytes. The scan's
overall total therefore implies 22 omitted files and 818,562 bytes. Current
omitted groups contain the same 22 paths and 821,541 bytes, a `+2,979`
difference. The audit row is simultaneously `-1,787` bytes from its recorded
aggregate and the README is `+40`, closing to `+1,232` exactly.

## File-level audit of differing/omitted groups

### Tracked generation root and semantic files

The scan did not retain direct expected rows for these 22 files. The
`807cbf3` Git blobs are the surviving tracked-content witness. The table
below records their blob byte size/SHA-256 and the current raw working-tree
byte size/SHA-256. `normalized_equal=yes` means the current CRLF bytes become
byte-identical to the Git blob after CRLF→LF normalization; no content row,
ID, tag, or semantic value changed.

| path | 807 blob size / SHA-256 witness | current size / SHA-256 | tracked | recovery/commit finding |
|---|---:|---:|---|---|
| `data/generation/generation_family_rules.csv` | 5,492 / `6507e640bcf2a1607d2235247b164c00319fc23ceb010f98934d99a55724f161` | 5,518 / `0f0e2e9f1f001d12e421324a6356bab42293fb206fe53a3e642495d5765c6936` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/generation/generation_model_observations.csv` | 3,587 / `47a2b3b4528a6aad441d8d77fab1a84cd97d2b874ee30794d6b6c1ce220c5965` | 3,605 / `ee036aac810ef94b9f0376a23d0159f4275d6d2feac7ccd689ca297d361164c8` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/generation/special2788_generation_profile.csv` | 554,388 / `8771d72738187d16235d33fb99d484b8e6d243b756a775fd5a04cb6970f3d60b` | 557,177 / `3d3b7c16bee23c34892c6ac1a40b69208ef14199c5bae749ac8a22151c8dc835` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/family_support_rules.csv` | 608 / `59609aadc82f9f4be97b82008159b55e4d738f41dbb9625c59be8a826fe7c4fd` | 610 / `85907d03a5425675d1afc87177a8c99fe846d941718780a6b86baa10373c5465` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/recommendation_generation_hints.csv` | 1,645 / `2fdc8878c9529bb0eeafebd2bc814a553e92d2b24fa0ff1478e4a51a610609dd` | 1,658 / `5ae09ddb0267f0a6de563ea5b49d76725795724500938552666e3c591f6ecd79` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/recommendation_semantic_labels.csv` | 1,989 / `4d126b2f513b3ee342258148771ed81282456f75cadb35ab579502675cfc957d` | 2,024 / `57459defccb4ac0fe8f55a938557531dad2d067ea45d36a1655f8cd5824cbe0f` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/semantic_bridge_v1.csv` | 47,576 / `80a797c0e7ab34b58b6c1353ebf466746135d38c5ba0d04cb0a937c322661bae` | 47,913 / `d34df85810641447f39e4b12f9dcecab6983b2e1a4384439fa3934dba8c35247` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/semantic_support_profiles.csv` | 15,900 / `33f9142333db867d53096cf2f11ba411aefa13996560326fa174803a2d8c2755` | 15,959 / `2ecddf3fa35fe7e1f2c2a32b201cd016f2d2df7f8672f25bed37237aa996afc2` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/stage10_test_slots.csv` | 160 / `cfd4826025c56ba0f376aa29424e4ecf09742510c2a1526606dabcbe572ca33e` | 161 / `ddac136b3c6839c8f31e60298d6551fd6d16ed48effa4cffa2c7ad4744789a49` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/stage8c_exit_pilot_family_assessment.csv` | 1,708 / `f25d887889a9f87efb8cad334b13dab692251012264103eb1d8b660b90d65b25` | 1,716 / `8e699ae1111a17498d67d23e858e65c57fc35b7ae8e98f4156fffd02cd591241` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/stage8c_exit_pilot_scope.csv` | 2,455 / `ae3cc40279d494eed0d17f7e09a91c88fb5821e34789d08752bc605ffe883a85` | 2,468 / `458678b49066cdd6dcfcc3bc9d41e80c34a2094c83be8f9d73a0004f6c6a9009` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/stage8c_family_candidate_applicability.csv` | 3,838 / `0f11f91a782d81785069b90e843e42849d113d3810f87c86243d22c857280287` | 3,854 / `4365211b4c15d858d3a6004d35ca15392852b30cdacdb839107b2afc2fbd01e5` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/stage8c_family_relation_proposals.csv` | 625 / `ac38075df40db42b6427e551aeccb375b7a831cf2072c995f5541d4eca928473` | 627 / `7dc74464b67fed6fe73e6d70707974e8bf5c9d3facf9dea7da0f3a5e9e455ef2` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/stage8c_family_rule_review.csv` | 3,903 / `1d1aa2ac834b10ecc144665357ed624fa02d2c513d91ce6bfa55fce9b0bd3043` | 3,929 / `681537dbdc17869bc4a70ce8ef8725efdeebd3bc859c9ad154933154203e832a` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/stage8c_model_familiarity.csv` | 230 / `3ab05b98c2153f50eaa25b179be619d19608184800be7ba09c01ce6f58e1939c` | 231 / `b9fa2c16a55f04aa584c8013db76209f5edffc77797a915ba1fcce966e92dc33` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/stage8c_non_tag_strategy.csv` | 136 / `aa265214cc80bac1e589bed889bed17ec5b2205a496cee438e0f40001e155214` | 137 / `4cafc8042676ec3cd9c0be6ea73ed47b1e91e05f3d2086fadccb3a8c4b267399` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/stage8c_pilot001_frozen_expectations.json` | 926 / `0cc4e5bcb82fa82914d8fa67d6143caefbe9e990628b48e3e296affb880e8692` | 955 / `ebe872ed84429227fc3351750549c18ba93f4f15af3cd2e1c27b78ecf35a4818` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/stage8c_practical_use.csv` | 149 / `31f7aa6a51e5cf7a0d1bf7dfbb861971b36f84301fe897bcbf595c9e70739a76` | 150 / `7415f73372277a2d1c1be682c4a78960b4016e9f5640e8de06cf1324bc45e499` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/stage8c_relation_evidence_events.csv` | 264 / `0eb251a91d5981efe114566e447975b18a628823733f930f8a3fcb38c1c0f096` | 265 / `99448e2bfa508b3ee877a639f7505a67c1dcf27a3bb8d692ee411596aa0ca730` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/stage8c_research_sources.csv` | 4,660 / `e0d7829e9c8fd925f2882cc3263b4c24ecb6687ced4a34ae69446fee3666c221` | 4,677 / `dcfedd028648e7519ee7814d497118e69d477a4da5c0f1a6682a556d86852036` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/stage8c_review_status.csv` | 161,898 / `85478656ab894d089ec46d5facc067f00ad98a6d464258b607b827210b916a18` | 164,687 / `42360a05641ed738b0f80925171e9f0a80d72ed3279b7bfac8e95ec28d11fe33` | yes | CRLF-only representation delta; current content is exact after normalization |
| `data/semantic/stage8c_static_family_coverage_strategy.csv` | 3,194 / `3f6f7764784f0fa38ed412bf8f8f3f2b1bd9d2a6750462330243a8bf6bdbbf59` | 3,220 / `f7d9b5749ff669a4930544104b0936e9a40498913599d6858fd04ce1a24f1a02` | yes | CRLF-only representation delta; current content is exact after normalization |

All 22 rows above were `normalized_equal=yes`. They were not recovered or
regenerated in this audit, and no regular Git commit after the scan input
commit records a content update for them. The current raw SHA differs from
the LF blob SHA only because the working-tree byte representation is CRLF.

### `data/generation/audit/` aggregate-different files

No per-file accident-before size or SHA survived for this seven-file row. The
current files are the canonical v2/v2.1 audit inputs, and their hashes match
the recovery report and the current Generation Profile v2.1 handoff evidence.
They are ignored local protected files, not tracked Git blobs.

| path | accident-before expected | current size / SHA-256 | provenance |
|---|---:|---:|---|
| `APPROVED_STATIC_1352_REVIEW_v1.csv` | no per-file record; group only | 545,869 / `dcd09c03e5dd9dedcedfa98e248d758ec8e54a77c0163d3271f2fc779895c30b` | v2.1 audit handoff |
| `EXPLICIT_STRUCTURAL_OVERRIDES_240_v1.csv` | no per-file record; group only | 94,802 / `e6f20275258c5ad1eb8d40ba21b100c709e457996ba078d7c5bf44270bec09dd` | v2.1 audit handoff |
| `FAMILY_AUDIT_VALIDATION_v1.json` | no per-file record; group only | 1,002 / `67af388ac98d8414e3a89c0d8e9fff220b2ccf25bdd4830faf1ffe995a05a5dd` | v2.1 audit handoff |
| `FAMILY_RULE_AUDIT_25_v1.csv` | no per-file record; group only | 7,738 / `70e49f7d1a5ef71167b2ea30bea6bc0ee75a79f60e105575d8ccc3adc49d9975` | v2.1 audit handoff |
| `HIGH_CONFIDENCE_CORRECTIONS_v1.csv` | no per-file record; group only | 35,507 / `22c76da0cb3a2b58c36b405609823e11c332ae5565c1c4bd35501a3c0be2bbf5` | v2.1 audit handoff |
| `PROMOTION_COUNTS_v1.json` | no per-file record; group only | 297 / `c6056909e0ed89ef54e386d201f9adeeafe1af7169d5a90913268273b27eb206` | v2 handoff |
| `PROMOTION_PLAN_v1.csv` | no per-file record; group only | 1,241,747 / `a1eba3166318bb314c4ac3cb83d85d49b5e60b0bece6300a2fa74022d0197315` | v2 handoff |

The scan-side `-1,787` cannot be assigned to one of these files without
inventing a per-file baseline. Its exact aggregate is recorded, and the
current seven-file set is independently tied to the canonical profile
version. This is why the difference is accepted as a known scan-basis/EOL
representation delta rather than a hash mismatch.

### Known Special README difference

| path | expected size / SHA-256 | current size / SHA-256 | finding |
|---|---:|---:|---|
| `data/special2788/illustrious_tag_knowledge_base_2788_README.md` | 1,106 / `cb44a99237de588ee2b5934a265078c580dab587af48ebf195251e953a8df70c` | 1,146 / `691f896b37ad8eaaad76f0d22a111a0b6da852d96b76e190201e2c07c4476461` | previously recorded known README-only difference; not overwritten |

## Corruption and snapshot checks

- The four exact external source recoveries match their pinned SHA-256 values.
- The eight deterministic runtime-index outputs match their accident-before
  SHA-256 values.
- The three timing/metadata outputs are valid audited new-snapshot metadata.
- `data/runtime_index/` current total is exactly 2,989,206,293 bytes.
- `data/runtime_source/` and the three Japanese source files match their exact
  pinned source SHA-256 values.
- The only additional file is the separately rejected ThetaCursed Parquet;
  it is excluded and unused.
- No unique local loss is indicated by the differing groups. The only
  human-authored/semantic risk noted in prior assessment is provenance scope,
  not a current content mismatch.

## Gate decision before regression tests

The delta is fully closed as a known scan-basis/representation difference:

- missing: 0
- exact-target hash mismatch: 0
- unique local loss: 0
- alternate snapshot: 0
- unexpected modification/corruption evidence: 0
- known README difference: +40 bytes
- remaining +1,192: accounted for by the omitted-group and audit aggregate
  differences above

Therefore the functional recovery gate is open for the requested read-only
runtime/search regression and full pytest. This report will be amended with
the test results and the final gate after those tests complete.

## Regression tests

Pending at report creation. The following are permitted only after the audit
gate above:

- runtime index integrity;
- Stage 5 true AND search;
- Stage 6 recommendation/statistics;
- Japanese search;
- Special2788 lookup;
- alias/semantic resolution;
- Prompt generation;
- `python -m pytest -q`.

## Final state

Until the regression suite is recorded, the audit verdict is:

`FUNCTIONALLY_RESTORED_WITH_AUDITED_NEW_METADATA`

The final `PROTECTED_DATA_RECOVERY_COMPLETE` verdict is conditional on all
requested tests passing. No #35 completion, #49 start, or main merge is part
of this task.
