# Issue #64 full rollout progress

Status: STAGING FINAL LEDGER / candidate build only / not production accepted.

Worker: ChatGPT (development-time classification/review). Codex paused after pilot revision 2.

Accepted basis: Issue #64 pilot revision 2, commit `5064429018123c80c32ac41af715668fb67fb74e`, DEV/AUDIT `PILOT_ACCEPTED`.

## Working set

- exact General population: 30,629 rows
- canonical row identity / resume source: `docs/issue64/artifacts/population.txt`
- historical working SHA-256: `58f9ff128a7ca21a17de4345c36c7891b8169a66fbe3d1de5c190cf48f17d51c`
- `post_count` is not required for the immutable rollout ledger

## Formal checkpoint

Formal checkpoint remains **1-30,400 / 30,629** until Batch 36 is present on the branch and MANIFEST is synchronized.

## Batch 36 staged result

Rows **30,401-30,629** (`yo-yo` -> `|_|`) were classified and audited:

- processed: **229**
- PROPOSED: **186**
- UNRESOLVED: **43**
- confidence: **140 HIGH / 46 MEDIUM / 43 LOW**
- intended ledger: `docs/issue64/full_rollout/batches/batch036_rows30401-30629_ledger.csv.xz`
- summary: `docs/issue64/full_rollout/batches/batch036_summary.json`
- raw CSV SHA-256: `8207c9d554f3598555847eace8e333da20d4075b40bedf6d4d4b34ac22317aa2`
- XZ SHA-256: `fca16c3c3d40c460cf02575a28646848e8ddfa74c3940663f065636b77427ddd`

Do not treat 30,629 as formal until MANIFEST is updated and reverified.
