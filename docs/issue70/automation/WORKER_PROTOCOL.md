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


## Recovery and resume

Every worker run is restartable. A stopped run must be treated as an interrupted checkpoint, not as permission to restart the lane from zero.

Before doing new research:
1. Re-read the authority CURRENT_MANIFEST.json.
2. Read this lane's existing files for the current cycle.
3. Reuse every already validated row whose manifest hash still matches.
4. Continue only the assigned rows that are not already safely completed.

Checkpoint after each research cluster or before a risky/long operation by committing lane-local progress under the current cycle directory. Recommended optional files are:
- `PARTIAL_RESULTS.csv`
- `CHECKPOINT.json`

A later run must reuse these checkpoints and must not repeat completed web research unless the saved evidence is inconsistent.

Classify failures before changing anything:
- rate limit / 429 / timeout: keep the checkpoint and resume later; do not change semantics.
- stale branch / push race: refresh the lane branch and retry only the mechanical publish step; never force-push.
- CSV/schema/quoting error: fix only the malformed artifact or existing component; preserve the semantic decisions.
- lane-local logic error: fix the current lane artifact/process in place.
- shared Manifest / Integrator / authority workflow error: do not patch authority from a worker. Write `RECOVERY_REQUEST.json` in the lane cycle directory with the observed failure and stop cleanly.
- evidence uncertainty: leave the row unresolved instead of guessing.

`RECOVERY_REQUEST.json` should contain issue=70, cycle_id, lane, manifest_progress_sha256, failure_class, observed_error, affected_paths, and production_modified=false.

A worker must not create alternate v2/v3 recovery workflows or branches. Recovery always resumes the same cycle and same lane until the manifest changes.

## Shared recovery watchdog

A separate recovery watchdog may inspect GitHub Actions and all lane branches. It may repair only shared automation/framework mechanics on the authority branch and may retry failed GitHub jobs. It must never invent or alter semantic verdicts for worker rows.

The watchdog must:
- inspect the failed job/step/log before editing;
- fix the existing script/workflow in place rather than create v2/v3 variants;
- use optimistic locking and never force-push;
- retry only failed jobs when possible;
- preserve all completed lane research and overlays;
- leave production/runtime/source/main and PR #115 untouched;
- stop if a repair would require changing semantic judgments.


## Reviewed unresolved rows

A worker must not repeatedly research the same difficult assigned row every hourly run.

When an assigned row has received a good-faith evidence check in the current cycle but still cannot be resolved at HIGH confidence, record it in:
`docs/issue70/automation/cycles/<cycle_id>/lane-<N>/REVIEWED_UNRESOLVED.csv`

Required columns:
`cycle_id,lane,manifest_progress_sha256,row_id,canonical_tag,category,post_count,review_status,review_reason,evidence_refs,audit_note`

Rules:
- `review_status` must be `REVIEWED_UNRESOLVED`.
- Only assigned row_ids may appear.
- A row must never appear in both RESULTS.csv and REVIEWED_UNRESOLVED.csv for the same cycle.
- `review_reason` and `audit_note` must explain why HIGH-confidence resolution was not safe.
- `evidence_refs` may contain checked URLs or be blank when no trustworthy first-party source could be established.
- Recording reviewed-unresolved is not a semantic verdict and does not change the external audit state.
- Once a row is recorded reviewed-unresolved, do not search it again in later hourly runs of the same cycle.
- A worker may complete a lane below target_resolutions after it has made a reasonable pass over its assignment and recorded the genuinely checked-but-unresolved rows. Safety wins over quota.

During integration, explicit reviewed-unresolved rows are aggregated into:
`docs/issue70/automation/REVIEWED_UNRESOLVED.csv`

The next Manifest prioritizes never-reviewed unresolved rows ahead of this registry. Reviewed rows remain eligible later, so new official evidence or exhaustion of fresh rows can bring them back; they are deferred, not permanently discarded.


## 2D-only media scope

Issue #70 now audits only the user's 2D/fictional-content scope for Character and Copyright.

This is a media/identity scope rule, not a rendering-technique rule:
- Anime, manga, games, visual novels, VTubers, illustrated fictional IP, and fictional game characters remain in scope even when rendered with 3D CG.
- Artist remains fully in scope. Never exclude an Artist merely because the creator is a real person.
- Character / Copyright that are clearly real-world or live-action-only may be marked REAL_3D and skipped from further semantic audit.
- Clear REAL_3D examples include real people/celebrities/idol groups, real sports or tournaments, real-world events, live-action-only TV/film properties, companies/services, and general commercial brands when the tag identity is the real entity rather than a fictional/illustrated property.
- Mixed-media franchises, fictional properties with both animation and live action, ambiguous brands/IP, or anything not clearly REAL_3D must NOT be auto-skipped. Treat them as UNCERTAIN and keep them in the normal audit flow.

Before doing expensive semantic research on a Character or Copyright row, perform a cheap scope check. When it is clearly out of scope, write:
`docs/issue70/automation/cycles/<cycle_id>/lane-<N>/SCOPE_SKIPPED.csv`

Required columns:
`cycle_id,lane,manifest_progress_sha256,row_id,canonical_tag,category,post_count,media_scope,scope_reason,evidence_refs,audit_note`

Rules:
- `media_scope` must be `REAL_3D`.
- Only Character or Copyright rows may appear. Artist is forbidden.
- Only assigned row_ids may appear.
- A row must not also appear in RESULTS.csv or REVIEWED_UNRESOLVED.csv in the same cycle.
- `scope_reason` must state the concrete reason such as real person, real sports event, live-action-only property, company/service, or general real-world brand.
- Evidence URL is optional for an obvious scope classification, but use one when it materially disambiguates the identity.
- Scope skipping is not a semantic translation verdict and must not create KEEP/FIX decisions.
- Do not spend time finding official Japanese title/name translations for a row after it has been safely classified REAL_3D.

The Integrator aggregates these rows into:
`docs/issue70/automation/SCOPE_SKIPPED_NON_2D.csv`

Rows in that registry are excluded from future manifests while remaining traceable in the raw external-audit accounting. This allows raw remaining counts to include out-of-scope history without wasting future worker time. Existing already-resolved rows are not rolled back merely because this scope rule was introduced later.
