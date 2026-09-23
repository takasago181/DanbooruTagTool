# CURRENT DEV TASK — LIVE ROUTING INDEX

最終更新: 2026-09-24

このファイルは「単一の実装task」を固定するものではなく、現在動いているlaneへのrouting indexである。
過去の Performance / Runtime Load Audit は完了済みであり、current taskとして再開しない。

## Current routing

### #180 — Character -> HOME Copyright rebuild

- State: ACTIVE RESEARCH / research-only
- Branch: `research/issue180-single-home-pilot`
- Verified HEAD at this routing sync: `837cd420894a80f12d9905475aa8a334907377ea` (actively advancing; always re-fetch live HEAD before work)
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

- State: **ACTIVE FULL PASS-A RESEARCH**
- Branch: `research/taxonomy-usability-audit`
- Goal: 全31,003 ordinary identitiesを独立にsemantic reviewし、画像生成でタグ名を知らなくても自然に辿れるdiscovery mapを作る。
- Current execution: 3 normal ChatGPT Automation workers + 1 coordinator/watchdog.
- Current live operation: **300 identities / worker run is a ceiling, not a quota**; normal preflight uses `docs/issue132/parallel/WORKER_EXECUTION_CARD_V1.md`; new immutable checkpoints are 25 rows; each identity is strictly finalized once before moving on; ambiguity/proper nouns/specialist or sexual-boundary concepts require `RESEARCHED`; unresolved meaning uses `SEMANTIC_UNRESOLVED`; every cumulative lane-local 100-row block gets high-risk re-review plus deterministic ordinary CHECKED spot-checks; redundant full-batch rereads/status/CI polling are intentionally removed.
- Operational authority: `docs/issue132/parallel/CURRENT_AUTOMATION_OPERATION.md`
- Frozen Pass-A semantic contract remains unchanged; old `READY FOR CODEX LUNA PASS A` / 100-row / 200-row wording is not current execution routing.
- Progress snapshot at this sync: valid persisted checkpoint union 500 / 31,003 (Lane 1: 225, Lane 2: 175, Lane 3: 100). Re-fetch live checkpoint union before continuing.
- No production mutation, main merge, #64/#76/#118 rewrite, or Character/Copyright/Artist lane mutation is authorized by #132 Pass A.

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
