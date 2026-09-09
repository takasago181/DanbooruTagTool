# Issue #36 — FINAL CONVERGENCE V3 AGENT REVIEW

Status: AUTHORITATIVE EXECUTION CONTRACT FOR CODEX / QUARANTINE ONLY

This contract replaces V2 execution behavior where they conflict. Its purpose is to end the loop by separating **development-time Codex semantic judgement** from deterministic repository validators.

The product runtime remains fully local/non-LLM. This V3 may use Codex as a development-time reviewer because the result is frozen as ordinary repository data before promotion.

## 0. Authority / branch / source

Read in order:
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #36 latest comments, especially independent V2 audit `5600982011`
4. Issue #41 final `PASS_PILOT` checkpoint `5589825869` as methodology evidence only
5. this contract

Execution branch:
`ui-ja/issue36-final-agent-convergence`

V2 audited-but-failed result HEAD:
`8d88f3f83462ab4a1fd322afc84c061c919d4a8e`

**Semantic source table for V3 must be the pre-V2 source, not the V2 95%-fallback output:**
`translation_quarantine/full_accepted_quality_sweep_20260909/final_translation_table.csv`

Source facts:
- 30,629 unique canonicals
- 23,194 accepted Japanese rows
- 7,435 fallback rows
- 1,677 `PHRASE_SEMANTICS_UNRESOLVED`

Preserve V2 infrastructure and lessons, but do not inherit V2 final row decisions merely because V2 gates said PASS.

Production promotion remains `NOT_AUTHORIZED` until fresh independent audit.

---

# 1. Product definition

Japanese exists so the user can glance/search and understand the canonical meaning.

Priority:
1. semantic correctness
2. real/readable Japanese
3. useful coverage
4. polish

Do not trade correctness for coverage. Equally, do not destroy useful coverage by treating lack of an exact phrase map as proof that an ordinary concept is unresolved.

**Core anti-collapse rule:**
A previous accepted row may be demoted only when V3 records a row-specific semantic/language defect or a row-specific unresolved ambiguity. `NO_EXACT_MAP`, `MULTIWORD`, `NO_STATIC_TEMPLATE`, `UNKNOWN_TO_SCRIPT`, or equivalent is never a sufficient demotion reason.

---

# 2. Critical architecture rule — Python is validator, not semantic reviewer

V3 has two different layers.

## A. Codex Agent Semantic Review
Codex itself, during development, reviews rows in bounded batches and writes frozen review data.

It may:
- KEEP current Japanese when semantically adequate
- REPAIR Japanese
- TRANSLATE a prior fallback
- mark TRUE_EXCEPTION
- mark EVIDENCE_UNRESOLVED only for a genuine row-specific ambiguity

This work MUST NOT be simulated by a generic Python branch that emits fallback whenever a mapping/template is absent.

## B. Deterministic Validator
Python may:
- check row counts/uniqueness
- language contamination
- malformed labels
- raw semantic English leakage
- completeness of review records
- evidence/rationale field quality
- canonical identity
- collision candidates
- state transitions
- replay of frozen decisions
- protected boundaries
- tests

Python MUST NOT invent the semantic decision for review-required rows.

---

# 3. Durable agent-review data

New root:
`translation_quarantine/final_agent_convergence_v3_20260909/`

Required:
- `review_queue.jsonl`
- `batch_progress.json`
- `agent_semantic_decisions/` (one JSONL per completed batch)
- `agent_challenge_decisions/` (independent second-pass challenge batches)
- `merged_agent_decisions.jsonl`
- `residual_fallback_challenge.jsonl`
- `collision_review.jsonl`
- `adversarial_agent_audit.jsonl`
- `final_rows.jsonl`
- `final_translation_table.csv`
- `final_translation_table.md`
- `coverage_summary.json`
- `transition_summary.json`
- `language_quality_summary.json`
- `semantic_quality_summary.json`
- `exception_ledger.jsonl`
- `replay_verification.json`
- `protected_boundary.json`
- `gate_status.json`
- `FINAL_REPORT.md`

The queue covers all 30,629 rows exactly once. Agent semantic review is required only where not strongly trusted as described below.

Recommended batch size: 100–150. Persist every completed batch before moving on. The task is restartable from batch files.

---

# 4. Initial lanes

Every row gets exactly one provisional lane.

## `TRUSTED_EXACT`
Allowed only for strong whole-canonical evidence already validated by prior #36/#41/qualified artifacts or explicit audited repair.

## `AGENT_REVIEW_KEEP_OR_REPAIR`
Prior accepted Japanese without strong exact proof. Current Japanese is a candidate, not authority. Codex decides KEEP / REPAIR / FALLBACK.

## `AGENT_REVIEW_TRANSLATE_OR_FALLBACK`
Ordinary translatable fallback rows, including all 1,677 `PHRASE_SEMANTICS_UNRESOLVED` and prior language/raw/malformed demotions when the canonical concept itself is ordinary and understandable.

