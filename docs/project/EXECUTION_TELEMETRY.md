# Execution Telemetry Schema

Status: **Issue #188 operational guidance**

Purpose: distinguish real semantic/tool limits from workflow overhead without creating a second evidence system.

Telemetry is **derived operational cache**, never semantic authority.

## 1. Storage rule

Prefer embedding telemetry in an already-required run-end status/cache update.

Do **not** create one extra commit/file merely to record telemetry.

If a task has no existing status/cache write, telemetry is optional unless the Issue explicitly requires it.

## 2. Minimal fields

Recommended run-end object:

```json
{
  "schema_version": "execution-telemetry-v1",
  "rows_completed": 0,
  "checkpoints_created": 0,
  "researched_rows": 0,
  "unresolved_rows": 0,
  "research_batches": 0,
  "preflight_mode": "FAST",
  "full_authority_fallback": false,
  "semantic_input_rows": 0,
  "structural_validation_failures": 0,
  "stop_reason": "TARGET_REACHED",
  "duration_seconds_observed": null
}
```

## 3. Semantics

- `rows_completed`: accepted immutable rows written this run.
- `checkpoints_created`: immutable checkpoint/result files created this run.
- `researched_rows`: rows finalized as RESEARCHED or equivalent.
- `unresolved_rows`: explicit unresolved outcomes.
- `research_batches`: external research/search batches actually executed; count grouped calls, not per-row guesses.
- `preflight_mode`: `FAST` or `FULL`.
- `full_authority_fallback`: true only when compact fingerprints failed or an actual contradiction/drift required full authority recovery.
- `semantic_input_rows`: rows actually exposed to semantic reasoning, not total source population.
- `structural_validation_failures`: machine-serialization/schema assertions that failed before or after write.
- `stop_reason`: existing task-defined stop reason.
- `duration_seconds_observed`: nullable; only populate when a reliable external timestamp is available. Do not invent timing.

## 4. Interpretation

Examples:

### Low rows + high researched_rows / research_batches

Likely genuine semantic difficulty.

### Low rows + FULL preflight + full_authority_fallback=true

Likely contract/routing recovery cost. Investigate why warm-resume fingerprint failed.

### Low rows + low researched_rows + FAST preflight

Likely workflow/tool overhead or overly conservative stop logic.

### semantic_input_rows far above run ceiling

Likely large-source transport regression.

### structural_validation_failures > 0

Serializer/tool boundary problem. Fix deterministic serialization; do not compensate with more semantic rereading.

## 5. Do not collect

Do not add:
- chain-of-thought;
- semantic reasoning transcripts;
- per-row hidden confidence scores;
- repeated source copies;
- full request/response logs;
- user/private runtime data.

Telemetry should answer "where did execution capacity go?" and nothing more.

## 6. #132 mapping

For Issue #132, add this object to lane `status.json` only when that status is already being written at run end / lane completion / 100-boundary.

No extra status update is authorized solely for telemetry.

Coordinator may compare:
- checkpoint-derived actual delta;
- status `last_run_metrics`;
- latest CI result.

Checkpoint union remains progress authority.
