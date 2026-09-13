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

Completed sequential rows: 1-15,400 / 30,629 (50.28%)

- PROPOSED: 14,428
- UNRESOLVED: 972
- HIGH: 13,001
- MEDIUM: 1,427
- LOW: 972
- remaining: 15,229

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

Batch 20 audit重点:
- `june`〜`leather_bag` の1,000件を連続監査し、accepted pilot-v2 taxonomy と protected/canonical boundaries を維持
- J/K/L帯の cosplay / uniform / weapon / food / living / place / text-symbol は対象identityをmodifier断片より優先
- `kiss*` / `knee*` / `lace*` / `latex*` / `leaf*` / `leaning*` 系列は語幹一括ではなく対象・行為・状態を分離
- 素材単体の `lace` / `latex` / `leather` は衣服名へ押し込まず COLOR_APPEARANCE、`lace_background` は PLACE_BACKGROUND として境界再監査
- 固有イベント・作品固有概念・ミーム・組織名など、安全に確定できない122件はUNRESOLVEDに保持
- external evidence はこの1,000件では未使用
- direct binary blob経由で通常形式の単一 `.csv.xz` ledgerを保存
- canonical/Japanese overlay/Special/#66 UI/search/mainは変更しないcandidate-buildのみ

## Batch 21 attempt / blocked before formal checkpoint

- intended range: **15,401-16,400** (`leather_belt` -> `marble_phantasm`), 1,000 rows
- formal completed row remains **15,400**; this attempt produced no ledger/summary/MANIFEST checkpoint and must not be counted
- preflight re-read live `main`, Issue #64 latest comments, `PROTOCOL.md`, `MANIFEST.json`, `PROGRESS.md`, accepted pilot-v2 taxonomy, and the 1,000 canonical identities
- blocker: the frozen usage source required for ledger `post_count` is `data/source/danbooru-2026-09-02.csv`, fixed by the pilot code at SHA-256 `9b32d5ac0713ab252e7470ba6af9cb34de56878b6b3b13dfbbf6a4a37d82d95b`; that untracked/local source is not available through the connected GitHub worktree in this run
- a public historical dataset for the same date was identified, but the exact file bytes could not be downloaded in this execution environment to verify the required SHA-256; current/live counts were deliberately **not** substituted because that would create input drift
- classification work performed in-memory during this attempt is **not persisted or accepted**; next run must resume from row 15,401 and re-audit before formal persistence
- no production/canonical/Japanese overlay/Special/#66 UI/search/main mutation was made

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

Next unprocessed global row: **15,401**.
