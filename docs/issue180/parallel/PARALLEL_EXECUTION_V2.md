# Issue #180 Parallel Authority-Campaign Execution v2

Status: **ACTIVE research execution contract**  
Canonical research branch: `research/issue180-single-home-pilot`  
Target: `Character -> HOME_COPYRIGHT (0..1)`

v2 is specific to Issue #180. It replaces the v1 assignment/epoch model with **authority campaigns**. The semantic policy, evidence bar, v3 resolver, migration provenance and #179 identity boundary are unchanged.

## 1. Roles

Use exactly five Worktrees:

- Forward 0 — `research/issue180-forward-0`
- Forward 1 — `research/issue180-forward-1`
- Forward 2 — `research/issue180-forward-2`
- Forward 3 — `research/issue180-forward-3`
- QA / Integrator — `research/issue180-qa-integrator`

Forward discovers and checks reusable authority. QA is the only canonical writer.

## 2. Issue #180 work unit = reusable authority, not row count

The scheduler groups current residual work by the authority that can be reused:

- `authority:<key>` — unifies matching family/discovery-roster leads so the same work authority is not researched by two lanes;
- `base:<character>` — validate variant/base identity once and reuse the confirmed base HOME;
- other non-ungrouped subjects remain one stable campaign;
- only genuinely structure-free direct long-tail work falls back to `direct:<canonical_tag>`.

Do **not** split one reusable family/roster/base authority across lanes merely to equalize counts.

Forward owner = SHA-256(campaign_key) modulo 4. The same campaign_key always goes to the same lane.

## 3. QA-built dispatch snapshot

Only QA/canonical runs the full v3 graph and campaign builder.

After a full v3 rebuild:

```
python scripts/issue180/build_parallel_campaigns_v2.py
python scripts/issue180/refresh_dispatch_snapshot_v2.py --write-tracked
```

Generated build artifacts remain:
- `artifacts/issue180-v3/parallel_authority_campaigns_v2.csv`
- `artifacts/issue180-v3/parallel_terminal_candidates_v2.csv`

QA publishes the current tracked dispatch:
- `docs/issue180/parallel/dispatch/CURRENT_DISPATCH_V2.csv`
- `docs/issue180/parallel/dispatch/fwd-0.csv`
- `docs/issue180/parallel/dispatch/fwd-1.csv`
- `docs/issue180/parallel/dispatch/fwd-2.csv`
- `docs/issue180/parallel/dispatch/fwd-3.csv`

Forward workers read only their current lane file from **origin/canonical**. They do not run full v3 or rebuild campaigns.

The dispatch is a research lead, not authority and not a lock. A campaign may disappear or shrink after integration; already checked positive evidence does not become invalid merely because the dispatch changed.

## 4. Positive evidence is not globally SHA-bound

This is the central v2 rule.

A checked external source and an exact relation it proves do not become invalid merely because another lane advanced canonical.

Therefore Forward AUTHORITY_BATCH proposals are **not bound to one canonical HEAD or one Research Unit fingerprint**.

QA evaluates every proposed relation against the current canonical graph when integrating it:

- already present -> deduplicate;
- still applicable and uniquely supported -> accept;
- now resolved by the same relation -> record as duplicate/covered;
- now conflicting with a distinct validated root -> reject or route to conflict review;
- no longer relevant -> reject as obsolete without invalidating the rest of the source batch.

Do not make a worker redo web research solely because canonical advanced.

## 5. Terminal conclusions remain fingerprint-bound

A claim such as `NO_SAFE_EVIDENCE` or `PARTIALLY_RESOLVED` describes an exact residual population, so it can become stale.

Every Forward TERMINAL_BATCH item must include:
- current `unit_id`;
- exact `member_ids_sha256`;
- terminal status;
- grounded review provenance.

QA accepts a terminal conclusion only if the exact current unit fingerprint still matches. Otherwise the conclusion is obsolete and the regenerated remainder is reviewed separately.

For campaigns that are intentionally smaller than their source Research Unit (especially structure-free `direct:<canonical_tag>` work), a worker must **not** fake a unit-level terminal review. Instead write a `RESEARCH_OUTCOME` batch recording that this campaign was checked and produced no safe positive relation. QA records that outcome as research accounting only with decision `ACCEPT_OUTCOME` and the exact campaign fingerprint. The scheduler then marks that campaign `EXHAUSTED_REVIEWED` and does not assign it again. If its target population changes, its fingerprint changes and it automatically reopens. When every current campaign covering an exact residual unit has been exhausted and the current unit fingerprint still matches, the scheduler lists the unit in `parallel_terminal_candidates_v2.csv`; QA may then create the canonical unit-level terminal review after normal v3 checks.

QA-owned deterministic/policy buckets remain:
- `SAFE_STRUCTURE_READY`
- `POLICY_BLOCKED`
- `IDENTITY_BLOCKED`
- `STRUCTURAL_NO_SAFE_PATH`
- `CONFLICT_REVIEW`

Forward does not terminalize those buckets.

## 6. One source = one authority batch

Forward writes append-only batch JSON under:
`docs/issue180/parallel/proposals-v2/fwd-N/`

Schema:
`docs/issue180/parallel/AUTHORITY_BATCH_SCHEMA_V2.md`

For a checked official/accepted page, collect all exact relations that page proves into **one AUTHORITY_BATCH**.

Do not emit one proposal per Character.

If the same source explicitly proves additional current Issue #180 Characters outside the original campaign, include those exact relations in the same source batch. This is deliberate source reuse. QA deduplicates against current canonical state.

