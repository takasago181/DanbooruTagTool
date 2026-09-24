# Issue132 Repair Lane 3 V2

Own only Lane 3 historical non-authoritative staging debt and historical 751-1050 route-family remediation. Never edit immutable checkpoints, Lanes 1-2, main, production, UserData, #64/#76/#118.

Read RUNTIME_WORKER_CARD_V4.md for semantic/exact rules, coordinator_status.json for latest CI run id, and repair_status_lane3.json if present.
Fetch latest staging-validator logs only when the CI run id/head changed from the status already examined; otherwise continue the stored queue.

First repair up to 3 oldest validator-named structurally invalid Lane3 windows per run. Identity shift/gap/duplicate/wrong tuple => full authoritative 25-window rebuild; never renumber/slide. Exact-tuple semantic lint => targeted correction with research only if uncertain. Pre/post exact gate mandatory.

When no structural Lane3 window remains, continue focused 751-1050 family audit without rereading all 300:
- simple color/pattern adjective alone -> remove COLOR secondary;
- object/clothing placement alone -> remove POSE secondary;
- animal/plant motif/print/ornament -> remove LIVING secondary;
- weak SCENE/TOOL secondary -> independent-browse challenge.
Seeds are not automatic rewrites; keep valid independent routes.

Maintain docs/issue132/parallel/repair_status_lane3.json: CI examined, repaired windows, remaining structural queue, route-family progress, blockers.
