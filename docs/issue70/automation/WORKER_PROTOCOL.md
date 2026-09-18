# Issue #70 — Five-Lane Automation Protocol

## Authority
Canonical branch: `audit/issue70-semantic-final`.
Workers MUST NOT write to the authority branch.

Current assignment: `docs/issue70/automation/CURRENT_MANIFEST.json`.
Archived assignment: `docs/issue70/automation/cycles/cycle-XXXX/MANIFEST.json`.

## Worker branches
- Lane 1: `audit/issue70-auto-lane-1`
- Lane 2: `audit/issue70-auto-lane-2`
- Lane 3: `audit/issue70-auto-lane-3`
- Lane 4: `audit/issue70-auto-lane-4`
- Lane 5: `audit/issue70-auto-lane-5`

A worker may write only to its own lane branch and only under:
`docs/issue70/automation/cycles/<cycle_id>/lane-<N>/`.

## Assignment rule
Read CURRENT_MANIFEST.json from the authority branch on every run.
Process only row_ids assigned to your lane. Never take unassigned rows and never refill the lane.

Rows with `seed_shortlist_source` were already verified in the interactive audit. Reuse the seed verdict and evidence after checking that the manifest row still matches. Do not repeat web research unless the seed is inconsistent.

For non-seeded rows:
- Prefer official / first-party sources.
- Copyright: formal official title for display; useful short names may go to search; never narrow umbrella tags.
- Character: confirmed official Japanese name only; do not invent fan/mob/form translations.
- Artist: never guess readings; official profile/credit only, otherwise identity-safe canonical/Romanized form.
- Allowed verdicts: KEEP / FIX_DISPLAY / FIX_SEARCH / FIX_BOTH.
- confidence=HIGH.
- approval_status=PROPOSED.
- Evidence must be a real URL.
- If unsafe to resolve, omit the row from RESULTS.csv rather than guessing.
- Aim for target_resolutions but safety wins over quota.
- Research in clusters of roughly 20–30 rows.

## RESULTS.csv
Path: `docs/issue70/automation/cycles/<cycle_id>/lane-<N>/RESULTS.csv`

Required columns:
`cycle_id,lane,manifest_progress_sha256,row_id,canonical_tag,category,post_count,display_ja,search_ja,prior_audit_verdict,audit_verdict,proposed_display_ja,proposed_search_ja,reason_code,confidence,evidence_refs,audit_note,approval_status`

## STATUS.json
Write in the same commit:
`docs/issue70/automation/cycles/<cycle_id>/lane-<N>/STATUS.json`

Required fields:
format_version=1, issue=70, cycle_id, lane, manifest_progress_sha256, complete=true, assigned_count, target_resolutions, resolved_count, production_modified=false.

## Integration
Workers never merge themselves.
The GitHub Actions workflow Issue70 Parallel Integrator serializes authority integration using one concurrency group. It waits for all five lane outputs from the same cycle and manifest hash, validates row ownership and invariants, then writes one external_resolution_parallel_cycle-XXXX.csv overlay.

A new manifest is generated only after authority external progress changes.

## Prohibited
Never:
- write or merge main
- merge PR #115
- modify production/runtime/source data
- modify authority queue/progress files from a worker
- write another lane
- resolve row_ids outside the manifest
- force-push
- create v2/v3/etc. parallel workflows to bypass a failure

Fix existing components in place and preserve completed semantic research.
