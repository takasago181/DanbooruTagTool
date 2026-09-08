# R3 Translation Automation — Test Implementation Specification

Status: TEST / QUARANTINE ONLY
Owner: UI-JA translation automation
Parent issues: #34 -> #36 -> #38
Baseline commit: `a787ce39aa50f938f95612801e79f30bcdb63427`

## 0. Hard boundary

This specification does **not** authorize production promotion.

Forbidden during this task:
- any production `data/**` edit;
- any #32 generation/support verdict edit;
- any #35 UI code/test edit;
- search-ranking logic changes;
- main merge;
- processing the remaining P0 925 as a bulk run;
- Stage10 production A/B.

All generated artifacts must remain under `translation_quarantine/r3/**`.

## 1. R3 authority model

Processing order is fixed:

`canonical identity -> authoritative semantic scope -> risk class -> display lane -> search lane -> #32 meaning bridge -> artifact states -> deterministic ledger`

Japanese text is a projection of established canonical meaning and must never become semantic authority.

Do not infer canonical meaning from existing `search_by_canonical` terms.

### Evidence roles

1. Exact-canonical authoritative definition/wiki evidence: may establish semantic scope.
2. Canonical/alias identity data: identity evidence only; alias is not automatically a Japanese synonym.
3. #32 meaning snapshot/fingerprint: consistency bridge only; it does not authorize wording by itself.
4. Existing local Japanese assets / current overlay: candidate wording evidence only.
5. Implication / related-tag / co-occurrence data: context evidence only; never synonym evidence by itself.
6. Canonical token composition: approval-capable only for LOW/MEDIUM transparent compositions under the rules below.

For HIGH/CRITICAL rows, absence of concrete exact-canonical scope evidence forces `REVIEW`.

## 2. Risk model

Highest applicable risk wins.

- `LOW`: simple concrete noun/object with one transparent entity meaning.
- `MEDIUM`: transparent color/simple attribute/count composition.
- `HIGH_POSE_ACTION`: pose/composition/state/action.
- `HIGH_ANATOMY_ADULT`: anatomy/adult/body-state/body-action.
- `CRITICAL`: relation, actor-target/body-site binding, rare/composite/idiomatic/ambiguous canonical, or meaning-relevant #32 disagreement/uncertainty.

If deterministic classification cannot establish a lower class safely, use `CRITICAL`.

## 3. Required implementation layout

Codex test-version implementation should create, at minimum:

- `translation_quarantine/r3/r3_common.py`
- `translation_quarantine/r3/r3_select_pilot.py`
- `translation_quarantine/r3/r3_run.py`
- `translation_quarantine/r3/r3_build_blind_audit.py`
- `translation_quarantine/r3/r3_verify.py`
- `translation_quarantine/r3/README.md`
- focused pytest coverage for deterministic selection, state derivation, search-term typing, bridge staleness/contradiction, blind masking, and rerun hashes.

The engine must not write outside `translation_quarantine/r3/**`.

The test suite must explicitly assert that production `data/**`, #32-owned files, and #35-owned files are unchanged relative to the pinned baseline used for the run.

## 4. Normalized output files

Do not extend the Phase1A CSV with another large horizontal block of audit columns. R3 uses normalized artifacts.

### `run_manifest.json`
One object containing:
- `schema_version`
- `engine_version`
- `baseline_commit`
- input file paths + blob/content hashes
- selection seed string
- pilot algorithm version
- blind algorithm version
- evidence manifest hash
- generated file hashes
- run timestamp as metadata only (must not affect deterministic content hashes)
- `production_modified: false`

### `pilot_selection.json`
Contains:
- exact eligible-pool definition
- excluded Phase1A canonicals hash
- selected 100 canonicals in stable order
- requested and achieved stratum counts
- #32-overlap counts selected/omitted
- deterministic selection key/hash per selected canonical

