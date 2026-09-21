# Issue #180 Autonomous Harness — Final Adversarial Audit v2

Status: RESEARCH HARNESS CANDIDATE / NO MAIN MERGE / NO PRODUCTION APPLY

This checkpoint documents the final pre-freeze design of the autonomous Character -> HOME Copyright audit.

## Goal

Compile all 35,890 Character rows into exactly one terminal state:

- HOME_CONFIRMED
- HOME_UNRESOLVED
- NOT_OFFICIAL_CHARACTER

HOME is 0..1. Wrong HOME is worse than unresolved.

## Adversarial findings fixed

The audit reproduced and fixed the following failure classes:

1. collaboration/project qualifier mistaken for HOME
   - project_voltage
   - marvel_vs._capcom

2. umbrella/company/platform qualifier mistaken for canonical Character HOME
   - project_moon
   - vocaloid
   - nintendo / namco / capcom / cygames / type-moon / fromsoftware
   - cevio / utau / synthesizer_v / voiceroid / voicevox / voicepeak / coefont
   - a.i._voice / gynoid_talk / talkex / voisona

3. known Issue #179 UNKNOWN identity receiving HOME only because its qualifier family was accepted
   - regression example: harmony_(pokemon)

4. weak current-master provenance being silently preserved
   - 14 rows requeued; only rows independently recovered by stronger family/direct evidence are allowed to reconfirm

5. legacy broad direct authority bypassing broad-family review
   - broad v1 rows are requeued and cannot autonomous FAMILY_QUALIFIER PASS

6. nested variant base selection using the wrong base
   - name_(variant)_(ip) can resolve to name_(ip)
   - conflicting base HOMEs fail closed

7. direct-vs-variant authority overwrite
   - different HOME => conflict
   - same HOME => corroboration; preserve direct provenance

8. reviewed unresolved work re-entering active queues
   - terminal reviewed family/Character/group/pattern results are separated from active work

9. no-op autonomous completion
   - final readiness requires meaningful decision work and exhaustion/review of mandatory lanes

10. autonomous gate weakening
   - after execution freeze, final write-scope allows decision shard CSV changes only

11. stale Issue #179 dependency
   - the autonomous run uses a frozen #179 handoff snapshot
   - live #179 changes are reported
   - live freshness is mandatory again before later user freeze/promotion

12. future Issue #179 confirmed non-official rows
   - they are removed from the HOME foundation and deterministically become NOT_OFFICIAL_CHARACTER
   - Luna itself cannot create NOT_OFFICIAL_CHARACTER

## Evidence policy

Old RelatedCopyright, post co-occurrence, name similarity and search overlap are discovery hints only.

Autonomous PASS requires grounded evidence and scoped authority.

Broad/umbrella families cannot receive autonomous FAMILY_QUALIFIER PASS.

Review-only scopes:
- DISCOVERY_GROUP
- VARIANT_PATTERN

These record completed research but never create HOME directly.

## One-pass efficiency

The run is deliberately group-first:

- mandatory high-yield unqualified discovery groups are roster-reviewed once;
- explicit DIRECT_CHARACTER decisions are written only for proven members;
- high-yield variant patterns are reviewed once and explicit VARIANT_CHARACTER decisions are written for covered variants;
- normalized/root-policy family mappings are reviewed once per family;
- long-tail unresolved rows do not require one web search each.

## Completion semantics

Autonomous completion does not mean every Character gets HOME.

It means:
- safe authority has been exploited;
- mandatory high-yield/safety lanes are reviewed or explicitly deferred;
- every one of 35,890 rows has a deterministic terminal state/reason;
- conflicts do not silently select a winner;
- full human review artifact is generated.

## Freeze rule

After the execution marker is created, Codex may modify only decision shard CSVs under:

docs/issue180/autonomous/decisions/*.csv

The base decision CSV is protected. Compiler, validators, policy, workflow, runbook and compatibility ledger are frozen.

A genuine harness defect discovered after freeze must be reported, not patched by the autonomous run.

## Promotion boundary

This checkpoint authorizes no:
- main merge
- production apply
- accepted Issue #70 source mutation
- #179 branch write
- Artist mutation

User review of all 35,890 rows remains mandatory before later freeze/promotion.
