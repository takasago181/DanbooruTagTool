# Issue132 Runtime Repair Card V7 — invalid-only repair

Status: ACTIVE when selected by RUNTIME_AUTHORITY.json.

## Purpose

Repair only output that is not currently acceptable under the flat Pass-A validator.

Repair is not a promotion pipeline and is not a second Worker.

## Ownership

Repair owns:
- invalid historical staging windows;
- windows with genuine operational holds;
- append-only repair overlays for exactly those windows.

Repair does not:
- promote staging to checkpoints;
- edit historical source files;
- rereview valid windows;
- chase a contiguous prefix;
- perform general forward classification;
- change main/production/UserData/#64/#76/#118.

## Target selection

Read:
1. RUNTIME_AUTHORITY.json
2. this card
3. Worker V9 semantic rules
4. latest applicable flat-validator snapshot

Choose the oldest actionable invalid or hold window across all lanes.
A later valid window remains valid and needs no action.

For one target:
- fetch only its source window;
- fetch only the authoritative neutral shard(s) needed for that exact range;
- preserve already valid decisions when safely bound;
- fix only actual structural/semantic defects;
- research only unresolved identities that materially need it;
- completed bounded research still uncertain => SEMANTIC_UNRESOLVED;
- genuine unavailable research/tool access may remain a hold.

Persist one append-only overlay for the exact source range using the existing repair-overlay model.
Do not overwrite the source.

If budget remains, process another independent invalid/hold target.
One target failure does not block another target.

## Validation

Before writing an overlay, require exact parity with current compact semantic validation:
- slot/review_seq/identity hash binding;
- exact field sets;
- full range coverage exactly once;
- allowed frozen codes;
- route/local consistency;
- mode constraints;
- researched evidence constraints;
- hold constraints.

## Progress

Repair success is measured only by the next flat-validator snapshot accepting that effective window.

No checkpoint count, prefix advancement, or promotion is part of Repair progress.

## Report

Report only:
overlays created, windows repaired pending validation, remaining invalid windows, remaining hold windows, exact blocker.
