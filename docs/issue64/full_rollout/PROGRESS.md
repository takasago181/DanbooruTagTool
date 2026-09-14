# Issue #64 full rollout progress

Status: IN PROGRESS / candidate build only / not production accepted.

Worker: ChatGPT (development-time classification/review). Codex paused after pilot revision 2.

Accepted basis: Issue #64 pilot revision 2, commit `5064429018123c80c32ac41af715668fb67fb74e`, DEV/AUDIT `PILOT_ACCEPTED`.

## Working set

- exact General population: 30,629 rows
- canonical row identity / resume source: `docs/issue64/artifacts/population.txt`
- historical local working CSV: `issue64_general_30629.csv`
- historical working columns: canonical / display_ja / search_ja / post_count
- historical working SHA-256: `58f9ff128a7ca21a17de4345c36c7891b8169a66fbe3d1de5c190cf48f17d51c`
- `post_count` is not a required field of the immutable rollout ledger under `PROTOCOL.md`; normal classification batches must not block merely because the frozen usage CSV is unavailable
- 7GB post/runtime index not used for this pass
- runtime LLM dependency: none

## Formal checkpoint

Completed sequential rows: **1-28,400 / 30,629 (92.72%)**

- PROPOSED: **26,300**
- UNRESOLVED: **2,100**
- HIGH: **23,732**
- MEDIUM: **2,568**
- LOW: **2,100**
- remaining: **2,229**
- next formal unprocessed global row: **28,401**

## Batch 33 — FORMAL

Rows **27,401-28,400** (`tiger_lily` -> `type_100_smg`) were classified, audited, persisted, and formally registered:

- processed: **1,000**
- PROPOSED: **903**
- UNRESOLVED: **97**
- confidence: **783 HIGH / 120 MEDIUM / 97 LOW**
- ledger: `docs/issue64/full_rollout/batches/batch033_rows27401-28400_ledger.csv.xz`
- summary: `docs/issue64/full_rollout/batches/batch033_summary.json`
- raw CSV SHA-256: `37e758d3170e62bdbf6fb9f124dc88a569f0803422203fae1454e10ec26bc886`
- XZ SHA-256: `defebed18ecb49001292da2e83e0cfac682810fb51a8d648168db024b7c96521`
- storage: Git data binary blob

## Batch 33 audit focus

- `tiger_*` / `torn_*` / `transparent_*` / `triangle_*` / `two-tone_*` were not classified by stem alone; object/concept identity remained primary.
- `torn_*` and `two-tone_*` route by the modified target (clothing/body/hair/object/etc.); only independent state/appearance concepts use the corresponding state/appearance genre.
- tattoo/symbol/UI/accessory/place/action boundaries were explicitly separated where the same modifier family crossed top-level genres.
- 97 work-specific events, memes, projects, brands, organizations, or otherwise ambiguous concepts remain explicit `UNRESOLVED`.
- historical usage / `post_count` was not used or substituted.
- canonical identity / production Japanese overlay / Special / #66 UI-search / main were not modified.

## Prior stop clarifications

- The earlier 20,401-21,400 attempt stopped without formal output when audit density could not be maintained. The same fixed 1,000 rows were later re-audited from the start and completed as formal Batch 26.
- The earlier attempt that stopped at row 15,400 treated unavailable historical `post_count` as a per-batch blocker. That stop condition is superseded by the routing correction recorded in Issue #64 and commit `3be2e2c1565e56362bdd445cab4d69eb75e84309`.
- Batch 31 was initially staged because safe atomic replacement of the minified one-line MANIFEST had not been completed. That blocker was resolved without reclassifying Batch 31.

## Rules

- accepted 17 top-level genres
- max path depth 2
- no visible catch-all
- beginner practical discovery path takes precedence over substring matching
- object identity takes precedence over modifier fragments
- keep pilot-v2 boundaries for role/clothing, sky/light, screen/composition, body/exposure
- ambiguous proper names/events/projects remain UNRESOLVED when evidence is insufficient
- canonical/Japanese overlay/Special data are not mutated during candidate build

## Persistence

- branch: `chatgpt/issue64-full-rollout`
- manifest: `docs/issue64/full_rollout/MANIFEST.json`
- immutable detailed ledgers: `docs/issue64/full_rollout/batches/`
- Batch 5+ summary JSON: `docs/issue64/full_rollout/batches/batchNNN_summary.json`
- past checkpointed batch files are not overwritten
- `PROGRESS.md` records the formal sequential stop point
- main is not updated until the full 30,629 candidate and audit are accepted

Recovery order:
1. `docs/project/CURRENT_STATE.md`
2. Issue #64 latest comments
3. `docs/issue64/full_rollout/PROTOCOL.md`
4. `docs/issue64/full_rollout/MANIFEST.json`
5. this `PROGRESS.md`
6. continue from row **28,401**