## `TRUE_ORIGINAL_FORM_EXCEPTION_CANDIDATE`
Names, products, codes, symbols, titles, opaque identity strings. Codex validates that original form is genuinely preferable.

No static route/state alone can skip an agent review except `TRUSTED_EXACT`.

---

# 5. Agent semantic decision schema

For each reviewed row persist at least:
- `canonical`
- `source_state`
- `source_display_ja`
- `source_search_ja`
- `lane`
- `decision`: `KEEP_JA` / `REPAIR_JA` / `TRANSLATE_JA` / `TRUE_EXCEPTION` / `EVIDENCE_UNRESOLVED`
- `final_display_ja`
- `final_search_ja`
- `semantic_gloss_ja`
- `semantic_facets`
- `risk_class`
- `decision_rationale_ja`
- `evidence_refs`
- `unresolved_question_ja` when unresolved
- `review_mode`: must be `CODEX_AGENT_SEMANTIC_REVIEW`
- `batch_id`

Semantic facets when applicable:
- head concept
- action/state
- actor
- ownership
- target
- body site
- direction/spatial relation
- count/cardinality
- negation
- required modifier
- qualifier scope
- concept width

`decision_rationale_ja` must be row-specific. A generic generated template repeated across large classes is invalid evidence.

---

# 6. Agent review rules

### Prior accepted rows
Do not demote merely for missing external proof. Codex may KEEP when it can semantically determine that the current Japanese preserves the canonical meaning.

Demote only for:
- actual meaning mismatch
- scope loss/expansion
- Chinese/non-Japanese
- raw semantic English leakage
- malformed display
- material unresolved ambiguity

### Prior fallback rows
For ordinary concepts, Codex should actually translate when the whole canonical meaning is clear from ordinary language/domain knowledge and semantic structure.

External evidence is useful for ambiguous/specialized cases but is not mandatory for every ordinary concept.

### 1,677 phrase rows
Every row gets an agent semantic decision. `EVIDENCE_UNRESOLVED` is allowed only for a genuine ambiguity and requires a specific Japanese unresolved question. Lack of an exact map/template is forbidden as the reason.

### Search label
Search Japanese may equal display Japanese when a conservative exact-equivalent term is sufficient. Do not invent broad synonyms merely to increase recall.

---

# 7. Independent agent challenge pass

After first-pass decisions are frozen, perform a second Codex pass with a **skeptical/challenge role** over:
- every HIGH/CRITICAL accepted row
- every REPAIR_JA / TRANSLATE_JA row
- every EVIDENCE_UNRESOLVED row from the 1,677 phrase set
- every collision candidate
- deterministic random 10% of remaining KEEP_JA rows

Challenge output:
- `CONFIRM`
- `REPAIR_REQUIRED`
- `FALLBACK_REQUIRED`
- `RESOLVABLE_FALLBACK` (important: fallback was unnecessarily conservative)

Challenge rationale must be row-specific.

Codex must internally repair/re-review until `REPAIR_REQUIRED` and `RESOLVABLE_FALLBACK` are zero in the challenge population.

The challenge pass may not call the same deterministic function as the first pass and declare it independent.

---

# 8. Residual fallback anti-collapse gate

Final non-exception fallback rows require special scrutiny.

Build a deterministic sample of at least 300 residual ordinary fallbacks (or all if fewer than 300). Run an independent Codex challenge asking only:
`Can this canonical be translated safely enough for glance-understanding without inventing meaning?`

Result:
- `TRULY_UNRESOLVED`
- `RESOLVABLE`

If ANY meaningful pattern of `RESOLVABLE` appears, define the reusable class and reprocess the full affected class before completion.

At final terminal state, the residual sample must contain zero `RESOLVABLE` results.

This gate exists specifically to prevent V2-style 95% fallback collapse.

---

# 9. Coverage utility gate

There is no target percentage that overrides correctness. However V3 may not call itself complete if coverage collapsed because review work was avoided.

Required reporting:
- source accepted: 23,194
- source fallback: 7,435
- kept accepted
- repaired accepted
- demoted accepted by concrete reason
- translated prior fallback
- true exceptions
- evidence-unresolved residual

If final accepted coverage falls by more than 20 percentage points from the 23,194/30,629 source level, terminal status must be `HOLD_COVERAGE_COLLAPSE` unless the independent challenge evidence demonstrates the demotions are genuinely necessary.

`HOLD_COVERAGE_COLLAPSE` is not completion.

This is an anti-gaming threshold, not a translation target.

---

# 10. Deterministic validators

