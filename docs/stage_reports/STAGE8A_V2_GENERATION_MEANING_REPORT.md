# Stage 8A v2 generation meaning report

## Result

Implemented Stage 8A v2 as a display-only semantic decorator around the fixed
Stage 6/7B Recommendation result. The formal package was reviewed against the
current implementation before editing; it required no Stage 0–7B behavior
change.

The final audit found that a single selected rule allowed statistical context
to replace the semantic-role generation explanation. The decorator now emits
two independent outputs: `generation_hint` for generation use and additive
`evidence_notes` for SAME_STAT, rare, and low-support context.

The three common-only `INDIRECT_SUPPORT` rules for BODY_PART,
STATE_REACTION, and APPEARANCE_CLOTHING were removed. Common membership alone
does not establish weak direct contribution, so these roles now retain their
normal semantic explanation unless future reviewed individual evidence says
otherwise.

## Changed and added files

- Added `data/semantic/recommendation_semantic_labels.csv` with 34 reviewed
  canonical labels.
- Added `data/semantic/recommendation_generation_hints.csv`; the final audited
  production set contains 12 rules after removing the three unsupported
  common-only `INDIRECT_SUPPORT` rules.
- Added `danbooru_tag_tool/stage8a_semantics.py` for strict loading,
  deterministic decoration, SAME_STAT relation detection, and hint selection.
- Updated `danbooru_tag_tool/ui.py` to render category, unmodified statistics,
  and the generation-reading hint in three lines.
- Added `tests/test_stage8a_semantics.py`, `tools/stage8a_verify.py`, and
  `tools/stage8a_real_tk_smoke.py`.
- Added Stage 8A schema, decision, benchmark evidence, report, and real Tk
  screenshot.

## Seed distribution

| Semantic role | Count |
|---|---:|
| ACTION_SUPPORT | 4 |
| APPEARANCE_CLOTHING | 1 |
| BODY_PART | 5 |
| CAMERA_COMPOSITION | 5 |
| IMPLEMENT | 5 |
| POSE | 4 |
| SITUATION_RELATION | 1 |
| STATE_REACTION | 6 |
| SUBJECT_BASIC | 3 |
| **Total** | **34** |

The production rule count is 12: nine semantic-role generation defaults and
three statistical/relation context rules.

## Validation

- Stage 8A targeted pytest: `12 passed in 0.05s`.
- Stage 7A/7B related pytest: `28 passed in 3.12s`.
- Final full regression: `153 passed in 23.44s`.
- Production parity for `anal AND butt_plug`: base_count `3735`, Stage 6
  candidates `5918`; decorated common/rare lists retained identical order,
  count, candidate objects, base_count, co_count, Conditional Rate, Raw Lift,
  Wilson lower bound, and shrunk Lift.
- All 5,889 unclassified candidates and 2,592 low-support candidates remained
  present. `1girl`, `solo`, `nude`, and `sex_toy` remained present when supplied
  by Stage 6.
- Separation checks passed: common BODY_PART retains `BODY_TARGET`; a rare
  classified candidate retains its semantic generation hint and receives a
  separate discovery context note; SAME_STAT retains both its semantic hint
  and its relation/bucket notes.
- Stage 6 Recommendation source and Stage 7B async source match the prior
  Stage 7B FINAL handoff byte-for-byte. The A→D coalescing regression remains
  green in the Stage 7B tests.
- Two consecutive Stage 8A evidence builds produced identical bytes:
  `metric_parity.json` SHA-256
  `36c0d72744d524389d14f8b43f1f12cce81c1ce88a47f7696f3090016a748315`;
  `protected_hashes.json` SHA-256
  `0834cff783477cf82506f04f14eab8d2861fb91b9e232c5dcc803140f9a62994`.
- Production Tk smoke passed at 900x540, 1120x760, and maximized. It verified
  visible meaning labels, generation hints, both Recommendation buckets,
  base_count, Manual Auxiliary add/added state, Prompt preview, visible copy,
  matching clipboard, and a responsive UI thread.
- Real Tk screenshot:
  `docs/stage_reports/STAGE8A_V2_REAL_TK_SCREENSHOT.png` (SHA-256
  `39649b5b0b361f3b1a865797f18e3cca2591981feebf70a00e6ca2bc55092d3a`).
- Special2788 SHA-256 remained
  `07584b365d5a68dbadd3f5e80859e768c2718b18746e32de02ce4b8bd60935e3`.

## Preserved boundaries

Stage 6 mathematics and role data, Stage 7B ranks, candidate totals, async
behavior, Stage 4 search, Stage 5 index, Japanese Overlay, Special/Alias/
Semantic identity, partial-AND prohibition, Manual Auxiliary behavior, Prompt
order, and offline runtime are unchanged. No content filter or penalty,
automatic add/delete/weight, Prompt rewrite, score fusion, LLM, or runtime
network path was added.

## Backup and unresolved items

Pre-change files and the prior handoff ZIP are under
`backups/stage8a_v2_pre_20260906_`. The expanded formal package is retained at
`backups/stage8a_v2_spec_package_20260906`.

No unresolved Stage 8A v2 item remains. Stage 8B, Stage 9, and Stage 10 were
not started.
