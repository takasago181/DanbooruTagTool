# Dictionary Validation Ledger Storage Policy

Issue: #32

## Decision
Use append-only 20-Special result blocks as the authoritative Special-level checkpoint ledger.

Path pattern:
`validation_quarantine/results_blocks/NNNN_MMMM.csv`

Each block:
- contains exactly one header plus up to 20 Special result rows;
- is created once after that checkpoint is complete;
- is not rewritten during ordinary forward progress;
- keeps its historical rule version and verdicts;
- may be superseded only by explicit revalidation records, never silently edited to pretend a later rule was used.

`RESULT_LEDGER_INDEX.csv` lists completed block files and is the navigation index.

## Legacy consolidated file
`validation_quarantine/results.csv` is retained as a compatibility/consolidated snapshot through sequence 60. It is no longer the per-20 write target. It may be rebuilt at external batch/finalization boundaries if useful, but the append-only block ledger is authoritative for checkpoint history.

## Why
GitHub's content update API replaces whole files. Rewriting a single growing results CSV every 20 Specials becomes slower, increases stale-write conflicts, and raises corruption/omission risk across 2,788 rows. Append-only blocks keep each checkpoint small and immutable.

## Other ledgers
- `candidate_fixes.csv`: small cross-cutting candidate ledger; update only when findings change.
- `semantic_support_results.csv`: 58-row frozen sidecar coverage ledger; small enough to remain consolidated.
- `revalidation_queue.csv`: queue/state ledger; update when rule/evidence changes require backfill.
- `progress.json` and `handoff.md`: small mutable checkpoint pointers; always fetch latest SHA before write.

## Automation rule
Scheduled/manual runs must:
1. read `progress.json` and `RESULT_LEDGER_INDEX.csv`;
2. create only the next missing 20-row result block;
3. then update the small progress/handoff/index files;
4. never overwrite an existing block during normal continuation;
5. stop and reconcile on any stale-write or unexpected existing-block conflict.
