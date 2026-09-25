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

- `family:<key>` — prove a stable family/work HOME once, then named membership separately as needed;
- `roster:<key>` — inspect one official/accepted roster and extract all exact covered current Characters;
- `base:<character>` — validate variant/base identity once and reuse the confirmed base HOME;
- other non-ungrouped subjects remain one stable campaign;
- only genuinely structure-free direct long-tail work falls back to `direct:<canonical_tag>`.

Do **not** split one reusable family/roster/base authority across lanes merely to equalize counts.

Forward owner = SHA-256(campaign_key) modulo 4. The same campaign_key always goes to the same lane.

## 3. Campaign queue

After a full v3 rebuild, run:

```
python scripts/issue180/build_parallel_campaigns_v2.py
```

Generated queue:
`artifacts/issue180-v3/parallel_authority_campaigns_v2.csv`

The queue is a **research lead**, not authority and not a lock.

A campaign may disappear or shrink after another accepted batch changes the graph. That does not invalidate authority already checked from a real source.

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

## 7. Forward execution

For each lane:

1. fetch current canonical before selecting new work;
2. rebuild v3 + authority campaigns when starting a new queue wave;
3. choose only campaign keys owned by that lane;
4. research highest reusable-yield campaigns first;
5. inspect the actual source page;
6. exhaust safe exact matches from that source before moving on;
7. write one source-level AUTHORITY_BATCH;
8. use TERMINAL_BATCH only after the exact residual fingerprint has genuinely been reviewed;
9. commit/push coarse source batches;
10. continue with another owned campaign.

A canonical advance does not force an in-progress source batch to be abandoned. Refresh the campaign queue before choosing the next campaign, not in the middle of a valid source review.

## 8. QA / Integrator execution

QA:

1. first bulk-process current QA-owned deterministic buckets;
2. rebuild v3 + campaign queue;
3. fetch all four Forward branches directly;
4. review each new source batch;
5. integrate accepted relations into existing canonical evidence/decision ledgers;
6. record decisions in `QA_REVIEW_LEDGER_V2.csv`;
7. reject duplicate/obsolete/conflicting relations individually rather than discarding an entire good source batch;
8. validate TERMINAL_BATCH only against exact current unit fingerprint;
9. rebuild v3 when accepted family/member/variant evidence can reshape the graph;
10. direct-HOME-only source batches may be accumulated into a coherent wave before one full rebuild;
11. push QA, require full-v3 CI green, then fast-forward the exact green QA HEAD to canonical;
12. repeat until OPEN/PENDING = 0.

There is no fixed "50 proposals / 250 members" epoch rule. Natural source/graph boundaries decide integration waves.

## 9. QA depth

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
- v2 scheduler tests;
- branch write scope;
- campaign-key lane ownership;
- batch schema;
- protected-source boundaries.

Forward CI does not require latest canonical to be an ancestor and does not run full 35,890-row v3 on each proposal push.

QA/canonical CI runs:
- all Issue180 tests;
- full v3 resolver/validator/reproducibility;
- v2 campaign rebuild;
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
