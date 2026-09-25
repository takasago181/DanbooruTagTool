# Issue132 Current Automation Operation — runtime router

Status: ACTIVE
Branch: `research/taxonomy-usability-audit`

This file is intentionally short. Historical operating details remain in Git history and superseded cards; they are NOT normal-run inputs.

## Product goal

Primary criterion:

> 作りたい画像の見た目・行為・部位・体位・衣装・構図などから、Danbooruタグ名を知らなくても自然に目的タグへ辿り着けること。

Image-generation usability is the goal, not taxonomy completeness or prose volume.
Adult/sexual generation is a normal supported workflow and must not be suppressed or over-researched merely for being adult/sexual.
Accuracy still wins over guessing.

## Current five-task model

- Worker 1 — Lane 1 NEW forward work
- Worker 2 — Lane 2 NEW forward work
- Worker 3 — Lane 3 NEW forward work
- Repair — historical invalid staging + Lane3 historical route-family debt
- Coordinator — QA / CI interpretation / watchdog only

## Current operational authority

Forward workers:
`docs/issue132/parallel/RUNTIME_WORKER_CARD_V6.md`
blob SHA: `e03eb5defab4d4cd33dc4e04769035bc1a0a1e64`

Repair:
`docs/issue132/parallel/RUNTIME_REPAIR_CARD_V5.md`
blob SHA: `85cc699df5f1b671637f6c0aaa6c267c767982a3`

Coordinator:
`docs/issue132/parallel/RUNTIME_COORDINATOR_CARD_V2.md`
blob SHA: `db5eef18c542efc815b3531ea7bb4f32d6960005`

Frozen Pass-A semantic authority remains unchanged. These cards optimize execution only.

## Hot-path rule

Normal tasks read only their current runtime card plus the live files that card explicitly requires.
Do not reread superseded cards, old operation manuals, status caches, Issue history, or full frozen docs unless a real invariant/contract conflict requires fallback.

Worker semantic block = up to 100 identities.
Persistence slice = 25 identities.
Per-run ceiling = 300 identities.
A 25-row save is persistence only, never a stop signal.

Live checkpoint/staging/repair-overlay data is authority; mutable status JSON files are caches only.

## Safety / persistence

Never evade safeguards.
Explicit content/policy rejection is not retried through another transport with identical bytes.
Transport/concurrency failures may use the authorized non-force Git-object fallback.
Independent work continues when safe.

Historical staging is repaired only through append-only repair overlays; old evidence is not replaced.

## Boundaries

Research branch only.
No merge/production apply.
Do not mutate main, production, UserData, #64/#76/#118 authority, canonical/PromptToken, Japanese production overlay, Character/Copyright/Artist lanes, or search ranking.
