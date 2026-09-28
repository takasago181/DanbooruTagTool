# Issue #180 Serial Completion v1

Status: ACTIVE serial execution contract
Branch: `research/issue180-serial-completion`
Canonical authority branch: `research/issue180-single-home-pilot`
Target: Character -> HOME_COPYRIGHT (0..1)

This contract changes execution scheduling only. It does not change HOME semantics, evidence quality, v3 resolver behavior, migration authority, #179 identity ownership, protected-source boundaries, or final completion gates.

## 1. Why serial mode exists

The previous 4 Forward + 1 QA model produced research faster than QA could integrate it. At activation, the latest QA checkpoint reported 993 unreviewed proposals / 3,710 relation instances across the four Forward mailboxes.

Serial mode therefore optimizes the current bottleneck:

1. drain existing QA backlog first;
2. then continue research and review in one managed Worktree;
3. preserve separate research and review passes;
4. batch expensive full-v3/CI work at natural semantic boundaries instead of after tiny waves.

The old Forward 0..3 and QA worktrees are paused. Their branches remain immutable evidence/mailboxes and must not be deleted or rewritten.

## 2. One Worktree, two explicit passes

The serial worker has one fixed execution lane but must keep two cognitive passes separate.

### Research pass

- discover/check allowed authority;
- create a candidate relation set;
- do not treat the candidate as accepted merely because the research pass produced it;
- record exact source URL, source claim, authority class, exact covered Character/member names, proposed relation type/root, and uncertainty notes.

### Review pass

Before canonical integration:

- re-open the actual source;
- independently re-check source identity and claim scope;
- re-check exact member/Character coverage;
- compare against the current canonical graph;
- accept/dedupe/reject/conflict each relation under the existing Issue #180 rules;
- do not rely on the research-pass conclusion alone.

This is not equivalent to a second human/agent, but it preserves a real second evidence pass while removing inter-Worktree queueing.

Always 100% review:
- new source identity/scope;
- family/root authority;
- variant/base identity;
- aliases/manual mappings;
- conflicts;
- terminal conclusions;
- migration corrections.

For deterministic exact-name extraction from an already ACCEPTED SOURCE_REVIEW_LEDGER_V2 source/mapping rule, the existing sampling rule remains allowed: 10%, min 10, max 50. Any mismatch escalates the whole batch to 100% row review.

## 3. Phase A — QA backlog drain first

Do not start new web research while any already-persisted Forward proposal remains unreviewed, except when one exact source must be opened to perform QA review.

Source mailboxes:
- research/issue180-forward-0
- research/issue180-forward-1
- research/issue180-forward-2
- research/issue180-forward-3

Determine unreviewed proposals by proposal_id against the current QA_REVIEW_LEDGER_V2.csv. Do not trust the activation snapshot after work begins; refetch live branches and ledger state.

Process backlog in coherent source/semantic waves.

Preferred wave size:
- roughly 50–100 proposals, or
- roughly 300–600 relation instances,
whichever reaches a natural semantic boundary first.

Smaller waves are allowed only when:
- accepted FAMILY_HOME / MEMBER_OF / VARIANT_OF evidence can reshape many residual units;
- a conflict needs immediate graph rebuild;
- a technical repair requires validation before more semantic changes;
- backlog remainder is smaller.

Do not run full-v3 for every 3–10 ordinary direct-HOME proposals.

## 4. Cheap checks inside a wave

During a wave, use cheap/local checks as appropriate:
- JSON/CSV parse-back;
- git diff --check;
- exact schema checks;
- targeted Issue180 unit tests relevant to touched structures;
- source-review ledger consistency;
- duplicate proposal_id / qa_id checks.

Do not repeatedly rebuild the full 35,890-row graph when the current sub-batch only adds straightforward DIRECT_HOME rows and no graph-shaping relation.

## 5. Full integration boundary

At the end of each coherent wave:

1. integrate accepted evidence/decisions;
2. update QA_REVIEW_LEDGER_V2.csv;
3. update SOURCE_REVIEW_LEDGER_V2.csv where source-level approval/reuse changed;
4. run full v3;
5. rebuild authority campaigns;
6. refresh tracked dispatch;
7. run all required Issue180 tests/validators;
8. verify #179 freshness;
9. verify protected-source boundaries;
10. verify reproducibility;
11. commit the exact integration wave;
12. push serial branch;
13. manually dispatch the Issue180 full-v3 workflow for this serial ref;
14. wait/poll until the exact commit is green;
15. only then fast-forward `research/issue180-single-home-pilot` to that exact green commit with no force push;
16. continue automatically.