Never infer unlisted members, aliases, variants or HOME from naming/co-occurrence alone.

## 7. Forward execution — append-only mailbox

Forward branches are research mailboxes, not canonical mirrors.

For each lane:

1. `git fetch origin --prune`;
2. do **not** merge/rebase canonical in routine research;
3. read `origin/research/issue180-single-home-pilot:docs/issue180/parallel/dispatch/fwd-N.csv`;
4. choose only `research_state=OPEN` rows for slot N;
5. use embedded accepted source hints before new web search;
6. follow `RESEARCH_STOP_PROTOCOL_V2.md`;
7. research highest reusable-yield campaigns first;
8. inspect the actual source page and exhaust all safe exact matches from that source;
9. write one source-level AUTHORITY_BATCH, or RESEARCH_OUTCOME when the bounded research routes are exhausted;
10. use TERMINAL_BATCH only after the exact whole current Research Unit was genuinely reviewed;
11. commit/push roughly 3–5 coherent source/outcome batches at a time;
12. refresh the canonical lane dispatch before selecting the next batch.

Forward never runs `run_issue180_v3.py`, never rebuilds the campaign queue, and never updates tracked dispatch/source-review/QA ledgers.

Canonical advancement does not force an in-progress source batch to be abandoned. Finish valid source research, push the mailbox batch, then refresh dispatch.

## 8. QA / Integrator execution

QA:

1. first bulk-process current QA-owned deterministic buckets;
2. run full v3 + campaign builder and refresh the tracked dispatch;
3. fetch all four Forward mailbox branches directly;
4. review each new source batch;
5. integrate accepted relations into existing canonical evidence/decision ledgers;
6. record decisions in `QA_REVIEW_LEDGER_V2.csv` and source-level reusable reviews in `SOURCE_REVIEW_LEDGER_V2.csv`;
7. reject duplicate/obsolete/conflicting relations individually rather than discarding an entire good source batch;
8. validate TERMINAL_BATCH only against exact current unit fingerprint;
9. accept a current RESEARCH_OUTCOME with QA decision `ACCEPT_OUTCOME`, preserving campaign_key + campaign_fingerprint; never turn one campaign-level negative into a unit terminal by itself;
10. rebuild v3/campaigns and refresh tracked dispatch so accepted exact outcomes become `EXHAUSTED_REVIEWED` and are not researched again;
11. use `parallel_terminal_candidates_v2.csv` to find exact current units whose campaigns are all exhausted; only after confirming no admissible path remains may QA create the canonical unit-level terminal review;
12. rebuild v3 when accepted family/member/variant evidence can reshape the graph;
13. direct-HOME-only source batches may be accumulated into a coherent wave before one full rebuild;
14. push QA, require full-v3 CI green, then fast-forward the exact green QA HEAD to canonical;
15. repeat until OPEN/PENDING = 0.

There is no fixed "50 proposals / 250 members" epoch rule. Natural source/graph boundaries decide integration waves.

## 9. Source-review reuse and QA depth

`SOURCE_REVIEW_LEDGER_V2.csv` is QA-only. It stores approved source identity/scope/mapping rules.

If a later batch uses the same accepted source for the same mapping rule:
- Forward still checks the exact member/Character is explicitly covered;
- QA may reuse the source-level approval instead of re-proving source identity/scope;
- ambiguous names, aliases, variants, changed claims, conflicting roots or changed mapping rules still receive 100% semantic review.

Always 100% review:
- source identity and actual page content;
- what the source claim proves;
- family/root authority;
- variant/base identity;
- conflicts;
- manual/ambiguous mappings;
- terminal conclusions;
- migration corrections.

For deterministic exact-name extraction from one already-approved roster/mapping rule, QA may second-review a sample (10%, min 10, max 50). Any mismatch escalates that entire batch to 100% row review.

Machine validation remains 100%.

## 10. CI and write ownership

Forward CI is lightweight:
- research-only scope;
- v2 scheduler/dispatch tests;
- branch write scope;
- campaign-key lane ownership;
- batch schema;
- protected-source boundaries.

Forward CI does not require latest canonical to be an ancestor and does not run full 35,890-row v3 on each proposal push.

QA/canonical CI runs:
- all Issue180 tests;
- full v3 resolver/validator/reproducibility;
- v2 campaign rebuild;
- tracked dispatch freshness check;
- source-review-ledger validation;
- #179 freshness;
- protected-source checks.

Forward never writes canonical evidence/decision/terminal-review ledgers. QA never edits Forward proposal files. No force push.

## 11. Legacy single-worktree freeze

The old single-Worktree executor remains retired. GitHub-backed research through `3004402b39e48f900ce17cb5d511dc3975f0003c` is preserved.

If the old Codex session contains local-only work from before its usage-limit stop, perform salvage only under `LEGACY_SINGLE_WORKTREE_HANDOFF_V1.md`. Do not resume old closure-sweep research.

## 12. True blockers and final gate

Return early only for:
- HOME semantic redefinition;
- protected #70/#179/#132 mutation;
- main merge / production apply;
- a genuine competing-root policy question that cannot safely remain unresolved;
- unexplained accepted-evidence corruption/loss.

Missing evidence, inaccessible pages, duplicate batches, regenerated campaigns, routine CI repair and safe unresolved outcomes are not blockers.

Finish when OPEN/PENDING = 0, all unresolved rows have concrete reasons, migration is accounted, conflicts/missing roots are safe, #179 freshness passes, full canonical v3 CI is green, and protected sources/main/production remain untouched.
