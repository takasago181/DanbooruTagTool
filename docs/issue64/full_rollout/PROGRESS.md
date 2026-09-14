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

Completed sequential rows: **1-26,400 / 30,629 (86.19%)**

- PROPOSED: **24,475**
- UNRESOLVED: **1,925**
- HIGH: **22,116**
- MEDIUM: **2,359**
- LOW: **1,925**
- remaining: **4,229**
- next formal unprocessed global row: **26,401**

## Batch 31 — FORMAL

Rows **25,401-26,400** (`sports_bra_peek` -> `surgeon_cuffs`) were classified, audited, persisted, and formally registered:

- processed: **1,000**
- PROPOSED: **919**
- UNRESOLVED: **81**
- confidence: **878 HIGH / 41 MEDIUM / 81 LOW**
- ledger: `docs/issue64/full_rollout/batches/batch031_rows25401-26400_ledger.csv.xz`
- summary: `docs/issue64/full_rollout/batches/batch031_summary.json`
- raw CSV SHA-256: `a007704975c45c8605f7eb77f4e973f9c3f83eff2a1fff570350ab9bcc93a4fd`
- XZ SHA-256: `1d024337547e7f94736c618378041a84e4f85a53194bd67e354ec783a10ff713`
- storage: Git data binary blob

The prior staged-state blocker is resolved. The complete existing `MANIFEST.json` blob was retrieved, Batch 1-30 entries were preserved, and Batch 31 was appended without reclassification or rewriting older batch records. `MANIFEST.json`, Batch 31 summary, ledger hashes, and this `PROGRESS.md` now target the same final row 26,400.

## Batch 31 audit focus

- `sports_*` / `star_*` / `stomach_*` / `striped_*` / `stuffed_*` / `sun_*` / `super_*` were not classified by stem alone; object/concept identity remained primary.
- `star_(sky)` / `star_(symbol)`, `sun` / `sun_symbol`, and `steam` / `steam_censor` preserve sky/light/symbol/style boundaries.
- `striped_*` routes by the modified object (clothing/body/background/etc.); only independent pattern concepts go to `COLOR_APPEARANCE`.
- 81 work-specific events, memes, projects, brands, transformations, or otherwise ambiguous concepts remain explicit `UNRESOLVED`.
- historical usage / `post_count` was not used or substituted.
- canonical identity / production Japanese overlay / Special / #66 UI-search / main were not modified.

## Prior stop clarifications

- The earlier 20,401-21,400 attempt stopped without formal output when audit density could not be maintained. The same fixed 1,000 rows were later re-audited from the start and completed as formal Batch 26.
- The earlier attempt that stopped at row 15,400 treated unavailable historical `post_count` as a per-batch blocker. That stop condition is superseded by the routing correction recorded in Issue #64 and commit `3be2e2c1565e56362bdd445cab4d69eb75e84309`.
- Batch 31 was initially staged because safe atomic replacement of the minified one-line MANIFEST had not been completed. That blocker is now resolved without reclassifying Batch 31.

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
6. continue from row **26,401**