A failed CI is a repair task, not a user stop, unless it reveals a true policy/protected-data blocker.

## 6. CI policy for serial mode

Routine pushes to `research/issue180-serial-completion` must NOT automatically run full-v3.

The Issue180 workflow supports manual `workflow_dispatch` on this branch. Use that only for integration boundaries.

This preserves durability via ordinary commits/pushes without paying ~6–8 minutes of full CI after tiny checkpoints.

Never promote a serial commit to canonical unless the exact commit received the required green full-v3 workflow result.

## 7. Phase B — serial research after backlog reaches zero

Once all persisted Forward proposals are reviewed/accounted:

1. rebuild v3/campaigns/dispatch from the latest canonical state;
2. select the highest reusable-yield OPEN campaign across all four scheduler slots;
3. prefer untouched OPEN before OPEN_WITH_PROGRESS;
4. honor prior_checked_routes and never repeat them;
5. reuse ACCEPTED SOURCE_REVIEW_LEDGER_V2 sources before new search;
6. follow RESEARCH_STOP_PROTOCOL_V2 route budgets;
7. one checked source should yield all exact safe relations it proves;
8. perform the explicit Review pass before integration;
9. accumulate ordinary direct-HOME work into coherent waves;
10. trigger full-v3/CI only at the integration boundary described above.

The slot hash remains useful for scheduler stability/accounting, but serial mode is not four parallel workers. One Worktree may process campaigns from any slot in scheduler-priority order.

## 8. Research outcomes

PARTIAL:
- record checked routes;
- keep campaign open as OPEN_WITH_PROGRESS;
- carry prior_checked_routes forward;
- do not infer negative HOME evidence;
- do not repeat those routes later.

EXHAUSTIVE:
- only when exact campaign scope is genuinely bounded/exhausted;
- must receive the explicit Review pass;
- only then may ACCEPT_OUTCOME / EXHAUSTED_REVIEWED be recorded.

Terminalization remains exact Research Unit fingerprint-bound. Do not close a large franchise because a few routes failed.

## 9. Stop rules

Do NOT stop for:
- ordinary PARTIAL;
- inaccessible pages after route budget;
- duplicates;
- stale proposals;
- stale dispatch that can be rebuilt;
- safe unresolved outcomes;
- normal serializer/schema repairs;
- normal CI/test repair;
- one campaign exhausting its routes;
- packet exhaustion.

Stop/report to the user only for:
- HOME semantic redefinition;
- required protected #70/#179/#132 mutation;
- main merge / production apply request;
- a genuine competing-root policy question that cannot safely remain unresolved;
- accepted-evidence corruption/loss that cannot be reconstructed;
- persistent inability to write/push/validate;
- final Issue #180 completion.

## 10. Final gate

Do not report complete until:
- Character population = 35,890;
- every Character has exactly one final state;
- OPEN/PENDING Research Unit = 0;
- unresolved rows have concrete reasons;
- migration differences are fully accounted;
- multi-home conflicts are resolved or explicitly safely unresolved;
- missing roots = 0;
- #179 freshness PASS;
- full v3 validation PASS;
- reproducibility PASS;
- required exact-SHA CI green;
- main / production / #70 / #179 / #132 protected sources untouched.

Do not merge to main or production-apply.

## 11. #188 telemetry

Each real serial run records the existing last_run_metrics fields in the normal Issue #180 checkpoint comment. Do not create telemetry-only commits. Unknown/unobservable values are null, never guessed.

Serial-mode useful fields additionally include:
- backlog_proposals_before / after;
- backlog_relations_before / after;
- proposals_reviewed;
- relations accepted / duplicate / rejected;
- full_v3_runs;
- CI runs;
- stop_reason.

The first serial activation snapshot is historical only; live GitHub always wins.

## 12. User-directed Phase B revision — deterministic closeout

Effective 2026-09-28. This section supersedes the Phase B instruction in §7 to process every OPEN campaign through web research. It changes scheduling and closeout only; HOME semantics, evidence standards, source authority, migration rules, and protected boundaries do not change. Preserve all existing Forward mailboxes, QA/source ledgers, v3 evidence, and migration provenance. Do not roll back, repeat completed research, or rebuild prior results from scratch.

