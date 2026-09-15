# CURRENT DEV TASK — ISSUE #80 FORGE BRIDGE V1 (COMPLETED / MERGED)

最終同期: 2026-09-15

## Routing status

- **Issue #80 — Forge bridge v1 is completed and integrated into `main` at `f5ced15e3a368cae29f869527a20bcb41c7237b4`.**
- Implementation branch: `codex/issue80-forge-bridge-v1`.
- Activation baseline: `a4eeadd9f018b659ddc59e08d4859cca09f32382`.
- Integration: fast-forward with `--ff-only`; no force push.
- No successor Active DEV is designated.
- #70 and #76 remain separate lanes; no taxonomy or translation data changes.

## Scope

Add a local companion bridge between the existing WPF app and Forge's txt2img fields. The bridge sends the visible/copy English Prompt as Positive, leaves Negative unchanged for common sends, and replaces Negative byte-for-byte for preset sends. It never starts generation.

## Safety boundaries

- Reuse the existing `UserData/user.db` payload/versioning boundary; do not create a second user-data store.
- Positive is always the visible/copy English Prompt from the current output profile; internal Prompt state is not changed.
- Preset Negative is opaque and is used byte-for-byte, including replace-empty.
- The versioned localhost-only FastAPI/JS bridge validates payloads, consumes pending requests once, and never triggers Generate or a generation API.
- Preserve #72/#73/#74/#75/#77/#79 behavior, including output-profile preview/copy equality.
- No new top-level folders, artifacts, WPF copy, #70/#76 data, taxonomy, canonical data, or protected data changes.

## Required validation

- Release build.
- All .NET tests.
- Focused #80 bridge/protocol/send/error-handling tests.
- #72/#73/#74/#75/#77/#79 regression tests.
- `git diff --check`.
- Practical Windows/WQHD launch and actual local Forge bridge check.

## Completion

- DEV acceptance: Issue #80 latest comment `5677859083`.
- Main integration: completed by fast-forward with `--ff-only`; implementation tip plus UI follow-up commit `f5ced15e3a368cae29f869527a20bcb41c7237b4` is included in `main`.
- Issue #80 is completed and closed after post-merge validation.
