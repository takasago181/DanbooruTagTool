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
