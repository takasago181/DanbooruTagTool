# Issue #36 — FINAL CONVERGENCE V2

Status: AUTHORITATIVE EXECUTION CONTRACT FOR CODEX / QUARANTINE ONLY

This contract supersedes the execution behavior of earlier #36 reconciliation instructions where they conflict. It is designed to end repeated one-row audit/rework loops. Codex must complete the whole pipeline below in one execution lane and must not report "done" after only implementing a detector, applying fixture repairs, or carrying unresolved homework forward unchanged.

## 0. Authority / source / branch

Read in this order before work:
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #36 latest comments
4. Issue #41 final `PASS_PILOT` checkpoint `5589825869` as methodology evidence only; do not reopen/rerun #41
5. this contract

Branch:
`ui-ja/issue36-machine-convergence`

Current implementation source HEAD before this contract:
`74ce389f433d23f7f036313bac9e82a7bb6377e2`

Current source artifact:
`translation_quarantine/full_accepted_quality_sweep_20260909/final_translation_table.csv`

Current source facts:
- 30,629 unique canonicals
- 23,194 accepted rows
- 7,435 fallback rows
- 1,677 fallback rows with `PHRASE_SEMANTICS_UNRESOLVED`
- production modified: NO

Previous sweep achievements must be preserved:
- whole accepted layer mechanically screened
- 4,549 unsafe accepted rows demoted
- 22 known defects repaired
- replay PASS
- protected boundary PASS

Previous sweep deficiency that this contract MUST fix:
- semantic review only covered known fixture rows, not the actual candidate population
- 1,677 phrase-semantic homework rows were carried forward without real resolution attempts

Production promotion remains `NOT_AUTHORIZED` until a fresh independent audit passes the final result.

---

# 1. Product-quality definition

Japanese overlay purpose:
`canonical English remains authoritative; Japanese exists so the user can glance/search and understand the canonical meaning.`

Priority order:
1. semantic correctness
2. actually Japanese / readable Japanese
3. useful coverage
4. stylistic polish

Allowed:
- awkward but semantically correct Japanese
- conventional Latin acronyms / product codes / franchise qualifiers when identity-bearing
- honest English fallback when meaning cannot be safely resolved

Forbidden:
- Chinese-only text accepted as Japanese
- raw English semantic-core tokens hidden inside Japanese punctuation
- malformed brackets/wrappers
- noun/verb or action/state substitution
- actor / owner / target / body-site loss
- direction / spatial relation loss
- count/cardinality loss
- negation loss
- required qualifier loss
- broad/narrow concept substitution
- accepting a row only because it passed a superficial regex or because an older state already said `JA_ACCEPT_*`

Coverage must never override correctness, but ordinary resolvable concepts must not be parked in fallback merely to avoid work.

---

# 2. Core architecture — separate resolver and verifier

Implement two logically separate components:

## 2.1 Resolver
Produces a proposed final decision for every row that requires semantic work.

Resolver output must include at least:
- `canonical`
- `source_state`
- `source_route`
- `source_display_ja`
- `decision`
- `proposed_display_ja`
- `proposed_search_ja`
- `semantic_gloss_en`
- `semantic_facets`
- `evidence_tier`
- `evidence_refs`
- `unresolved_reason` when fallback

## 2.2 Verifier
Must not simply call the same `quality_flags()` used by the resolver and declare success.
It must independently consume the canonical + proposed Japanese + structured semantic record and issue:
- `PASS`
- `FAIL_REPAIR_REQUIRED`
- `FALLBACK_REQUIRED`

For high-risk rows it must explicitly verify preserved facets.

Codex must iterate resolver -> verifier -> correction -> verifier internally until no `FAIL_REPAIR_REQUIRED` remains.

A single known-fixture map is not a verifier.
A regex language detector is not a semantic verifier.

---

# 3. Durable work queue — no context-loss / no manual handoff assumption

Create a new root:
`translation_quarantine/final_convergence_v2_20260909/`

Required durable files:
- `work_queue.jsonl`
- `batch_progress.json`
- `resolver_results.jsonl`
- `verifier_results.jsonl`
- `exception_ledger.jsonl`
- `final_rows.jsonl`
- `final_translation_table.csv`
- `final_translation_table.md`
- `coverage_summary.json`
- `language_quality_summary.json`
- `semantic_quality_summary.json`
- `collision_review.jsonl`
- `adversarial_audit.jsonl`
- `replay_verification.json`
- `protected_boundary.json`
- `gate_status.json`
- `FINAL_REPORT.md`

