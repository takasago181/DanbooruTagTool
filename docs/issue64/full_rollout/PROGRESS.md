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

Completed sequential rows: **1-29,400 / 30,629 (95.99%)**

- PROPOSED: **27,164**
- UNRESOLVED: **2,236**
- HIGH: **24,495**
- MEDIUM: **2,669**
- LOW: **2,236**
- remaining: **1,229**
- next formal unprocessed global row: **29,401**

## Batch 34 — FORMAL

Rows **28,401-29,400** (`type_10_(tank)` -> `waving_hands`) were classified, audited, persisted, and formally registered:

- processed: **1,000**
- PROPOSED: **864**
- UNRESOLVED: **136**
- confidence: **763 HIGH / 101 MEDIUM / 136 LOW**
- ledger: `docs/issue64/full_rollout/batches/batch034_rows28401-29400_ledger.csv.xz`
- summary: `docs/issue64/full_rollout/batches/batch034_summary.json`
- raw CSV SHA-256: `4be1a11f64d64b8ecc682265a8e22d4040ff3f64b4f4c3b6e08278ce4d770dc3`
- XZ SHA-256: `bbbf4fd74559e1c092b2e8c722d9d663cf3c2c96df8a90b7875765ed2c47e943`
- storage: Git data binary blob

## Batch 34 audit focus

- `under_*` / `vampire_*` / `viewer_*` / `waist_*` / `water_*` were not classified by stem alone; object/concept identity remained primary.
- `vampire_bite` was corrected to `ACTION_CONTACT/contact` rather than being pulled into creature classification by the `vampire_*` stem.
- `very_big_eyes` / `very_hairy` were corrected to face/body identity paths rather than expression/hair-style shortcuts.
- role concepts without a safe accepted pilot-v2 path (`waiter`, `waitress`, `warrior`, `viking`, `voice_actor`, `virtual_youtuber`, etc.) remain explicit `UNRESOLVED` rather than being forced into metadata.
- explicit `_(style)` tags use `STYLE_QUALITY_META/style`; explicit `_(cosplay)` tags use `CLOTHING/dresses_outfits`.
- ambiguous work-specific events, memes, projects, organizations, transformations, or otherwise unsafe concepts remain `UNRESOLVED`.
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
6. continue from row **29,401**
