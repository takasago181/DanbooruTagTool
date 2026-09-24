# Issue132 Runtime Coordinator Card V4

Read only this card, coordinator_status.json, three lane status files, repair_status_lane12.json and repair_status_lane3.json when present, plus latest Issue132 CI conclusion. Fetch CI job logs only when run_id/head_sha changed or the failure class changed.

Responsibilities:
- monitor 3 forward workers; never load their semantic shards;
- verify post-V4 new windows use exact tuple binding;
- classify stop: 300/lane-complete/hard-block/actual-forced = acceptable; voluntary 25/50/etc with safe continuation = INVALID_STOP;
- Lane 2: specifically detect return of 25/50 wrap-up;
- staging-only CI failure = repair debt, not reason to stall clean forward workers;
- frozen/immutable failure = high-priority reconciliation;
- official reviewed = immutable checkpoint union only;
- summarize repair debt trend from the two repair status files;
- do not perform historical repair unless a Repair task is blocked and one tiny urgent same-lane intervention is necessary.

New-row quality watchdog: sample for repeated color->COLOR, placement->POSE, motif->LIVING, weak SCENE/TOOL secondaries. Historical Lane3 751-1050 debt belongs to Repair3.

Keep coordinator_status concise; no repeated narrative history.