`work_queue.jsonl` must cover all 30,629 canonicals exactly once.

`batch_progress.json` must make the process restartable without redoing completed batches.
Recommended semantic-review batch size: 100-200 rows.

Codex may make intermediate commits, but MUST continue working in the same task until the final gate is terminal.
Do not stop after Phase A/Phase B and call it completion.

---

# 4. Phase A — classify every row into an evidence lane

Every canonical must receive exactly one lane:

## A. `TRUSTED_ACCEPT`
Use only when the Japanese label has strong whole-canonical support such as:
- exact-canonical human/strict evidence already frozen in qualified/R3 artifacts
- #41 exact-canonical validated evidence where overlapping
- exact-canonical trusted local Japanese asset with identity match
- an already audited exact repair from prior #36 rounds

Previous `JA_ACCEPT_MACHINE` alone is NOT sufficient evidence.
Previous `JA_ACCEPT_EXISTING` alone is NOT automatically sufficient if provenance is unknown.

## B. `NEEDS_SEMANTIC_REVIEW`
Everything accepted/fallback that is translatable but lacks whole-canonical proof.
This includes route/source-risk rows, especially legacy machine/lightweight/direct/lexical composition.

## C. `TRUE_ORIGINAL_FORM_EXCEPTION`
Only identity/code/symbol/product/title/proper-name/opaque rows where Japanese translation is not necessary or would damage identity.
Record a concrete exception subtype.

## D. `UNRESOLVED_REVIEW_REQUIRED`
Temporary only during processing. This lane MUST be empty at final output.

No row may remain accepted merely because mechanical language screening found no simplified Chinese or raw English.

---

# 5. Phase B — semantic fingerprint for review rows

For every `NEEDS_SEMANTIC_REVIEW` row, create a structured semantic fingerprint before deciding Japanese wording.

At minimum record when applicable:
- `head_concept`
- `action_or_state`
- `actor`
- `ownership`
- `target`
- `body_site`
- `direction_or_spatial_relation`
- `count_or_cardinality`
- `negation`
- `required_modifier`
- `qualifier_scope`
- `concept_width_note`

Do not derive acceptance from the Japanese wording itself.

Risk escalation:
- relation / actor-target / ownership -> HIGH
- anatomy/adult action/body-site -> HIGH
- direction/spatial -> HIGH
- count/cardinality -> HIGH
- action-vs-state / noun-vs-verb polysemy -> HIGH
- negation -> HIGH
- qualified/proper identity ambiguity -> HIGH

LOW risk is limited to transparent singleton/common concrete concepts with strong evidence.

---

# 6. Phase C — resolve the 1,677 phrase homework rows for real

All current `PHRASE_SEMANTICS_UNRESOLVED` rows MUST enter `NEEDS_SEMANTIC_REVIEW`.

They may not be bulk-carried forward with a generic status such as `TRANSLATION_HOMEWORK_UNRESOLVED` without a per-row resolution attempt.

Each row must end as one of:

## `RESOLVED_JA`
Requirements:
- whole phrase meaning established
- semantic fingerprint recorded
- concise Japanese proposed
- verifier PASS

## `TRUE_EXCEPTION`
Requirements:
- genuine original-form identity/code/symbol/product/proper-name exception
- concrete reason subtype

## `EVIDENCE_UNRESOLVED_FALLBACK`
Allowed only when:
- exact concept remains materially ambiguous after attempting available evidence
- `attempted_evidence` is non-empty
- `specific_unresolved_question` is non-empty
- fallback is not chosen merely because translation is multiword or inconvenient

A run with `phrase_rows_resolved = 0` is an automatic CONTRACT FAIL unless all 1,677 rows independently qualify as true exceptions or evidence-unresolved with specific per-row evidence records. A single generic branch in code that retains all 1,677 is forbidden.

Do not use per-token concatenation as a general solution.

---

# 7. Evidence order

For any semantic review, use this order:
1. exact-canonical trusted Japanese evidence already in repository artifacts
2. exact-canonical R3/#41/qualified semantic evidence
3. exact-canonical local authoritative asset / exact identity reference
4. canonical structure only when relation is unambiguous and the translation pattern is explicitly validated
5. conservative Codex-generated wording with recorded semantic fingerprint

