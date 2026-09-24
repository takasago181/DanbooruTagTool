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

New-row quality watchdog is event-driven, not hourly repetition:
- keep last_sampled_100_boundary per lane in coordinator_status;
- only when a lane completes a NEW 100-row boundary not yet sampled, perform the independent second-line sample for repeated color->COLOR, placement->POSE, motif->LIVING, weak SCENE/TOOL secondaries;
- if the sample is clean, mark that 100-block sampled and do not reread it next cycle;
- if a systematic family issue appears, flag only the affected family/range for Repair; do not make the forward worker reread unrelated rows.
Historical Lane3 751-1050 debt belongs to Unified Repair.

Read unified repair state from repair_status.json. Do not expect per-lane repair-status files.

Keep coordinator_status concise; no repeated narrative history.

## Primary write transport — Git object protocol

All Issue132 writes use `docs/issue132/parallel/GIT_OBJECT_WRITE_PROTOCOL_V1.md` as the PRIMARY transport. Do not use contents `create_file/update_file` for normal Issue132 persistence. Use branch-head/tree -> create_blob -> create_tree -> create_commit -> re-fetch head -> update_ref(force=false), with retry on concurrent branch advance exactly as defined there. Contents API is fallback only when the Git-object path is unavailable.

A pre-write runtime safety refusal on contents API is not a blocker and must not stop/disable the task. Only an actually attempted Git-object path failure after the protocol's retries may become a write blocker.