Validators must enforce:
- 30,629 unique canonical rows
- canonical identity/order unchanged
- all queue rows have terminal decisions
- no generic REVIEW/PENDING
- no Chinese-only accepted output
- no raw English semantic core except allowed identity material
- no malformed accepted labels
- all accepted rows have first-pass semantic record
- all required challenge rows have challenge record
- all final accepted challenge verdicts compatible with acceptance
- all residual ordinary fallback sample verdicts `TRULY_UNRESOLVED`
- fallback has concrete subtype/reason
- no `NO_EXACT_MAP`/`MULTIWORD`/`NO_TEMPLATE` reason
- replay PASS from frozen decisions
- protected boundary PASS
- production modified NO

---

# 11. Collision review

Do not demote all duplicate Japanese automatically.

For each duplicate/sibling risk, Codex challenge records whether:
- duplicate is semantically legitimate
- labels need differentiation
- one/both are mistranslated

Ownership/count/direction/action-state distinctions must be preserved.

---

# 12. Final adversarial AGENT audit

After final rows are frozen, perform an agent semantic audit, not just deterministic verifier reuse.

Minimum 600 rows:
- 150 random accepted
- 150 HIGH/CRITICAL accepted
- 150 repaired/new translations
- 150 residual fallback/true exceptions

Force-include all historical #36 blockers.

For each record:
- canonical
- final Japanese/fallback
- fresh semantic judgement
- `PASS` / `REPAIR_REQUIRED` / `RESOLVABLE_FALLBACK`
- Japanese rationale

Any failure triggers full-class repair and regeneration of the audit.

Final adversarial audit must have zero `REPAIR_REQUIRED` and zero `RESOLVABLE_FALLBACK`.

---

# 13. Historical regressions

Carry forward all historical fixtures from V2 and earlier #36 audits, including language, malformed, phrase/polysemy, actor-target, qualified-label, and original-form controls.

Do not weaken a regression by accepting either Japanese or fallback when a previously validated exact Japanese repair exists; validated exact repairs must remain exact unless a documented semantic correction supersedes them.

---

# 14. Final terminal gates

`gate_status.json` must include at least:
1. `row_count_30629_unique`
2. `canonical_identity_unchanged`
3. `review_queue_complete`
4. `agent_first_pass_complete`
5. `agent_challenge_complete`
6. `challenge_repair_required_zero`
7. `challenge_resolvable_fallback_zero`
8. `phrase_1677_agent_review_complete`
9. `accepted_language_gate_pass`
10. `accepted_semantic_records_complete`
11. `fallback_reason_specificity_pass`
12. `residual_fallback_agent_challenge_pass`
13. `coverage_anti_collapse_pass`
14. `collision_agent_review_pass`
15. `adversarial_agent_audit_600_pass`
16. `historical_regressions_pass`
17. `deterministic_replay_pass`
18. `protected_boundary_pass`
19. `production_modified_no`
20. `focused_regression_tests_reported`
21. `full_pytest_reported_accurately`

Allowed terminal:
- `FINAL_READY_FOR_INDEPENDENT_AUDIT`
- `HOLD_EXTERNAL_EVIDENCE` only for a finite enumerated residual set after all internal agent review/challenge is complete

Forbidden terminal:
- `PARTIAL_DONE`
- `HOMEWORK_RETAINED`
- `SAFE_FOR_NOW`
- `HOLD_COVERAGE_COLLAPSE` as completion

Codex must continue within the same task until an allowed terminal is reached.

---

# 15. Tests

Tests must validate the contract, not hardcode a convenient bad output distribution.

Forbidden test patterns:
- asserting a large expected fallback count because the current resolver produces it
- treating `PASS` and `FALLBACK_REQUIRED` as equivalent evidence of product quality
- accepting historical fixtures as either Japanese or fallback when an exact validated repair is known

Required tests:
- data/schema completeness
- invalid generic fallback reasons rejected
- challenge coverage completeness
- residual fallback challenge gate
- coverage anti-collapse gate
- language/malformed/raw-token controls
- semantic facet preservation fixtures
- collision behavior
- historical exact repairs
- replay/protected boundary
- full pytest accounting

---

# 16. Scope

Allowed:
- `translation_quarantine/**`
- tests directly required for #36 V3

Forbidden:
- production `data/**`
- Japanese production overlay
- #32 data/verdicts
- #35 UI
- #41 writes
- `CURRENT_DEV_TASK.md`
- main
- Stage10 production A/B

No production promotion in V3.

---

# 17. Completion report

Report only at allowed terminal:
- execution start HEAD
- final HEAD
- source table/hash
- all transition counts
- first-pass agent review row count
- challenge row count
- phrase 1,677 outcomes
- residual fallback challenge size/outcomes
- final accepted/fallback counts and percentages
- coverage delta vs source
- demotion reasons
- translated prior-fallback count
- collision results
- adversarial 600 results
- historical regressions
- replay/protected verdicts
- focused/full pytest accounting
- `production_modified: NO`
- `promotion: NOT_AUTHORIZED`

Fresh independent ChatGPT audit remains mandatory before any production promotion.