### `evidence_manifest.jsonl`
One evidence item per line. Required fields:
- `evidence_id`
- `canonical`
- `source_type`
- `source_ref`
- `source_url` when applicable
- `retrieved_or_revision_at` when available
- `scope_note`
- `content_identity` (hash/revision/blob identity when practical)
- `evidence_role` (`SEMANTIC_SCOPE`, `IDENTITY_ONLY`, `WORDING_CANDIDATE`, `CONTEXT_ONLY`, `BRIDGE32`)
- `frozen: true`

Deterministic reruns consume this frozen file and do not re-fetch live pages.

### `pilot_rows.jsonl`
Exactly one current R3 decision record per fresh pilot canonical. Required fields:
- `pilot_ordinal`
- `canonical`
- `lanes`
- `priority`
- `post_count_or_reference`
- `semantic_class`
- `risk_class`
- `semantic_scope_summary`
- `semantic_evidence_ids`
- `display_candidate`
- `display_state`
- `display_evidence_ids`
- `search_state`
- `bridge32_state`
- `row_state`
- `issue32_overlap`
- `issue32_snapshot_ref`
- `issue32_content_identity`
- `issue32_meaning_fingerprint`
- `evaluated_issue32_meaning_fingerprint`
- `bridge32_availability` (`AVAILABLE`, `NOT_REQUIRED`, `BRIDGE_MISSING`, `BLOCKED_BRIDGE`)
- `reason_codes`

Allowed state vocabulary: `READY`, `REVIEW`, `STALE_REVIEW`, `CONTRADICTION`.

### `search_terms.jsonl`
One search candidate per line. Required fields:
- `canonical`
- `term`
- `term_class`
- `term_state`
- `evidence_ids`
- `justification`
- `rejection_reason`

Allowed `term_class`:
- `EXACT_SYNONYM`
- `ORTHOGRAPHIC_VARIANT`
- `READING_VARIANT`
- `COMMON_EXACT_PARAPHRASE`
- `BROAD_SEARCH_ALIAS`

Existing `search_by_canonical` terms enter as candidates only.

`BROAD_SEARCH_ALIAS` requires explicit justification and can never count as semantic approval evidence.

### `bridge32.jsonl`
One audit record for every fresh-pilot canonical. Rows outside the #32
overlap are explicit `NOT_REQUIRED` records, not missing evidence:
- `canonical`
- `snapshot_ref`
- `content_identity`
- `frozen`, `pinned`, `immutable`
- `meaning_fingerprint`
- `evaluated_issue32_meaning_fingerprint`
- meaning-relevant propositions used
- `bridge32_state`
- `bridge32_availability`
- `reason_codes`

Meaning fingerprint includes only the normalized translation-visible proposition
allowlist: identity/entity scope, count/cardinality, actor/ownership,
target/body-site, action/state, intrinsic relation, pose, spatial requirement,
required modifier/qualifier, canonical meaning width, and semantic-support
relation only when UI-JA explicitly used it as semantic context. Generation-only
metadata must not stale translation. A required overlap without a valid pinned
snapshot is `BRIDGE_MISSING` or `BLOCKED_BRIDGE` and cannot become READY.

### `blind30_input.jsonl`
Reviewer-visible input only:
- canonical
- candidate display
- candidate accepted/review search terms with term classes
- frozen semantic evidence/scope notes
- #32 snapshot evidence where applicable

It must exclude automation states, reason codes, prior Phase1A verdicts, and any field that reveals READY/REVIEW decisions.

### `blind30_key.json`
Deterministic selection key, kept separate from reviewer-facing input.

### `blind30_review.jsonl`
Reviewer output schema:
- `canonical`
- `display_judgement` (`PASS`, `FALSE_APPROVAL`, `INSUFFICIENT_EVIDENCE`)
- `search_judgement` (`PASS`, `FALSE_APPROVAL`, `INSUFFICIENT_EVIDENCE`)
- `bridge32_judgement` (`PASS`, `SILENT_CONTRADICTION`, `NOT_APPLICABLE`)
- `review_note`

