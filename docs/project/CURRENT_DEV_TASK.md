# CURRENT DEV TASK — COMPATIBILITY ROUTING POINTER

最終更新: 2026-09-24

このファイルは旧workflowとの互換用ポインタです。
**current routingの内容をここへ複製しない。**

## Current authority

1. live GitHub `main`
2. `docs/project/CURRENT_ROUTING.json`
3. `docs/project/CURRENT_STATE.md`
4. selected live Issue + latest checkpoint
5. `docs/project/PERMANENT_RULES.md`
6. task-specific contract/spec

## Active lanes

- #132: `research/taxonomy-usability-audit`
- #179: `research/issue179-character-quality-audit`
- #180: `research/issue180-single-home-pilot`
- #188: project-wide execution-efficiency infrastructure

Issue/branch HEAD/progressはこのファイルの固定値ではなく、live GitHubから取得する。

## Resume rule

- cold start: `CHAT_START_PROTOCOL.md` のfull authority recovery
- warm resume: `EXECUTION_ARCHITECTURE.md` のcompact fingerprint + task-local immutable progress
- production / protected-data / delete: warm-resume shortcutを一般化しない

## Historical task details

旧Performance/runtime/#117等の詳細をcurrent taskとしてここへ再掲載しない。
必要なら:
- `docs/project/CURRENT_STATE_HISTORY.md`
- live Issue / PR / Git history

を参照する。
