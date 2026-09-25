# Issue132 Current Automation Operation — canonical runtime router

Status: ACTIVE
Branch: `research/taxonomy-usability-audit`

This file is routing only. Historical operating details and superseded cards are not normal-run inputs.

## Product goal

> 作りたい画像の見た目・行為・部位・体位・衣装・構図などから、Danbooruタグ名を知らなくても自然に目的タグへ辿り着けること。

Image-generation usability is the goal, not taxonomy completeness or prose volume.
Adult/sexual generation is a normal supported workflow. Adult/sexual content alone must not trigger suppression, extra research, or special risk treatment.
Accuracy still wins over guessing.

## Five-task model

- Worker 1 — Lane 1 NEW forward work
- Worker 2 — Lane 2 NEW forward work
- Worker 3 — Lane 3 NEW forward work
- Repair — historical invalid staging + promotion-blocking historical holds + Lane3 route-family debt
- Coordinator — QA / CI interpretation / watchdog only

## Only current operational authorities

Forward workers:
`docs/issue132/parallel/RUNTIME_WORKER_CARD_V7.md`
blob SHA: `c92903f23c7c084c88e1853948aaceff75ec7263`

Repair:
`docs/issue132/parallel/RUNTIME_REPAIR_CARD_V6.md`
blob SHA: `6628d42ccd8b7f45dad155ea51b04c51c800a8c2`

Coordinator:
`docs/issue132/parallel/RUNTIME_COORDINATOR_CARD_V5.md`
blob SHA: `592dca5f81888efc81ebba28a1a28d579ecafa74`

All earlier Runtime Worker/Repair/Coordinator cards are SUPERSEDED even if their numeric names are encountered during repository browsing.

Frozen Pass-A semantic authority remains unchanged. These cards optimize execution only.

## Hot path

Normal tasks read only their exact current card plus live files that card explicitly requires.
Do not choose a card by "highest file found" or by repository search.
Do not reread old operation manuals, status caches, Issue history, or full frozen docs unless a real invariant/contract conflict requires fallback.

Worker semantic block: up to 100 identities.
Persistence slice: 25 identities.
Per-run ceiling: 300 identities.
A 25-row save is persistence only, never a stop signal.

Report checkpoint prefix and staging high-watermark separately.
Live checkpoint/staging/repair-overlay data outranks mutable status JSON.

## Hash naming

Global parent:
- parent_neutral_sha256 = ac0f888d02f19a440c63b3b9f695c58f9ba53b98ebe9756edec51db1c5ff8f7d
- parent_identity_order_sha256 = f80c63018ce19a8c7c5d8d6fd83d03cf760c510d8f6cfa455d1ab356fb31361b

Shard manifests also contain shard-local `identity_order_sha256` and `csv_sha256`. These are NOT global parent hashes and must never be compared to the global parent values.

## Safety / persistence

Never evade safeguards.
Explicit content/policy rejection is not retried through another transport with identical bytes.
Transport/concurrency failures may use the authorized non-force Git-object fallback.
Independent work continues when safe.

Historical staging is repaired through append-only repair overlays. Existing historical staging remains immutable evidence.
A valid active overlay becomes the effective historical window.
Promotion logic must resolve the effective overlay before creating a checkpoint.

## Boundaries

Research branch only.
No merge/production apply.
Do not mutate main, production, UserData, #64/#76/#118 authority, canonical/PromptToken, Japanese production overlay, Character/Copyright/Artist lanes, or search ranking.