If external evidence is unavailable, do not stop the whole run. Resolve safe concepts conservatively and use `EVIDENCE_UNRESOLVED_FALLBACK` only for genuinely ambiguous residuals.

Do not require owner intervention for ordinary translation decisions.

---

# 8. Phase D — accepted-layer semantic revalidation

The current 23,194 accepted rows must not all be trusted by default.

At minimum force `NEEDS_SEMANTIC_REVIEW` for accepted rows matching any of:
- legacy `JA_ACCEPT_MACHINE` with weak/unknown whole-canonical provenance
- `LIGHTWEIGHT`
- `DIRECT_TRANSLATION`
- `LEXICAL_COMPOSITION`
- historical token composition
- label generated from broad synonym rather than exact canonical identity
- multi-token canonical with no exact phrase evidence
- high-risk semantic facet from Section 5
- suspiciously short/generic Japanese relative to a specific multi-token canonical
- duplicate Japanese label shared by semantically unrelated canonicals

The resolver may confirm the current wording, repair it, or demote it.

Do not require manual semantic review of rows with strong trusted exact-canonical evidence; record why they are trusted.

---

# 9. Phase E — language / malformed / raw-token gate

Apply whole-table checks to final accepted rows:
- simplified-Chinese-specific contamination
- strong Chinese-only grammar/lexicon patterns
- raw English semantic-core tokens except explicit allowed identity acronyms/codes
- unmatched brackets
- broken qualifiers
- wrapper remnants
- blank/near-empty descriptive body

Do not use generic `[一-龥]` as proof of Japanese.
Do not blanket reject valid kanji-only Japanese.

Allowed-original-form controls must be present in tests to prevent over-filtering.

---

# 10. Phase F — semantic collision / sibling check

Build a collision report for accepted Japanese labels.

Flag for review when:
- same Japanese label maps to multiple unrelated canonicals
- a Japanese label appears to describe a known sibling/neighbor concept instead of the source canonical
- broad synonym collapses distinctions such as ownership, count, direction, action/state, or object class

Duplicate Japanese is not automatically invalid; reviewer/verifier records whether the duplicate is semantically legitimate.

This gate exists specifically to catch failures like a source canonical being translated as a related but different concept.

---

# 11. Phase G — fixed adversarial audit before completion

Before Codex may report completion, generate a deterministic adversarial audit set from the FINAL table.

Use a fixed seed derived from the final table SHA-256 and include at minimum:
- 100 random accepted rows
- 100 high-risk accepted rows
- 100 rows repaired/resolved in this V2 pass
- 100 final fallback/exception rows

Also force-include all historical blocker examples from prior #36 audits.

For every sampled row record:
- canonical
- Japanese/fallback
- semantic fingerprint summary
- verifier verdict
- why it is safe

Any discovered pattern-wide defect requires:
1. reusable rule/fix
2. re-run against the full affected class
3. regenerate audit set/result

Do not patch only the sampled row.

---

# 12. Mandatory historical regression fixtures

Must preserve/fix at minimum:

Language/non-Japanese:
- `:p`
- `^_^`
- `anal_object_insertion`
- `imminent_anal`
- `presenting_own_anus`
- `presenting_own_ass`
- `presenting_own_pussy`
- `vibrator_bulge`
- `vibrator_cord`
- `vibrator_in_anus`
- `vibrator_on_clitoris`
- `vibrator_on_nipple`
- `vibrator_on_penis`

Raw/malformed/scope:
- `presenting_own_foot`
- `a_(phrase)`
- `imminent_penetration`
- `android`

Earlier phrase/polysemy blockers:
- `painting_fingernails`
- `painting_toenails`
- `hydraulic_press`
- `building_snowman`
- `building_sand_sculpture`
- `break_action`
- `shooting_star_(symbol)`
- `shot_glass`
- `shredded_muscles`

Earlier wrapper/raw-English blockers:
- `heavy_chromatic_aberration`
- `knees_together_feet_apart`
- `fictional_aircraft`
- `finger_counting_duo`
- `father_and_son_threesome`
- `nipples_pressed_together`
- `no_genitals`
- `tank_gun`
- `tears_of_joy_emoji`
- `the_fool_(tarot)`
- `no_magazine_(weapon)`
- `newt`

