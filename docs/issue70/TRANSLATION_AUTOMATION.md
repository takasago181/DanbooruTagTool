# Issue #70 translation automation

This document is the operating contract for the long-running Character /
Copyright / Artist Japanese overlay. The translation candidate is produced by
the worker, but queue state, identity, promotion, and completion are
deterministic and repository-backed.

## Current bootstrap checkpoint

- Source manifest: `docs/issue70/data/source_chunks_manifest.json`
- Population: 92,739 rows in 186 chunks (normally 500 rows; final chunk 239)
- Category counts: Character 35,890; Copyright 8,536; Artist 48,313
- Existing validated completed chunks: 21 / 186
- Existing validated completed rows: 10,500 / 92,739
- Existing status totals: `ACCEPTED_AI` 9,338; `REVIEW_REQUIRED` 1,162
- Remaining after bootstrap: 82,239 rows
- Durable queue state: `docs/issue70/data/queue_state.json`
- Final marker: `docs/issue70/data/final_completion.json` (must not exist until
  the full audit passes)

The numbers above are generated from result CSV validation, not copied from a
legacy lane checkpoint. Re-run `status` for the current numbers.

## Queue model

`queue_state.json` has one record per source chunk. Each record contains:

- `chunk_index`, first/last row number and first/last `row_id`
- `source_file`, `source_sha256`, and `row_count`
- `state`: `PENDING`, `CLAIMED`, `COMPLETED`, `RETRYABLE`, or
  `FAILED_VALIDATION`
- `claimed_by`, `claimed_at`, `heartbeat_at`, and `attempt_count`
- `result_path`, `result_sha256`, `accepted_count`, `review_count`, and
  `last_error`

The queue is dynamic. A worker claims the lowest available chunk; worker
numbers are not permanent partitions. A completed chunk is never claimed
again. A claim whose heartbeat is older than the configured lease is moved to
`RETRYABLE`. If a promoted queue result exists while the state update was
interrupted, the next queue operation validates it and repairs the state to
`COMPLETED`.

The previous four fixed lanes and five-worker operational assumption are
**obsolete**. Their result files and progress files remain as immutable
historical/provenance inputs and are not deleted or rewritten.

## Worker protocol

From the repository root:

```powershell
python scripts/issue70/queue_manager.py bootstrap
python scripts/issue70/queue_manager.py status
python scripts/issue70/queue_manager.py claim --worker-id worker-<unique-id>
```

`claim` returns exactly one source chunk by default. The worker reads the
returned `source_file`, creates a result CSV in a private staging path, and
keeps the claim alive for long work:

```powershell
python scripts/issue70/queue_manager.py heartbeat --worker-id worker-<unique-id> --chunk-index <N>
```

When the result is ready, promotion is the checkpoint boundary:

```powershell
python scripts/issue70/queue_manager.py complete --worker-id worker-<unique-id> --chunk-index <N> --result <staged.csv>
```

Promotion validates source hash, row count, row order, `row_id`,
`canonical_tag`, category, schema, duplicate identities, non-empty Japanese
display, and status totals before copying the result to the immutable
per-chunk queue result path and marking the chunk completed. Repeating the
same command after an interrupted state write is safe. A different result can
never overwrite an accepted result.

For a temporary worker failure, report and release the chunk:

```powershell
python scripts/issue70/queue_manager.py fail --worker-id worker-<unique-id> --chunk-index <N> --error "short diagnostic"
```

The outer ChatGPT Automation is only a trigger. It may start one worker per
run, but it is not a source of truth and its enabled/disabled state does not
partition or permanently remove queue capacity. Any surviving worker can
continue the queue.

## GitHub checkpoint protocol

The queue file and promoted result must be committed together. Before a push,
the worker must fetch the current `origin/main`, revalidate its source/result,
and replay its own change on the latest main. An unrelated main commit is
normal and does not cancel the worker. If the same queue/result identity was
changed by another worker, the rebase/push must fail closed and retry after
re-reading queue state; it must never overwrite or force-push.

The state file is the compare-and-swap record for claims. A successful push is
the durable claim/result checkpoint. Local process locking only covers two
workers in one checkout; Git's non-fast-forward rejection serializes workers
in separate checkouts.

Only Issue #70 data paths may be included in an automated translation
checkpoint commit:

- `docs/issue70/data/queue_state.json`
- `docs/issue70/data/results/queue/*.csv`
- `docs/issue70/data/final_completion.json` only for a passing final audit

An unrelated UI/data change on main must be preserved during rebase.

## Existing data migration

`bootstrap` validates every source chunk and discovers valid existing result
CSV files, including Manual Batch 001 and all legacy lane results. It computes
their current hashes and status totals and records them as `COMPLETED`. It
does not translate or rewrite them. Existing `progress.json` and
`progress_lane1.json` through `progress_lane4.json` are retained as migration
provenance only; their incomplete/partially missing counters are not used as
the new queue authority. Re-running `bootstrap` is idempotent and only repairs
an interrupted queue-result promotion.

## Translation policy

- Never change `canonical_tag`, `row_id`, category, source order, or source
  identity.
- Character: prefer an established Japanese name, using Copyright context and
  aliases only as evidence.
- Copyright: prefer an official or generally established Japanese title.
- Artist: do not meaning-translate a handle. Keep the original/native form
  when a reliable Japanese name is unavailable.
- Ambiguous or uncertain candidates are `REVIEW_REQUIRED`.
- Existing Japanese terms and co-occurrence evidence are evidence, not
  authority.
- Runtime remains local and non-LLM.

## Result schema

Result CSVs contain exactly:

`row_id,canonical_tag,category,display_ja,search_ja,translation_status,translation_note`

Allowed statuses are `ACCEPTED_AI` and `REVIEW_REQUIRED`. Accepted rows are
immutable.

## Audit and final completion

```powershell
python scripts/issue70/queue_manager.py audit
python scripts/issue70/queue_manager.py audit --write-final
```

The final marker command refuses to write unless all 186 chunks are
`COMPLETED` and the audit reports exactly 92,739 rows with:

- missing `row_id` = 0
- duplicate `row_id` = 0
- canonical mismatch = 0
- unexpected extra rows = 0
- result schema errors = 0
- accepted + review status counts equal covered rows

The final audit also rechecks the source manifest SHA and every result's
source identity and result hash. `final_completion.json` is therefore a
derived marker, not a manually editable progress flag.
