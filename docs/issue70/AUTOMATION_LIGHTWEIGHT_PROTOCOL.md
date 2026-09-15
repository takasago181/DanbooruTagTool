# Issue #70 ChatGPT Automation lightweight protocol

This protocol exists only to make the repository-backed Issue #70 translation queue usable from ChatGPT Automation, where reading a 500-row source CSV or repeatedly compare-and-swapping the large central `queue_state.json` is unreliable.

It does **not** change translation policy, row identity, completed results, the 92,739-row population, or final coverage requirements.

## Source transport

The original 500-row files in `docs/issue70/data/source_chunks/` remain authoritative and are never rewritten.

A generated transport layer lives under:

- `docs/issue70/data/source_shards/`
- `docs/issue70/data/source_shards_manifest.json`

Each normal 500-row source chunk is represented by ten compact 50-row shards. The final 239-row chunk has five shards. Shards retain only the evidence needed for translation:

- `row_id`
- `canonical_tag`
- `category`
- `category_name`
- `source_aliases`
- `verified_aliases`
- `existing_display_ja`
- `existing_search_ja`
- `existing_candidate_ja`
- `existing_rejected_ja`
- top 3 related copyright identities

The shard manifest records the original source file/hash, shard paths/hashes, row counts and first/last `row_id`. A worker must concatenate shards in shard order and validate the resulting 500-row identity sequence before translating.

The compact shards are generated mechanically by `scripts/issue70/build_compact_shards.py`. They are transport artifacts, not a new semantic source of truth.

## Lightweight claim protocol

ChatGPT Automation workers do not mutate `queue_state.json` when claiming work.

A claim is the atomic creation of:

`docs/issue70/data/automation_claims/chunk_NNN.json`

with at least:

- `chunk_index`
- `worker_id`
- `claimed_at`
- `source_manifest_sha256`
- `source_shards_manifest_sha256`

GitHub's create-file operation is the compare-and-swap boundary: only one worker can create a previously absent claim path. If creation fails because the path now exists, the worker must choose another pending chunk.

A worker determines pending work from:

1. `docs/issue70/data/automation_bootstrap.json` immutable completed chunk list at rollout,
2. immutable result files already present under `docs/issue70/data/results/queue/`,
3. active claim files under `docs/issue70/data/automation_claims/`.

The rollout bootstrap is generated from the validated `queue_state.json`; it must report exactly 21 completed chunks / 10,500 completed rows at this migration point.

## Stale claims

A claim older than 120 minutes may be recovered after the worker verifies that no immutable result exists for that chunk. The stale claim is deleted using its current blob SHA, then a new create-file claim is attempted. Never overwrite a live claim.

A worker that fails before promotion must delete its own claim when possible. If it crashes, stale recovery handles it later.

## Completion / promotion

The worker reads all compact shards for its claimed chunk and produces one ordinary 500-row result CSV using the existing result schema:

`row_id,canonical_tag,category,display_ja,search_ja,translation_status,translation_note`

The worker must validate:

- source-shard manifest hash
- every shard hash
- total row count
- first/last `row_id`
- `row_id`, `canonical_tag`, category and order
- no duplicate identity
- non-empty `display_ja`
- status is only `ACCEPTED_AI` or `REVIEW_REQUIRED`
- accepted + review = chunk row count

Promotion is the immutable creation of:

`docs/issue70/data/results/queue/queue_chunkNNN_<first>_<last>.csv`

If that result path already exists, it must be treated as completed after validation and must never be overwritten.

After successful immutable result creation, delete the worker's claim file. This means the large central `queue_state.json` is not a required write path for ChatGPT Automation.

## Reconciliation

`queue_state.json` remains the deterministic local/Codex queue representation used by `queue_manager.py`, but it is no longer the remote Automation claim CAS boundary.

The queue manager's bootstrap/audit can rediscover valid result CSVs and reconcile them later. Final completion still requires the existing full 92,739-row audit against the original source manifest. Compact shards cannot create `final_completion.json` by themselves.

## Worker rule

ChatGPT Automation performs the actual Japanese translation. Codex is not the translator in this protocol.

A worker processes at most one 500-row chunk per scheduled run, reading that chunk as compact 50-row shards, and promotes exactly one immutable result.
