# Stage 8B Support Knowledge Pilot report

## Result

Implemented the Stage 8B Pilot as an offline, explicit-only Support Knowledge
Layer. The UI now has a third `意味から補助` tab beside the two fixed statistical
tabs. It shows support slot, support class, canonical/display term, Japanese
reason, and combination context without fake statistics. A candidate changes
the Prompt only after the user presses `＋追加`, through existing Manual
Auxiliary behavior.

The final relation audit found that canonical deduplication selected one row as
representative metadata. `SemanticSupportCandidate` now retains every selected
Special relation in `relations`. The UI still shows one canonical candidate,
then renders each owner Special's slot, class, reason, and combination separately.
Relation ordering is deterministic and independent of Special selection order.

## Pilot coverage

| ID | Special | Kind | Production family | Candidate canonicals |
|---:|---|---|---|---|
| 161 | anal training | Primary | SEMANTIC_SUPPORT | anus, anal_object_insertion, gaping, large_insertion |
| 416 | bdsm | Primary | CONTEXT_MODIFIER | bondage, restraints, blindfold, collar |
| 312 | sex machine | Primary | MACHINE_STRUCTURED | machine, sex_toy, dildo, vibrator, object_insertion |
| 325 | tentacle sex | Primary | NONHUMAN_INTERACTION | tentacles, sex, multiple_penetration |
| 173 | double penetration | Primary | INSERTION_STRUCTURED | object_insertion, multiple_penetration, anus, vaginal, spread_legs |
| 16 | cooperative footjob | Primary | MULTI_ACTOR_INTERACTION | footjob, feet, penis |
| 385 | cumdrip from penis | Primary | FLUID_STATE_ACTION | penis, cum, dripping |
| 488 | xray sex | Primary | SEMANTIC_SUPPORT | x-ray, cross-section, sex |
| 88 | masturbation | Control | SELF_ACTION | solo, sitting, on_back, kneeling |
| 122 | missionary | Control | POSE_COMPOSITION | on_back, lying, spread_legs, from_above, sex |

Production contains 39 enabled Special rows: 21 `CORE_SUPPORT` and 18
`OPTIONAL_VARIATION`. All 39 carry intent and combination metadata. The family
rule file contains zero production rows by design. Control candidates stay
within ordinary subject/pose/action context; no unrelated hard-direction
candidate was injected.

The package lists ID 416 as `RESTRAINT_ACTION`, while the fixed production
Generation Profile is `CONTEXT_MODIFIER`. The current reviewed production value
was retained. This is the only package-to-production family difference and is
recorded in the machine-readable audit.

## Files

- Added `data/semantic/semantic_support_profiles.csv` and
  `data/semantic/family_support_rules.csv`.
- Added `danbooru_tag_tool/stage8b_support.py`.
- Updated `danbooru_tag_tool/ui.py` only to load and display the third tab and
  route explicit button presses to Manual Auxiliary.
- Added `tests/test_stage8b_support.py`, `tools/stage8b_verify.py`, and
  `tools/stage8b_real_tk_smoke.py`.
- Added this report, the schema, decision, benchmark JSON, and four real Tk
  screenshots.

## Validation

- Stage 8B plus Stage 7A/7B/8A targeted regression: `65 passed in 3.74s`.
- Full regression: `178 passed in 24.39s`.
- Multi-Special tests retain both relations for `anus`, `object_insertion`,
  `on_back`, and `spread_legs`, including opposite class/combination values.
  Reversing selected-Special order returns identical aggregate metadata, and
  Manual Auxiliary receives the deduplicated canonical once.
- Stage 6 parity for `anal AND butt_plug`: base_count 3735 and 5,918
  candidates; common/rare order and all raw values remained identical.
- Stage 7B Recommendation and async source hashes match the prior FINAL; its
  latest-request-wins A→D regression remains green.
- Stage 8A retained all 5,918 decorated candidates, including 5,889
  unclassified and 2,592 low-support candidates; no filtering or reranking.
- Two consecutive Stage 8B audit builds were byte-identical:
  `pilot_audit.json` SHA-256
  `2a81dff01a146a18ee336b92f033eb33fc3577254f61bbbcd0d5e09d555dd1a3`;
  `protected_hashes.json` SHA-256
  `c995f270d11604197f19d74f0dc3d29b5160083ab942cc30cc1863c484a0f471`.
- Real Tk smoke passed for anal training at 900x540, sex machine at 1120x760,
  masturbation maximized, and `masturbation + missionary` at 1120x760. The
  multi-Special screenshot shows one `on_back` candidate with two relation
  blocks. Smoke checked the third tab, support slot/reason,
  no fake statistics, visible add controls, Manual Auxiliary addition, Prompt,
  clipboard, bounds, and a responsive UI thread.
- Special2788 SHA-256 remains
  `07584b365d5a68dbadd3f5e80859e768c2718b18746e32de02ce4b8bd60935e3`.
- Runtime external LLM, network, and API calls: zero.

## Self-audit and boundaries

Unknown/profileless ID 145 (`anal prolapse`) returns zero candidates; its tag
text does not trigger heuristic expansion. Loader errors cover unknown IDs or
canonicals, invalid enums, duplicates, incomplete enabled/alternative/model
observation rows, while disabled rows stay out of runtime. Synthetic tests cover
family union, Special override, canonical deduplication, and lossless relation
provenance.

Special2788 and other protected sources were not changed. Special/Alias/
Semantic identity, Stage 4 search, Stage 5 index, Stage 6 mathematics, Stage 7B
async behavior, Stage 8A meaning decoration, Prompt order, weights, and offline
operation remain fixed. No auto-add/delete, Prompt rewrite, severity-based
filter/penalty/boost, substring/regex inference, or automatic conflict
resolution was introduced.

No unresolved implementation failure remains. ID 416's documented package
family difference is retained for independent audit. Stage 8C and Stage 9 were
not started; FINAL is left to ChatGPT review.
