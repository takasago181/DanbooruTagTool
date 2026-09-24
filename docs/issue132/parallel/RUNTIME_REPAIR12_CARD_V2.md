# Issue132 Repair Lanes 1-2 V2

Own only historical non-authoritative staging debt in Lane 1 and Lane 2. Never edit immutable checkpoints, Lane 3, main, production, UserData, #64/#76/#118.

Read RUNTIME_WORKER_CARD_V4.md for semantic/exact rules, coordinator_status.json for latest CI run id, and repair_status_lane12.json if present.
Fetch latest staging-validator logs only when the CI run id/head changed from the status already examined; otherwise continue the stored repair queue.

Queue only validator-named invalid Lane1/2 windows. Process up to 3 oldest promotion-blocking windows per run per lane, maximum 6 total, but never sacrifice semantic review quality.

For identity shift/gap/duplicate/wrong tuple: full 25-window rebuild from authoritative shard tuples; old staging is hints only; never renumber or slide rows.
For exact-tuple windows with only definite structural/semantic lint: repair only the defective fields if the correct value is certain; research if materially uncertain.
Every write requires pre-write and re-fetch post-write exact tuple + 22-field gate.
If a rebuilt window cannot pass, repair/delete it before moving on.

Maintain docs/issue132/parallel/repair_status_lane12.json: CI examined, repaired windows, remaining queue by lane, structural debt trend, blockers.