The objective is to assign one HOME only when existing evidence safely proves it. Otherwise, finish the Character in the existing `HOME_UNRESOLVED` state with a concrete reason. Maximizing `HOME_CONFIRMED` is not an objective; reaching zero OPEN/PENDING is.

### 12.1 Phase A remains first

Drain every persisted unreviewed proposal from Forward 0..3 by `proposal_id` against the live current QA ledger before any new campaign research. Do not discard or re-research Forward work. Keep separate research and review passes, reopen/recheck sources, verify exact Character/member coverage and canonical applicability, and apply the existing 100% review and deterministic sampling rules. Use the source/semantic wave sizing and CI batching in §§3–6.

### 12.2 One-time deterministic Phase B classification

After backlog reaches zero, run the current full v3 pipeline once, then deterministically classify every current OPEN Research Unit and campaign exactly once from that v3 snapshot into these operational lanes. These are scheduling labels only, not new semantic statuses:

1. **AUTO_SAFE** — Existing Issue #180 evidence policy already proves exactly one HOME without new web research. Eligible evidence includes a terminal Copyright qualifier resolved through an already reviewed unique root normalization; an exact safe structural variant whose exact base exists and is HOME_CONFIRMED; exact member coverage plus HOME proved by already ACCEPTED source/evidence ledger entries; and the current `SAFE_STRUCTURE_READY` equivalent. Never use name similarity, RelatedCopyright, post co-occurrence, search-result proximity, or string similarity as authority.
2. **HIGH_YIELD_RESEARCH** — Only cases with a concrete high-yield route: one permitted official/authorized roster, character, or cast source likely to resolve multiple current Characters (normally five or more); a reusable ACCEPTED source family/scope with exact additional members; a concrete official source hint already present in dispatch; or a migration residual/validated conflict that must be resolved for the final gate. Candidate roots or RelatedCopyright alone are not a reason to include an item. New web research is allowed only in this lane.
3. **FINAL_UNRESOLVED** — Every remaining OPEN item. Deterministically inspect current v3 structures, evidence and candidate graph, #179 origin handoff, and ACCEPTED source ledger. If there is no validated direct HOME, safe family HOME plus membership path, safe exact base/variant path, approved reusable authority, high-yield route, or competing validated HOME conflict, and policy forbids guessing, close it through the existing exact-fingerprint terminal review mechanism using the correct existing reason (`NO_SAFE_EVIDENCE`, `PARTIALLY_RESOLVED`, `POLICY_BLOCKED`, `IDENTITY_BLOCKED`, or another already-defined reason). `FINAL_UNRESOLVED` is never written as a semantic status.

Keep each Research Unit's exact fingerprint and `member_ids_sha256` binding. Do not use terminal review to conceal a validated conflict, skip identity review, or turn missing evidence into HOME_CONFIRMED. Unresolved is a normal final result and must carry a concrete reason and evidence/review path.

### 12.3 Revised Phase B order and boundaries

After Phase A:

1. Bulk-process all AUTO_SAFE items under the unchanged evidence policy.
2. Process HIGH_YIELD_RESEARCH in reusable-source waves. Reopen each source, collect all exact safe current relations that source proves in one pass, obey `RESEARCH_STOP_PROTOCOL_V2` route budgets, and do not repeat equivalent searches.
3. Once the high-yield lane is complete, perform one deterministic bulk terminal sweep of FINAL_UNRESOLVED. Do not web-search these items individually or reopen research after the sweep starts.
4. At the natural AUTO_SAFE, high-yield wave, and FINAL_UNRESOLVED boundaries only, run full v3, rebuild campaigns, refresh tracked dispatch, run required Issue180 tests/validators, verify source ledger, #179 freshness, protected-source boundaries, and reproducibility. Then use the exact-commit CI and no-force fast-forward promotion process in §§5–6.
5. Confirm the final gate in §10 from the resulting current state.

Small checkpoints inside a wave continue to use cheap validation. Routine serial pushes do not start full-v3 automatically. A failed CI, stale dispatch, duplicate, safe unresolved result, or ordinary serializer/schema repair remains an autonomous repair-and-continue task.
