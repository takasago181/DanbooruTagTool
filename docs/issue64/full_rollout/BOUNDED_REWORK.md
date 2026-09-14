# Issue #64 bounded rollout rework

This rework supersedes damaged or inconsistent candidate artifacts without rewriting historical ledgers, summaries, taxonomy, or canonical source data. It recovers only the 1,200 rows whose Batch 9 and Batch 17 persisted ledgers cannot be decoded. It does not rerun LLM classification across the 30,629-row population.

## Effective output

`effective_sidecar.csv` is the single effective 30,629-row candidate. The correction manifest records its hash and traces every recovery, reindex, path correction, and targeted semantic correction. `effective_batch_summaries.json` is regenerated from the effective rows; the Batch 16 ledger remains authoritative and its historical summary is preserved unchanged.

The rework also:

- reindexes 198 surviving Batch 8 decisions by canonical identity, records two duplicate decisions, and explicitly recovers its two missing edge rows;
- replaces the two unreadable 1,200-row ledger ranges with the bounded review CSV, retaining 125 ambiguous rows as `UNRESOLVED` / `LOW`;
- corrects 721 Batch 34 rows that used 52 subgenre IDs absent from accepted pilot-v2, mapping only reviewed direct aliases and otherwise keeping the accepted top-level genre;
- records 77 targeted semantic corrections, including the reviewed relation/contact and image-cropping patterns, without adding taxonomy nodes. The fresh risk sample also moved `studio_microphone` to objects/equipment and `vocaloid_boxart_pose` to pose; clothing tags such as `cropped_hoodie` remain clothing;
- records the local working-source CSV hash separately from `population.txt`: the former is a richer UTF-8-SIG CSV, while the latter is the sorted canonical-only UTF-8/LF identity list. Their bytes differ, but the locally available CSV hash and canonical sequence match the manifest and fixed population.

## Rebuild and verify

From the repository root, run:

```powershell
python tools/issue64_full_rollout_rework.py
python tools/issue64_full_rollout_validate.py --effective --report docs/issue64/full_rollout/audit/effective_integrity_report.json
python -m pytest -q -p no:cacheprovider --basetemp .pytest_issue64_bounded tests/test_issue64_full_rollout_validate.py
```

The final effective audit reports 30,629 ordered unique rows, 36 covered batches, no invalid taxonomy paths, 28,226 proposed rows, and 2,403 explicit unresolved rows. The 1,200-row recovery membership and the 721-row Batch 34 correction coverage are checked by the validator.

## Final bounded semantic gate

The latest live DEV review was Issue #64 comment `5660957158` on branch head `ad1461fc01cfbfc438692020e139d01d8aff2edd`. It required persisting and resolving only the remaining risk candidates; no full-population semantic reread was requested or performed.

The complete materialized residual list is `corrections/residual_candidate_review.csv` (76 canonical entries): 48 relation/contact candidates from the prior correction rule and its adjacent controls, all 25 Batch 34 `water_*` entries, the named `2011` and `father's_day` temporal/event candidates, and `two-tone_leg_warmers`. The generator fails closed if the list changes size, duplicates a canonical, drifts from its expected pre-review state, or declares a KEEP while changing a row.

Disposition:

- **68 KEEP**: relation/contact routes follow the accepted boundary; water-prefixed rows are judged by target identity, not by their shared prefix.
- **2 RECLASSIFY**: `two-tone_leg_warmers` → `CLOTHING`; `water_drop_hair_ornament` → `CLOTHING/ACCESSORY`.
- **6 UNRESOLVED**: `2011`, `father's_day`, `water_drop`, `water_on_glass`, `water_stream`, and `water_type_theme_(pokemon)`. These lack a safe route in the accepted shallow taxonomy; no taxonomy node was added.

The two-tone placement follows the accepted clothing-object-first boundary, supported by a Danbooru example tagging the garment as `two-tone leg warmers` alongside `leg warmers` ([Danbooru post](https://safebooru.donmai.us/posts/11946290)). The hair ornament follows the accepted taxonomy's explicit HAIR_FACE boundary. The `water_censor` entry remains a screen/censorship effect under `STYLE_QUALITY_META`; its meaning is consistent with the existing visual-effect route ([tag explanation](https://www.hoshikou-ailabo.net/blog/2024/09/28/hidden-tags/)). No ambiguous water rows were forced into a neighboring genre.

Final output SHA-256: `a118f5f904c38cee5b63f0c83b06a56f50ee8afdb623c52eb354731bc0b846d9`.

Final counts: `PROPOSED 28,226 / UNRESOLVED 2,403`; confidence `HIGH 25,097 / MEDIUM 3,129 / LOW 2,403`. The full effective validator passes with 30,629 rows, zero missing/extra/duplicate canonicals, zero invalid paths, source hash PASS, and no warnings/errors. Focused tests: 10 passed.

**Final verdict: `ACCEPT_FOR_PRODUCTION_INTEGRATION`.** This is the DEV-side final bounded review verdict for the effective candidate, pending review of the clean integration branch. It does not merge, close Issue #64, or start #66 UI/catalog integration.

## Clean integration candidate boundary

Prepare the candidate from latest live `main` `3f4e47d7331809b2e6a234824799fb3bc179bae8`. Promote only the accepted taxonomy, final effective sidecar, concise provenance/validation, focused contract validation, and the minimal proposed management routing sync. Keep historical batch ledgers and the large rework/audit tree on this branch. Do not include #66 app implementation changes, and do not merge or close #64.
