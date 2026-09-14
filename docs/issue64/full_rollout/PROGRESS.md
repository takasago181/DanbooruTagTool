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

Completed sequential rows: **1-27,400 / 30,629 (89.46%)**

- PROPOSED: **25,397**
- UNRESOLVED: **2,003**
- HIGH: **22,949**
- MEDIUM: **2,448**
- LOW: **2,003**
- remaining: **3,229**
- next formal unprocessed global row: **27,401**

## Batch 32 — FORMAL

Rows **26,401-27,400** (`surgeonfish` -> `tiger_ii`) were classified, audited, persisted, and formally registered:

- processed: **1,000**
- PROPOSED: **922**
- UNRESOLVED: **78**
- confidence: **833 HIGH / 89 MEDIUM / 78 LOW**
- ledger: `docs/issue64/full_rollout/batches/batch032_rows26401-27400_ledger.csv.xz`
- summary: `docs/issue64/full_rollout/batches/batch032_summary.json`
- raw CSV SHA-256: `abb8967a6252c933db2dec13bd7e81fc1a0c961e6cccf67f94f0c16f7ab5b558`
- XZ SHA-256: `c084637eb9dedbbc51e8869e2289d29c209351090cd3574708974cb7d203a38b`
- storage: Git data binary blob

## Batch 32 audit focus

- `sword_*` / `tail_*` / `tentacle_*` / `thigh_*` / `tied_*` were not classified by stem alone; object/body/action/clothing-state identity remained primary.
- `team_*` group/role identity was separated from corresponding `*_uniform` clothing entries.
- `taurus_(constellation)` / `taurus_(symbol)` / `taurus_(zodiac)`, tarot arcana, flags, and text entries preserve sky/symbol/text boundaries rather than sharing a lexical route.
- 78 work-specific events, memes, projects, brands, transformations, or otherwise ambiguous concepts remain explicit `UNRESOLVED`.
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
6. continue from row **27,401**
