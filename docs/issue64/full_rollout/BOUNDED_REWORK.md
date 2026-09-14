# Issue #64 bounded rollout rework

This rework supersedes damaged or inconsistent candidate artifacts without rewriting historical ledgers, summaries, taxonomy, or canonical source data. It recovers only the 1,200 rows whose Batch 9 and Batch 17 persisted ledgers cannot be decoded. It does not rerun LLM classification across the 30,629-row population.

## Effective output

`effective_sidecar.csv` is the single effective 30,629-row candidate. The correction manifest records its hash and traces every recovery, reindex, path correction, and targeted semantic correction. `effective_batch_summaries.json` is regenerated from the effective rows; the Batch 16 ledger remains authoritative and its historical summary is preserved unchanged.

The rework also:

- reindexes 198 surviving Batch 8 decisions by canonical identity, records two duplicate decisions, and explicitly recovers its two missing edge rows;
- replaces the two unreadable 1,200-row ledger ranges with the bounded review CSV, retaining 125 ambiguous rows as `UNRESOLVED` / `LOW`;
- corrects 721 Batch 34 rows that used 52 subgenre IDs absent from accepted pilot-v2, mapping only reviewed direct aliases and otherwise keeping the accepted top-level genre;
- records 69 targeted semantic corrections, including the reviewed relation/contact and image-cropping patterns, without adding taxonomy nodes. The fresh risk sample also moved `studio_microphone` to objects/equipment and `vocaloid_boxart_pose` to pose; clothing tags such as `cropped_hoodie` remain clothing;
- records the local working-source CSV hash separately from `population.txt`: the former is a richer UTF-8-SIG CSV, while the latter is the sorted canonical-only UTF-8/LF identity list. Their bytes differ, but the locally available CSV hash and canonical sequence match the manifest and fixed population.

## Rebuild and verify

From the repository root, run:

```powershell
python tools/issue64_full_rollout_rework.py
python tools/issue64_full_rollout_validate.py --effective --report docs/issue64/full_rollout/audit/effective_integrity_report.json
python -m pytest -q -p no:cacheprovider --basetemp .pytest_issue64_bounded tests/test_issue64_full_rollout_validate.py
```

The current effective audit reports 30,629 ordered unique rows, 36 covered batches, no invalid taxonomy paths, 28,232 proposed rows, and 2,397 explicit unresolved rows. The 1,200-row recovery membership and the 721-row Batch 34 correction coverage are checked by the validator.

This is a fresh structural and bounded-correction audit for DEV review. It does not itself accept the taxonomy rollout, update management state, merge a branch, or authorize Issue #66 integration.
