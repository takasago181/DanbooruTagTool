# Project Execution Architecture

Status: **Issue #188 foundation / project-wide guidance**

Purpose: keep recurring research, translation, audit, and automation work fast **without weakening semantic accuracy, provenance, protected-data safety, or final acceptance gates**.

## 1. Core architecture

Use this default shape for large recurring work:

```
heavy authority/source
  -> immutable hash/manifest
  -> compact execution capsule
  -> deterministic bounded input extraction
  -> semantic/translation work
  -> immutable append-only result/checkpoint
  -> cheap incremental validation
  -> periodic risk-based QA
  -> final full audit / acceptance
```

The model should spend time on judgment, not repeatedly reconstructing unchanged state.

## 2. Execution tiers

Classify the task before selecting preflight strength.

### READ_ONLY

Examples:
- inspect state;
- compare artifacts;
- review a report.

Normal gate:
- verify live target;
- read only evidence needed for the question.

### APPEND_ONLY

Examples:
- semantic review ledger;
- translation queue result;
- immutable audit checkpoint.

Normal gate:
- verify compact routing/contract fingerprints;
- derive exact next prefix from immutable evidence;
- read only the bounded next input;
- validate the new append;
- avoid destructive/protected-data preflight that cannot be exercised by the task.

### MUTATING

Examples:
- implementation changes;
- generated sidecar replacement;
- queue reconciliation.

Normal gate:
- current routing + live Issue;
- affected contract/spec;
- focused regression;
- dependency/impact checks.

### DESTRUCTIVE / PRODUCTION

Examples:
- runtime promotion;
- UserData migration;
- cleanup/delete;
- production taxonomy apply.

Normal gate:
- full fail-closed authority recovery;
- protected-data evidence;
- exact before/after provenance;
- complete acceptance criteria.

**Efficiency rules may never weaken DESTRUCTIVE / PRODUCTION safeguards.**

## 3. Cold start vs warm resume

### Cold start

Use when:
- new chat/session;
- lane selection changed;
- contract changed;
- branch/Issue authority is uncertain;
- previous state cannot be trusted.

Read the full authority chain required by the project.

### Warm resume

Use when:
- same lane;
- same frozen contract;
- recurring scheduled worker;
- immutable progress exists;
- compact routing and contract fingerprints match.

Warm resume should normally read:
1. compact routing/contract fingerprints;
2. task-local immutable progress listing;
3. next bounded input;
4. any changed/required evidence.

Do **not** reread large unchanged authority documents merely because they exist.

If a fingerprint differs, fall back to cold-start/full-authority behavior.

## 4. Authority vs cache

Project-wide default:

> immutable evidence is authority; status/progress summary is derived cache.

Examples of immutable evidence:
- checkpoint CSV;
- result CSV;
- accepted manifest;
- committed decision record.

Examples of cache:
- status.json;
- progress counters;
- coordinator summary.

A stale cache must be reconstructable from immutable evidence and must never invalidate already-valid immutable progress.

Operational rules:
- workers should not rewrite a status cache after every small append unless a consumer actually requires it;
- prefer cache refresh at run end / meaningful boundary / coordinator cycle;
- a cache count lower than the checkpoint union means **cache stale**, not progress rollback;
- cache reconstruction must be deterministic where possible;
- if both cache and immutable evidence are read, reconcile in favor of validated immutable evidence.

## 5. Large-source transport

Authoritative large files are not automatically good worker inputs.

For large recurring work:
- preserve original authority unchanged;
- create deterministic compact shards/ranges;
- pin source hash/order/population;
- include only fields needed for the task;
- let workers reason over only the next bounded slice;
- run final audit against original authority.

Issue #70 compact shards are the current reference pattern.

Generic deterministic extractor:
- `scripts/maintenance/extract_compact_csv_slice.py`

Use it when a large CSV can be narrowed by stable order/lane/range/field projection before semantic reasoning. The generated slice manifest pins the source SHA, source/filtered counts, selected range, output fields, and output SHA.

The compact output remains transport/cache only and must never silently replace the source authority.

## 6. Quality model

Do not equate quality with repeated full rereads.

Prefer:
- strong per-item certainty gate;
- mandatory research when material uncertainty remains;
- explicit unresolved state when research cannot resolve meaning;
- risk-based periodic QA;
- deterministic ordinary-case sampling;
- machine structural validation.

Remove:
- duplicate rereads of obviously clear items;
- repeated verification of unchanged hashes;
- full-population ingestion where deterministic filtering can happen first.

## 6.5. Machine serialization boundary

Structured output must not rely on the model visually counting delimiters.

For CSV / JSON / manifests / ledgers:
1. build a structured row/object first;
2. serialize with a real CSV/JSON writer;
3. parse the produced bytes/text back;
4. assert exact schema/field count/types/enums/order;
5. only then persist or push.

This is especially important for append-only Automation work. Semantic review belongs to the model; quoting, column alignment, JSON escaping, sorting, duplicate/gap detection, and schema conformance belong to deterministic code.

Do not add a second semantic reread merely to compensate for weak serialization. Fix the serialization boundary instead.

## 7. CI tiers

### Incremental

For append-only progress:
- changed checkpoint/result schema;
- enum/ID validity;
- exact prefix/assignment;
- duplicate/gap checks;
- JSON/CSV parse;
- lightweight union consistency.

### Boundary

At meaningful milestones:
- accumulated block consistency;
- risk QA;
- broader union validation.

### Full

Only for:
- source/contract changes;
- explicit manual dispatch;
- finalization;
- merge/acceptance gate.

Full CI may rebuild large source products, rerun all smoke tests, and upload artifacts.

## 8. Telemetry

Recurring workers should expose enough operational metrics to distinguish semantic difficulty from workflow overhead:
- rows completed;
- researched/unresolved count;
- checkpoint count;
- tool/read/write counts when available;
- validator failures;
- actual stop reason;
- approximate run duration when observable.

Telemetry is operational evidence only, not semantic authority.

Common schema:
- `docs/project/EXECUTION_TELEMETRY.md`

Prefer embedding `last_run_metrics` into an already-required run-end status/cache write. Do not create a separate commit just for telemetry.

## 9. Anti-regression rule

Before adding a new safety step to a recurring worker, ask:
1. What failure does it prevent?
2. Is that failure already covered elsewhere?
3. Can the check be deterministic instead of model-based?
4. Must it run every item/run, or only on change/boundary/finalization?
5. Does it preserve ambiguity detection and final evidence?

If the new step duplicates an existing gate, prefer consolidation rather than accumulation.
