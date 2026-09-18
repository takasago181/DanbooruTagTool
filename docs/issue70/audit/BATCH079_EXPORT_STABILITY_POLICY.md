# Issue #70 batch079 exporter stability checkpoint

## Active workflow

Only this exporter workflow is active for batch079 candidate generation:

- `.github/workflows/issue70_export_external_batch079_candidates_v7.yml`

The failed v1-v6 workflow definitions are removed. Do not create v8/v9/etc. Fix v7 in place if a future correction is needed.

## Authoritative inputs

The exporter must use only:

1. `EXTERNAL_QUEUE_LIVE.csv` for the root external population, category, canonical tag, post count, and current display/search values.
2. `external_resolution_*.csv` for concrete resolved row_ids.
3. `EXTERNAL_PROGRESS_LIVE.json` for invariant cross-checks.

Historical audit CSVs are not used to reconstruct category or unresolved membership.

## Reliability rules

- No category inference from filenames.
- No scanning `copyright_*.csv`, `character_*.csv`, `artist_*.csv`, `identity_safe_*.csv`, or candidate exports to reconstruct the queue.
- Candidate generation is diagnostic/read-only for production/runtime.
- If the branch advances during a run, stale candidate publishing is skipped successfully instead of producing a push race failure.
- The workflow uses one concurrency group with `cancel-in-progress: true`.

## Production safety

This does not modify production translation data, runtime catalog, main, or PR merge state.
