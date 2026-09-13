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

## Checkpoint 2026-09-14 JST

Completed sequential rows: 1-21,400 / 30,629 (69.87%)

- PROPOSED: 19,927
- UNRESOLVED: 1,473
- HIGH: 17,909
- MEDIUM: 2,018
- LOW: 1,473
- remaining: 9,229

Batches:

- 1-500: 484 proposed / 16 unresolved
- 501-1,300: 783 proposed / 17 unresolved
- 1,301-2,300: 974 proposed / 26 unresolved
- 2,301-3,300: 982 proposed / 18 unresolved
- 3,301-4,300: 967 proposed / 33 unresolved
- 4,301-5,300: 963 proposed / 37 unresolved
- 5,301-5,500: 196 proposed / 4 unresolved
- 5,501-5,700: 190 proposed / 10 unresolved
- 5,701-5,900: 181 proposed / 19 unresolved
- 5,901-6,900: 939 proposed / 61 unresolved
- 6,901-7,900: 931 proposed / 69 unresolved
- 7,901-8,900: 929 proposed / 71 unresolved
- 8,901-9,900: 953 proposed / 47 unresolved
- 9,901-10,900: 906 proposed / 94 unresolved
- 10,901-11,150: 245 proposed / 5 unresolved
- 11,151-12,150: 908 proposed / 92 unresolved
- 12,151-13,150: 932 proposed / 68 unresolved
- 13,151-13,400: 216 proposed / 34 unresolved
- 13,401-14,400: 871 proposed / 129 unresolved
- 14,401-15,400: 878 proposed / 122 unresolved
- 15,401-16,400: 893 proposed / 107 unresolved
- 16,401-17,400: 897 proposed / 103 unresolved
- 17,401-18,400: 898 proposed / 102 unresolved
- 18,401-19,400: 948 proposed / 52 unresolved
- 19,401-20,400: 940 proposed / 60 unresolved
- 20,401-21,400: 923 proposed / 77 unresolved

## Batch 26 audit重点

- `pinstripe_skirt`〜`pumpkin_ornament` の1,000件を連続監査し、accepted pilot-v2 taxonomy と protected/canonical boundaries を維持
- `pinstripe*` / `plaid*` / `polka_dot*` / `print*` は柄modifierで一括せず、衣服・背景・髪・物体・画面枠など対象identityを主経路に分類
- `pokemon*` / `pov*` / `power*` / `public*` は語幹一括せず、生物・衣装・物体・行為・構図・身体・画面表現等へ意味分離
- 固有イベント・作品固有概念・ミーム・ブランド・抽象語など、安全に実用経路を確定できない77件はUNRESOLVEDに保持
- historical usage / `post_count` は通常ledger必須でないため未使用。global row identity/orderは固定 `population.txt` を使用
- external evidence はこの1,000件では未使用
- direct Git data binary blob経由で通常形式の単一 `.csv.xz` ledgerを保存
- canonical/Japanese overlay/Special/#66 UI/search/mainは変更しないcandidate-buildのみ

## Prior Batch 26 quality stop clarification

前回の20,401–21,400 attemptは実行予算内で監査密度を維持できず、正式成果を保存せず20,400で停止した。今回、同じ固定1,000件を先頭から再監査し、未完成の前回分類は再利用せず正式Batch 26として完成させた。

## Prior Batch 21 blocker clarification

The earlier attempt that stopped at row 15,400 treated unavailable historical `post_count` as a per-batch blocker. That stop condition is superseded by the routing correction already recorded in Issue #64 and commit `3be2e2c1565e56362bdd445cab4d69eb75e84309`: `PROTOCOL.md` requires canonical + classification status + primary/secondary path + confidence, and the fixed row identity/order source is `docs/issue64/artifacts/population.txt`.

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

Detailed row-level results are persisted directly in this GitHub work branch.

- branch: `chatgpt/issue64-full-rollout`
- manifest: `docs/issue64/full_rollout/MANIFEST.json`
- immutable detailed ledgers: `docs/issue64/full_rollout/batches/`
- normal batches may use `.csv.xz`; connector-limited batches may use ordered `.xz.b64.partNNN` text fragments with exact reconstruction hashes in MANIFEST
- batch 5+ summary JSON: `docs/issue64/full_rollout/batches/batchNNN_summary.json`
- past checkpointed batch files are not overwritten; corrections are recorded as later review/correction artifacts
- PROGRESS.md records the current sequential stop point
- Issue #64 records major checkpoints and review gates
- main is not updated until the full 30,629 candidate and audit are accepted

Recovery order for a new chat:

1. `docs/project/CURRENT_STATE.md`
2. Issue #64 latest comments
3. `docs/issue64/full_rollout/PROTOCOL.md`
4. `docs/issue64/full_rollout/MANIFEST.json`
5. this `PROGRESS.md`

Next unprocessed global row: **21,401**.
