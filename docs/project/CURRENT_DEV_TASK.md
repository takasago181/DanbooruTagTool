# CURRENT DEV TASK — LIVE ROUTING INDEX

最終更新: 2026-09-22

このファイルは「単一の実装task」を固定するものではなく、現在動いているlaneへのrouting indexである。
過去の Performance / Runtime Load Audit は完了済みであり、current taskとして再開しない。

## Current routing

### #180 — Character -> HOME Copyright rebuild

- State: ACTIVE RESEARCH / research-only
- Branch: `research/issue180-single-home-pilot`
- Verified HEAD at this routing sync: `494a61ddb76d01f7f07a76b9d42ca1294690c4f8`
- Draft PR: #182
- Goal: high-precision authorityから各Characterのcanonical HOME Copyrightを0..1件で確定する。
- Safety: missing relation > wrong relation。
- Do not merge to main or apply to production until the Issue #180 completion/review gates are satisfied.
- Issue本文・latest checkpoint・issue-specific docsを必ずlive取得してから再開する。

### #179 — Character/Copyright quality audit

- State: ACTIVE RESEARCH
- Branch: `research/issue179-character-quality-audit`
- Verified HEAD at this routing sync: `78cd14693d066e8f150a140628eef6c5d343b2c5`
- Draft PR: #181
- Goal: Character/Copyright identity, Japanese display/search, ranking, 2D scope quality.
- Artist is out of audit scope.
- #180のHOME relation authorityと混同しない。

### #132 — taxonomy / discoverability research

- State: ACTIVE RESEARCH
- Goal: 実際の画像生成で使いやすいtag discovery / classification UXを検証する。
- Current direction is research/prototype comparison; production mutation is not authorized merely by this routing file.
- live Issueのcurrent checkpointを取得してから続行する。

## Parallel / maintenance routes

- #65: Stage10 hands-on image-generation learning. Parallel learning; not a v1 product completion gate.
- #44: persistent KNOWLEDGE owner. Prompt / generation-effectiveness responsibility is included here; there is no separate PROMPT team.
- #52: repository cleanup tracker / maintenance.
- #138: production runtime cleanliness maintenance contract.
- #71: post-v1 roadmap; activate only when the user explicitly selects an item.

## Completed / do not route as unfinished

- Performance / Runtime Load Audit: complete.
- Portable/runtime hardening: complete.
- #177 mitigation: current UI hides Artist and disables unreliable old Character-Copyright relation surfaces.
- Forge Generation Recipe automatic apply/generate flow: not a remaining task; #175/#176 established the reference/persistence-only recipe direction.

## Preflight

Before any implementation/research continuation:

1. Fetch live `main` and `docs/project/CURRENT_STATE.md`.
2. Fetch the target live Issue body and latest checkpoint/comments.
3. Read `docs/project/PERMANENT_RULES.md`.
4. Read target issue-specific specs/checkpoints.
5. Verify branch and HEAD live; do not trust the SHA in this snapshot if the branch has advanced.
6. Fail closed on scope/routing contradictions.

## Isolation rule

Do not mutate #179 or #180 research branches as part of management/routing cleanup.
Do not mix #179/#180/#132 data, commits, or authority without an explicit handoff recorded in GitHub.

Historical completed-task details belong in Git history/issues/CURRENT_STATE historical sections, not as the current task represented by this file.
