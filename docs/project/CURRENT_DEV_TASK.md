# CURRENT DEV TASK — ISSUE #83 AGGRESSIVE LOCAL CLEANUP (ACTIVE)

最終同期: 2026-09-15

## Routing status

- **Issue #83 is the active maintenance task for this workspace.** It runs from latest live `main`, requires inventory and current-dependency proof, and permits targeted deletion of obsolete/reproducible local assets in the same task.
- Preserve the current WPF runtime/catalog, accepted catalog build inputs, Issue #70 queue/source/results, current #44/#65 data, and any unproven/active worktree state.
- Do not use `git clean -fdx` or `git clean -fdX`; do not delete active #70 queue state or accepted rows.
- **Issue #76 — Special browse taxonomy v2 is completed and integrated into `main`.**
- Implementation branch: `codex/issue76-special-v2-production`.
- Final branch tip: `cf6f34919d163d346411d562e9075b3843f4b170`.
- Merged PR: `#81`.
- Main merge commit: `0a1e94c8268cde97cfbc2305b3f2869d6919b5d6`.
- Issue #76 is closed as completed.
- Issue #83 is the current maintenance successor for this task only; #76 remains completed and must not be reopened.
- #70 translation/data, #65 Stage10 learning, #44 KNOWLEDGE, and #24 safety debt remain separate lanes.

## Accepted scope

The production WPF MainWindow keeps the existing overall UI while Special browse now uses the accepted shallow v2 facets:

- `種類から探す`
- `部位から探す`
- `テーマから探す`

Facet conditions intersect with AND semantics. Existing search ranking/order, Prompt editing/output, presets, Forge bridge, General browse, and canonical identity are preserved.

The user-accepted interaction is also integrated:

- the three Special axis groups stay expanded while the Special root is open;
- `1つ戻す` removes only the latest facet condition;
- `全解除` clears Special facet/history state without clearing ordinary search text;
- canonical duplicate rows are deduplicated in the result surface.

## Runtime / data boundary

- Existing Issue #56 v1 sidecar/evidence remains preserved as provenance.
- Accepted Issue #76 audit evidence is parsed only during explicit `--build-catalog`.
- The accepted v2 classification is persisted into each Special catalog row as `CatalogEntry.SpecialBrowseV2` in `catalog.db`.
- Normal startup reads the precomputed classification and does not reconstruct the 2,788-row mapping from audit CSVs.
- Existing pre-#76 `catalog.db` files are not overwritten automatically and require one explicit rebuild to contain v2 browse data.

## Validation

Final implementation evidence:

- Release build: PASS, 0 warnings / 0 errors
- full .NET tests: `126 passed / 6 skipped / 132 total`
- Issue #76 focused: `13 passed`
- production bake/persistence: `1 passed`
- regression: `63 passed / 2 skipped / 65 total`
- `git diff --check`: PASS
- Special identities: 2,788 preserved
- accepted status distribution: `2745 / 15 / 6 / 1 / 21`
- #70/#64/#63, canonical/protected data: unchanged

## Completion

- Final implementation return: Issue #76 comment `5679455508`.
- Final merge/close checkpoint: Issue #76 comment `5679492819`.
- Main integration: PR #81 -> `0a1e94c8268cde97cfbc2305b3f2869d6919b5d6`.
- Issue #76: **COMPLETED / CLOSED**.
- Issue #83 cleanup execution is active; no separate AUDIT lane is active.
