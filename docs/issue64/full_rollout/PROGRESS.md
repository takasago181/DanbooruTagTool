# Issue #64 full rollout progress

Status: IN PROGRESS / candidate build only / not production accepted.

Worker: ChatGPT (development-time classification/review). Codex paused after pilot revision 2.

Accepted basis: Issue #64 pilot revision 2, commit `5064429018123c80c32ac41af715668fb67fb74e`, DEV/AUDIT `PILOT_ACCEPTED`.

## Working set

- exact General population: 30,629 rows
- local working CSV: `issue64_general_30629.csv`
- columns: canonical / display_ja / search_ja / post_count
- SHA-256: `58f9ff128a7ca21a17de4345c36c7891b8169a66fbe3d1de5c190cf48f17d51c`
- 7GB post/runtime index not used for this pass
- runtime LLM dependency: none

## Checkpoint 2026-09-13 JST

Completed sequential rows: 1-4,300 / 30,629 (14.04%)

- PROPOSED: 4,190
- UNRESOLVED: 110
- HIGH: 3,732
- MEDIUM: 458
- LOW: 110
- remaining: 26,329

Batches:

- 1-500: 484 proposed / 16 unresolved
- 501-1,300: 783 proposed / 17 unresolved
- 1,301-2,300: 974 proposed / 26 unresolved
- 2,301-3,300: 982 proposed / 18 unresolved
- 3,301-4,300: 967 proposed / 33 unresolved

Batch 5 audit重点:
- `brown_*`, `bra*`, `breast_*`, `branch`, `burning_*` の部分一致誤爆を補正
- 対象identityを色・文字断片より優先
- 身体の「揺れ」はPOSE_MOVEMENT、拘束/接触はACTION_CONTACT、衣服からの露出はCLOTHING_STATE_EXPOSUREへ分離
- 物理的な印刷物はOBJECT_PROP主 + TEXT_SYMBOL副
- 特殊器具はDAILYへ無理に押し込まない
- 固有イベント・ブランド・意味不明語33件はUNRESOLVEDのまま保持

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
- immutable detailed ledgers: `docs/issue64/full_rollout/batches/*.csv.xz`
- batch 5+ summary JSON: `docs/issue64/full_rollout/batches/batchNNN_summary.json`
- past batch files are not overwritten; corrections are recorded as later review/correction artifacts
- PROGRESS.md records the current sequential stop point
- Issue #64 records major checkpoints and review gates
- main is not updated until the full 30,629 candidate and audit are accepted

Recovery order for a new chat:

1. `docs/project/CURRENT_STATE.md`
2. Issue #64 latest comments
3. `docs/issue64/full_rollout/PROTOCOL.md`
4. `docs/issue64/full_rollout/MANIFEST.json`
5. this `PROGRESS.md`

Next unprocessed global row: **4,301**.
