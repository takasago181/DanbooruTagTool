# Issue132 Current Automation Operation

Status: **HISTORICAL AUTOMATION OPERATION / CURRENTLY PAUSED**

The five normal ChatGPT Automation tasks described below are no longer the live execution driver. The current live execution authority is `docs/issue132/parallel/RUNTIME_AUTHORITY.json`, which selects guarded Codex execution and keeps those automations paused.

Current machine-readable authority:

`docs/issue132/parallel/RUNTIME_AUTHORITY.json`

Execution generation: **flat Pass-A V1**.

Exactly five active Issue132 tasks:
- Worker 1 — lane 1 forward review
- Worker 2 — lane 2 forward review
- Worker 3 — lane 3 forward review
- Repair — invalid/hold windows only
- QA-Coordinator — accepted-set validation, selective semantic QA, completion

Product goal:

> 作りたい画像の見た目・行為・部位・体位・衣装・構図などから、Danbooruタグ名を知らなくても自然に目的タグへ辿り着けること。

Adult/sexual generation is a normal supported workflow. Accuracy wins over guessing.

The old staging -> checkpoint -> promotion prefix pipeline is no longer the active progress model.

Progress is the union of all independently valid identities. An early invalid range does not erase or block later valid ranges.

Historical checkpoint files are accepted seed data. Historical staging files remain immutable evidence. Repair is append-only and touches only invalid/hold windows. No checkpoint promotion is performed.

New Worker persistence target is up to 100 consecutive lane-local identities per file, with up to 300 identities per run.

Mechanical validation covers 100% of accepted output. Semantic QA is risk-based rather than a complete duplicate review.

No merge or production apply is authorized.
