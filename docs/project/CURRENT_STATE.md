# CURRENT STATE

最終更新: 2026-10-03 — #245 production closeout complete; Foundation Gate 0 open

This file keeps only the current project state. Historical detail belongs in `CURRENT_STATE_HISTORY.md`.

## Current routing

### #248 — Foundation Audit

Status: **READY / ACTIVE NEXT**

Start gate is satisfied:
- #245 production promotion complete and Issue closed;
- new LKG recorded;
- production UserData/Library/LoRA/catalog/authority protection verified;
- real Forge -> Library round-trip verified;
- final Release 364 PASS / 4 SKIP / 0 FAIL.

#248 is audit/measurement only. It must determine what Foundation work is actually necessary and then stop for review.

Detailed scope: live Issue #248.

### #259 — Codex/autonomy + personal-workstation policy cleanup

Draft PR #259 contains global rule simplification. It is management/policy-only and does not change product source/runtime/UserData.

Core policy:
- WHAT / WHY / HARD BOUNDARIES / ACCEPTANCE are fixed by project intent;
- HOW is chosen by Codex;
- private single-user workstation, not public-distribution quality, is the default deployment assumption;
- adult/sexual/fetish/hard-niche 2D generation is a first-class product priority.

## Current production baseline

- runtime: `C:\Codex\DanbooruTagTool-App`
- source commit: `b3f48c359a8473c8bbf02347487cba5d8dacf96c`
- repository gate-open main: `c75a4795bd082987e8e8348f0432200b20094ff5`
- LKG: `docs/project/LAST_KNOWN_GOOD.json`
- EXE SHA256: `C69C83B365C24CBA8B870BA6A5778AC83CE28DEBED779D1D556C1A9B74768F7B`
- catalog SHA256: `D91A68186661127F16E2AE102B4DD9F3A96EAE578B3C989A8B4F17169639FC6F`
- Release: 364 PASS / 4 SKIP / 0 FAIL
- focused: 112 PASS / 1 SKIP / 0 FAIL
- primary Create -> Forge -> PNG -> Library metadata/hash: PASS

Known limitation:
- native pixel capture white client; final visual appearance NOT_VERIFIED.
- actual UI operations/status, WPF render/tree and generation workflow passed.

## Product goal

Canonical source:
`docs/PRODUCT_GOAL_LOCK.md`

Core flow:
`理解 -> 発見 -> 選択 -> 出力`

Priority use case:
**adult / sexual / fetish / hard-niche 2D generation**, especially terminology discovery and difficult structural concepts such as relation/body-site/actor-target/count/visibility/device/restraint/fluid/topology.

General-purpose use remains supported.

## Permanent protections

Keep:
- UserData/personal Library/LoRA protection;
- rollback/recovery for risky runtime changes;
- no destructive `git clean -fdx/-fdX`;
- canonical identity / stable Special-ID protection;
- explicit research/evidence -> production promotion decision;
- credentials/secrets out of Git;
- relevant regression tests.

Do not treat second-PC portability, single-file packaging, zero-PDB/DLL shape, machine-independent paths, universal offline operation, or PR ceremony for trivial edits as universal requirements.

## Completed / do not reopen by default

#132, #179 accepted projection, #180, #188, #199, #201, #204, #210/#211, #216, #223, #226, #228, #229, #232, #245.

Use live GitHub + immutable checkpoint/result rather than fixed historical SHAs when a completed area must be inspected.
