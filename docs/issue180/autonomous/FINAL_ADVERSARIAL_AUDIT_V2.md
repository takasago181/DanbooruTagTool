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
   - sushiro (regression example: sangonomiya_kokomi_(sushiro))
   - futaba_channel (community/imageboard qualifier; regression example: daiginjou_(futaba_channel))

2. umbrella/company/platform qualifier mistaken for canonical Character HOME
   - project_moon
   - vocaloid
   - nintendo / namco / capcom / cygames / type-moon / fromsoftware
   - snk / arika / alicesoft
   - cevio / utau / synthesizer_v / voiceroid / voicevox / voicepeak / coefont
   - a.i._voice / gynoid_talk / talkex / voisona
   - adaptation root exception: blue_archive_the_animation -> blue_archive

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

8. newly unlocked variant patterns being missed by a static freeze-time registry
   - 1,691 baseline variant rows had an existing base Character but no confirmed base HOME
   - every recompile now rebuilds dynamic ready patterns from the current HOME graph
   - dynamic pattern IDs include membership count + hash, so later-added members invalidate the earlier pattern review
   - final readiness therefore catches large variant groups unlocked or enlarged by later family/direct decisions

9. reviewed unresolved work re-entering active queues
   - terminal reviewed family/Character/group/pattern results are separated from active work

10. no-op / low-effort autonomous completion
   - final readiness requires meaningful decision work and exhaustion/review of mandatory lanes
   - terminal UNRESOLVED / NEEDS_HIGHER_REASONING requires grounded evidence plus substantive notes
   - weak legacy rows may be evidence-backed deferred after real review instead of being forced into a guessed HOME

11. autonomous gate weakening
   - after execution freeze, final write-scope allows decision shard CSV changes only

12. stale Issue #179 dependency
   - the autonomous run uses a frozen #179 handoff snapshot
   - live #179 changes are reported
   - live freshness is mandatory again before later user freeze/promotion

13. future Issue #179 confirmed non-official rows
   - they are removed from the HOME foundation and deterministically become NOT_OFFICIAL_CHARACTER
   - Luna itself cannot create NOT_OFFICIAL_CHARACTER

## Evidence policy

Old RelatedCopyright, post co-occurrence, name similarity and search overlap are discovery hints only.

Autonomous PASS and terminal reviewed deferrals require grounded evidence and scoped authority. Internal `REPO:` authority is allow-listed to the dedicated Issue #180 evidence directory and policy files. Generated artifacts/work queues/masters/review outputs and autonomous decision files cannot serve as authority, including through this repository's GitHub/raw/API URLs; this prevents old relation/co-occurrence candidates from becoming circular proof. Approved evidence CSVs are additionally key/HOME-bound so one legitimate evidence file cannot be reused for an unrelated decision.

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

## Evidence-scope hardening

The final audit also closed two internal-evidence escalation paths:

- a source-registry or Character row with the same `home_copyright` cannot be promoted into FAMILY_QUALIFIER authority unless the evidence row explicitly names the same family;
- base Character evidence cannot prove VARIANT_CHARACTER officiality unless the evidence explicitly names the variant Character itself.

`AUTHORITY_POLICY_V1.md` is methodology, not row-level factual evidence, and is excluded from the decision-evidence allow-list. Generated artifacts/review outputs remain discovery/context only.

Character-specific HOME holds are terminal review states, not PASS authority. A grounded Character terminal review suppresses all HOME inheritance paths for that Character without asserting NOT_OFFICIAL.

## Human review auditability

The 35,890-row user review exposes:
- HOME/final state
- #179 origin/officiality context
- authority type/provenance for confirmed HOME
- unresolved reason
- evidence-backed review context for terminal family, direct Character, discovery-group and variant-pattern reviews

A group/pattern review never creates HOME merely by appearing as review context.

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