### `run_summary.json`
Must report:
- selected stratum counts
- artifact-state counts
- READY/REVIEW/STALE_REVIEW/CONTRADICTION row counts
- accepted/rejected/review search-term counts by term class
- #32 overlap/bridge-state counts
- bridge availability counts (`AVAILABLE`, `NOT_REQUIRED`, `BRIDGE_MISSING`, `BLOCKED_BRIDGE`)
- current/evaluated fingerprints, snapshot refs, and content identities per audit row
- deterministic rerun verification result
- blind30 gate metrics when audit exists
- `remaining_925_p0_processed: false`
- `production_modified: false`

## 5. Display lane

Produce exactly one primary `display_candidate` per canonical.

It must be:
- concise and natural for Japanese-first desktop UI;
- meaning-complete with English hidden;
- same semantic width as canonical;
- free of added/dropped actor, target, body site, relation, count, cause, intensity, subtype, or sexual context unless canonical encodes it.

If one concise label cannot be supported safely, `display_state=REVIEW`.

LOW/MEDIUM deterministic composition may reach READY only when every atomic component comes from trusted frozen identity/wording evidence, composition is transparent, and no idiom/relation/body-site ambiguity rule triggers. Otherwise escalate risk/review.

## 6. Search lane

Default goal is one exact useful Japanese term.
- second term: only common exact spelling/reading/synonym;
- third term: requires per-term justification;
- more than three accepted terms is test-version failure unless explicitly allowlisted by the spec fixture.

Automatic exact-synonym approval must reject:
- meme/joke/fandom phrase;
- subtype/child concept;
- parent/category phrase;
- attribute-added phrase;
- actor/target/context-added phrase;
- adjacent concept;
- implication-only/related/co-occurrence term;
- count change;
- object/state/action/relation type change;
- sibling collision.

A search failure must not erase an independently safe display improvement.

## 7. #32 bridge state

For overlap rows:
- same meaning fingerprint -> normal flow;
- meaning fingerprint changed after evaluation -> `STALE_REVIEW`;
- independently supported meanings are incompatible -> `CONTRADICTION`;
- generation-only changes -> no staleness.

Row derivation priority:
1. any contradiction -> `row_state=CONTRADICTION`
2. else any stale bridge -> `row_state=STALE_REVIEW`
3. else if display or search requires review -> `row_state=REVIEW`
4. else -> `row_state=READY`

`CONTRADICTION` and `STALE_REVIEW` block later promotion for the affected canonical.

## 8. Fresh unseen 100 P0 selection

Pinned source: Phase1A R2 baseline commit `a787ce39aa50f938f95612801e79f30bcdb63427`.

Eligible pool:
1. `priority == P0` in the pinned `missing_candidates.csv`;
2. exclude every canonical present in pinned `phase1a_review.csv` (the existing 100 regression fixtures);
3. do not mutate the queue during selection.

Selection seed string: `UIJA-R3-PILOT-20260908-V1`.

Stable key: `sha256(seed + "\0" + canonical)` ascending; canonical ascending is the tie-breaker.

Requested strata:
- 25 `LOW`
- 20 `MEDIUM`
- 20 `HIGH_POSE_ACTION`
- 20 `HIGH_ANATOMY_ADULT`
- 15 `CRITICAL`

Within each stratum, #32-overlap rows sort before non-overlap rows, then by stable key. This forces available overlaps into their natural strata without increasing pilot size.

If a stratum has fewer eligible rows than requested, record the shortage and fill deterministically from the next-higher-risk strata in this order:
`LOW -> MEDIUM -> HIGH_POSE_ACTION -> HIGH_ANATOMY_ADULT -> CRITICAL`.
Never fill a higher-risk shortage from a lower-risk class. If 100 rows still cannot be formed, fail closed; do not silently alter quotas.

The selected canonical list and all source hashes must be written before candidate generation.

## 9. Existing Phase1A 100 regression fixtures

The existing 100 rows remain regression fixtures. They are not part of the fresh 100 and must not be used to tune per-row overrides for the fresh pilot.