Preserve validated qualified examples:
- `human_(warcraft)`
- `hydro_symbol_(genshin_impact)`
- `advanced_ship_(eve_online)`

---

# 13. Final state model

Final table may contain only:
- `JA_ACCEPT_EXISTING`
- `JA_ACCEPT_MACHINE`
- `JA_ACCEPT_STRICT`
- `ENGLISH_FALLBACK_EXCEPTION`

No `REVIEW`, `PENDING`, `UNRESOLVED_REVIEW_REQUIRED`, or internal batch state may remain.

For every final accepted row:
- nonblank display/search
- Japanese readability gate PASS
- semantic verifier PASS
- evidence/provenance recorded in V2 ledger

For every final fallback row:
- explicit subtype/reason
- either true original-form exception or specific evidence-unresolved reason
- no generic "multiword so fallback" reason

---

# 14. Completion gate — Codex must self-iterate until terminal

Create `gate_status.json` with each gate explicitly PASS/FAIL:

1. `row_count_30629_unique`
2. `canonical_identity_unchanged`
3. `work_queue_complete_30629`
4. `temporary_review_state_zero`
5. `accepted_language_gate_pass`
6. `accepted_semantic_verifier_pass`
7. `phrase_1677_individually_processed`
8. `fallback_reason_specificity_pass`
9. `collision_review_complete`
10. `adversarial_audit_400_pass`
11. `historical_regressions_pass`
12. `deterministic_replay_pass`
13. `protected_boundary_pass`
14. `production_modified_no`
15. `focused_and_regression_tests_reported`
16. `full_pytest_reported_accurately`

Codex must NOT report task completion while any gate is FAIL.

Within the same execution slot:
- inspect failing gate
- fix reusable root cause
- rerun affected class
- rerun gates

Terminal outcomes allowed:

## `FINAL_READY_FOR_INDEPENDENT_AUDIT`
All 16 gates PASS.

## `HOLD_EXTERNAL_EVIDENCE`
Only allowed if all computable/internal gates pass and a finite, enumerated set of rows genuinely cannot be resolved without unavailable exact-canonical evidence. Those rows remain explicit fallback. The hold report must name the count and exact reason; it must not hide unprocessed work.

`PARTIAL_DONE`, `SAFE_FOR_NOW`, `HOMEWORK_RETAINED`, or equivalent is not an allowed terminal outcome.

---

# 15. Tests

Required:
- focused V2 resolver/verifier tests
- language detector tests including Japanese kanji-only controls and Chinese contamination controls
- semantic fingerprint/verifier tests across action/object/state/direction/count/ownership/negation
- collision tests
- all historical #36 regressions
- relevant R3/qualified-label regressions
- deterministic replay
- protected-boundary verification
- full pytest

Full pytest reporting rule remains:
If Windows TEMP ACL / `WinError 5` setup/finalize errors occur, report exact counts and do not call the full suite PASS. Product/assertion failures are blockers.

---

# 16. Scope boundaries

Allowed writes:
- `translation_quarantine/**`
- tests directly required for #36 V2 reconciliation

Forbidden:
- production `data/**`
- `data/runtime/japanese_overlay.json`
- runtime production indexes
- canonical English identity changes
- Prompt/cooccur/recommendation behavior
- semantic-support production data
- generation metadata
- #32 data/verdicts
- #35 UI
- #41 state/artifacts except read-only evidence reuse
- `docs/project/CURRENT_DEV_TASK.md`
- main
- Stage10 production A/B

No production promotion in this task.

---

# 17. Final report requirements

When and only when terminal outcome is reached, commit/push and report:
- execution start HEAD
- final HEAD
- changed files
- final table hash
- accepted/fallback counts
- number of rows in each evidence lane
- number of semantic-review rows processed
- number of prior accepted rows confirmed / repaired / demoted
- phrase 1,677: resolved / true-exception / evidence-unresolved counts
- Chinese/raw-English/malformed fixes
- collision review counts/outcomes
- adversarial audit 400 results
- historical regression result
- replay result
- protected boundary result
- focused/regression/full pytest results
- production_modified
- terminal enum
- explicit `promotion: NOT_AUTHORIZED`

Then STOP for fresh independent ChatGPT audit.
