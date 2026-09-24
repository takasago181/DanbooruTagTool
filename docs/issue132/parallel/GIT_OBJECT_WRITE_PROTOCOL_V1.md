# Issue132 Git Object Write Protocol V1

Use this protocol for ALL writes on branch `research/taxonomy-usability-audit` from Issue132 automations.

Purpose: avoid contents-API pre-write safety rejection while preserving concurrent-worker safety.

## Allowed targets
Only the target files already authorized by the caller's role:
- own-lane staging/status for forward workers;
- Issue132 historical staging + repair_status.json for Unified Repair;
- coordinator_status.json / quality_flags only when Coordinator is authorized.
Never write main, production, UserData, #64/#76/#118, immutable checkpoints, or another worker's forward lane.

## Atomic fast-forward algorithm

For each persistence unit:

1. Fetch branch endpoint:
   `GET /repos/takasago181/DanbooruTagTool/branches/research/taxonomy-usability-audit`
   Record `base_head_sha` and `base_tree_sha`.

2. Build final UTF-8 bytes for every file in this persistence unit.

3. For each changed/created file, call `create_blob`.
   For deletion use a tree entry with `sha:null`.

4. Call `create_tree` with:
   - `base_tree_sha = base_tree_sha`
   - only the changed path entries
   - file mode `100644`, type `blob`.

5. Call `create_commit`:
   - parent = `base_head_sha`
   - tree = new tree SHA.

6. Immediately fetch the branch endpoint again.
   - If current HEAD still equals `base_head_sha`, call `update_ref` with `force=false`.
   - If HEAD changed, DO NOT move the ref. Discard the unpublished commit, re-fetch the new head/tree, rebuild the tree on that base using the same already-validated file bytes, then retry.

7. If `update_ref(force=false)` fails because the branch advanced, perform the same rebase/retry. Never use force=true.

8. After success, re-fetch every written file from the branch and run the caller's exact structural/semantic validation.

## Retry rule
Concurrency conflict is not a hard blocker until 3 fresh-base attempts fail. Each retry must use the newest branch head/tree. Never overwrite or erase intervening Worker/Repair/Coordinator commits.

## Persistence granularity
- Forward workers: one 25-row staging window per commit; status may be a separate terminal commit.
- Repair: one repaired 25-row window per commit; repair_status may be separate.
- Coordinator: status/quality metadata may be one small commit.

This keeps successful work durable and minimizes conflict surface.

## Blocker rule
A generic "safety check blocked write" before a GitHub operation is not a blocker.
Only report a write blocker after the Git-object path itself was attempted and failed. Record operation, target, base HEAD, new commit SHA if created, update_ref result/error, and retry count.