R3 tests should verify that known failure patterns are mechanically caught, including at minimum:
- `1girl`: category/noisy search term rejection;
- `simple_background`: narrower subtype rejection;
- `straddling`: sexual-subtype narrowing rejection;
- `gaping`: target/scope evidence requirement;
- `cuffs`: subtype collision handling;
- anatomy/adult HIGH rows without concrete scope evidence -> REVIEW.

No new fresh-pilot canonical-specific override table is allowed. A fix discovered during blind audit must be expressed as a reusable rule/pattern and revalidated against all matching rows.

## 10. Deterministic blind 30 audit

Blind seed: `UIJA-R3-BLIND30-20260908-V1`.
Stable blind key: `sha256(seed + "\0" + canonical)` ascending.

Target quotas:
- 4 LOW
- 5 MEDIUM
- 6 HIGH_POSE_ACTION
- 7 HIGH_ANATOMY_ADULT
- 8 CRITICAL

Within each blind stratum, #32-overlap rows sort before non-overlap rows, then by blind key. Thus every fresh #32 overlap is included when it fits the natural stratum quota. Any omitted overlap due to quota overflow must be recorded in `blind30_key.json`.

The reviewer must judge from `blind30_input.jsonl` without seeing automation state/reason fields.

Blind gate:
- semantic false READY = 0
- search-scope false READY = 0
- silently accepted #32 contradiction = 0
- deterministic rerun hashes identical
- production modified = NO

Any false READY triggers root-cause classification and **all matching-pattern revalidation**. One-row patching is forbidden.

## 11. Determinism contract

Deterministic content hashes exclude volatile timestamps and filesystem paths.

Canonical JSON serialization for hashable artifacts:
- UTF-8
- LF line endings
- stable field ordering
- stable record ordering
- `ensure_ascii=false`
- no generated timestamp in hashed semantic payload.

Running R3 twice with the same pinned inputs and frozen evidence manifest must produce identical semantic artifact hashes.

The verifier treats the existing output as the original replay and requires
the three-way equality `original == rerun1 == rerun2`. It must not accept a
rerun merely because rerun1 and rerun2 agree. Replay consumes the normalized
frozen evidence artifact; it does not re-read a live #32 worktree. Saved bridge
fingerprints are checked against a fresh calculation from the saved
translation-visible propositions.

Live source acquisition, if used, is a separate freeze step. Once `evidence_manifest.jsonl` is frozen, the evaluator never re-fetches a source during deterministic reruns.

## 12. Codex vs scheduled Task vs audit responsibilities

### Codex
Owns deterministic machinery only:
- schemas and validation;
- risk classifier/safety rails;
- candidate/evidence ingestion interfaces;
- pilot/blind selection;
- state derivation;
- hash ledger;
- regression/focused tests;
- fail-closed path protections.

Codex must not bulk-process 925 rows and must not promote production data.

### Scheduled/recurring Task (later, after test gate)
May operate repeated quarantine batches using the frozen engine:
- select next authorized batch from GitHub quarantine queue;
- acquire/freeze allowed evidence;
- run engine;
- commit only quarantine outputs;
- stop and surface REVIEW/CONTRADICTION or failed verification.

The Task must not reinterpret schema/rules and must not auto-promote production.

### Independent audit lane
Owns blind judgement and pattern-level revalidation request. It must not see automation states before judging the blind sample.

### Human
Handles unresolved REVIEW/CONTRADICTION and any policy/spec change. Human effort is not required for rows safely rejected to REVIEW.

## 13. Test-version completion gate

Codex test-version implementation is complete only when:
1. all R3 schemas validate;
2. fresh 100 selection is deterministic and matches requested/fallback rules;
3. existing Phase1A 100 are preserved as regression fixtures;
4. fresh pilot runs only in quarantine;
5. blind30 reviewer input is correctly masked;
6. original, first replay, and second replay produce identical semantic hashes;
7. production files are unchanged;
8. remaining P0 925 bulk run has not happened;
9. no main merge is performed by this test task.

Passing implementation tests authorizes only the fresh 100 dry-run + blind30 gate. It does not authorize bulk P0 or production promotion.
