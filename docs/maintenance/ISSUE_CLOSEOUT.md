# Issue closeout and cleanup

Record disposition at the Issue/PR checkpoint before closing substantial work.
This is ownership/recovery evidence, not permission to delete another chat's work.

| Surface | Closeout decision |
| --- | --- |
| Product/data | accepted semantic/domain owner; remaining Issue-named code and its retirement condition |
| Tests | current regression retained, equivalent replacement, or frozen reproduction oracle |
| Scripts | shared Maintenance/tooling, research replay, or archive with source SHA/hash |
| Workflow | current semantic CI, owned manual KNOWLEDGE workflow, or disabled historical registry + recovery |
| Branch | merged HEAD reachable from main, LKG/provenance retention, or unique/unmerged recovery reason |
| Worktree | owner, meaningful tracked/untracked/ignored assets, recovery and safe retirement |
| Evidence | authority vs generated runtime vs research vs historical evidence vs test oracle |
| Routing | remove completed lane from cold-start route; keep historical checkpoint link |

Use `workspace_task.ps1 -Action Finish -Issue N` for owner-controlled retirement.
It refuses dirty/ignored/unmerged content; preserve/review it rather than bypassing
with force/reset/clean. App-managed checkouts require their owning task's lifecycle.
Do not infer disposable status from closed Issue, detached HEAD, age or file count.

Delete remote refs only after ownership and exact ancestry/recovery proof. Use an
expected old SHA lease to refuse concurrent branch updates; save the original SHA
and `git push origin <SHA>:refs/heads/<branch>` recovery command. A squash-merged
or unique branch is not automatically safe. Keep research/KNOWLEDGE branches when
their independent assets are not fully represented in main.

Closed-Issue write automation must have an explicit current owner or be disabled.
Keep workflow ID/prior state and `gh workflow enable <id>` rollback. Archive YAML
before removing it; current semantic CI must retain unique checks, fail failures,
cancel superseded runs and use bounded artifact retention. Foundation Batch B's
ledger is an example, not a new default batch-deletion script.
