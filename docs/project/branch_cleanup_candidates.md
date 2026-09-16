# Remote branch cleanup candidates

Audit date: 2026-09-16. This is a review list, not an authorization to delete.

Each branch below has zero branch-side commits by the mechanical check:

```text
git rev-list --count origin/main..origin/<branch> == 0
```

They remain KEEP because this audit did not prove all non-commit conditions
(active Issue references, open PR usage, restore anchors, persistent knowledge,
current Issue #70 operation, or protected historical evidence) are absent.

| Remote branch | Unique commits vs origin/main | Decision |
| --- | ---: | --- |
| `origin/codex/issue28-e2e-verdict` | 0 | KEEP / candidate |
| `origin/codex/issue43-special-core-dictionary` | 0 | KEEP / candidate |
| `origin/codex/issue49-dict-promotion-latest-main` | 0 | KEEP / candidate |
| `origin/codex/stage9c9d-completion` | 0 | KEEP / candidate |
| `origin/docs/organize-agent-rules-no-semantic-change` | 0 | KEEP / candidate |
| `origin/docs/stage10-ab-automation-temp` | 0 | KEEP / candidate |
| `origin/codex/issue44-hf-token-gated-dispatch` | 0 | KEEP / candidate |

No remote branch was deleted. Re-run the reference checks against live GitHub
Issue/PR state before any future deletion, and never force-push.
