## #255 decision: NO ACTION / history rewrite unnecessary

Post-#264 main `76269b8c69f772cae25435b460928da4f1745f90`:
- Current tracked tree: 970 blobs / 73,739,581 bytes (~70.3 MiB), versus the earlier ~323 MB active-tree baseline. Batch B already removed 259,721,312 active-tree bytes with remote recovery tag/hash ledger.
- GitHub repository metadata: 147,062 KB (~143.6 MiB). Incremental fetch completes in ~1s and checkout/switch in well under a second; no evidence of clone/fetch/checkout blocking normal work. A redundant network full clone is unnecessary for this decision.
- Common local `.git`: 1,110,678,253 bytes; `git count-objects`: 335.81 MiB packed, 395.76 MiB loose, 308.22 MiB in 21 temporary-object files, 737 prune-packable objects. This includes retained local refs/recovery state and avoidable local storage; it is not GitHub clone size. No gc/prune/repack/temp-object deletion was run.
- Largest reachable blob: 47,698,225 bytes, historical JSONL audit evidence; other top objects are CSV/JSONL and compressed research evidence. No >100MB reachable blob or large executable/DB dependency demonstrated. Reachable all-ref history 8,095 commits / 270 local+remote branch refs is provenance, not a rewrite reason.

Expected rewrite benefit is unproven; local ordinary GC/storage maintenance could address local object overhead separately if it becomes a practical problem, without renumbering history. Existing active-tree archive already addresses the measured burden. Reuse the Batch A/B branch/worktree census and recovery ledger; no second worktree inventory.

Rewriting history would risk frozen research tags, 73 deleted-ref recovery SHAs, unique/KNOWLEDGE branches, attached worktree owners, old production LKG and checkpoint provenance. That risk outweighs an unmeasured remote clone saving. Keep exact history and archive/foundation-pre-batch-b-20261003 recovery.

Decision A: NO ACTION, completed. No history rewrite, forced push, reflog expiry, Git cleanup, branch/worktree deletion or production/UserData change. Continue only Foundation final validation/uninstalled LKG and Epic closeout as authorized.
