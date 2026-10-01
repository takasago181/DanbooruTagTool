# Provisional Browse HOME — fast bulk audit

Base: `d9ab6d0739b8e4ff6293a25c2a21c9eb4aad19d5`. Research branch: `codex/issue216-unresolved-coverage-7073`.

This is a pattern audit of the independent Browse overlay. **ACCEPT means suitable for the provisional Browse layer, not accepted formal HOME authority.** No #180/#216 decision, source registry, source member or production data was changed. The original provisional CSV remains unchanged.

## Results

| Metric | Count |
|---|---:|
| Original provisional assignments inspected | 7,011 |
| ACCEPT | 6,808 |
| CHANGE of existing assignment | 2 |
| REJECT of existing assignment | 201 |
| Added from the 3,091 previously unresolved rows | 448 |
| Total audited Browse assignments | 7,258 |
| Still unresolved, including rejected assignments | 2,844 |
| Top500 unresolved | 10 |
| Top2000 unresolved | 211 |

The output CSV uses CHANGE for both replacements and additions: **450 CHANGE = 2 replacements + 448 additions**. Its verdict counts are ACCEPT 6,808 / CHANGE 450 / REJECT 201 / UNRESOLVED 2,643. `still unresolved` includes REJECT plus UNRESOLVED. All 10,102 subjects are accounted exactly once.

| Original class | ACCEPT | CHANGE | REJECT | UNRESOLVED |
|---|---:|---:|---:|---:|
| HIGH 308 | 305 | 0 | 3 | 0 |
| MEDIUM 6,703 | 6,503 | 2 | 198 | 0 |
| Unresolved 3,091 | 0 | 448 | 0 | 2,643 |

## How the audit was performed

Reviewed the complete list of 1,950 proposed HOME groups and the associated reason patterns, with representative member surfaces for the 330 largest groups (4,519 original assignments), the HIGH groups, explicit risk groups and high-frequency changes. The audit uses group plausibility and targeted exceptions; it does not individually verify every Character. Compact per-row hazard flags derive from existing verified aliases/catalog and cached canonical wiki bodies. No new external Web request or authority source was needed.

The three HIGH patterns were examined first, then MEDIUM work/ecosystem groups, then high-frequency unresolved cases, then the remaining obvious shared families. Plausible single work/franchise signals are bulk ACCEPT unless a real-person, artist-qualified, fan/OC, non-work or identity hazard is present. Long-tail acceptance by this rule is intentionally a fast Browse judgment; an ACCEPT is not a new fact-checked source claim and may still contain errors.

The existing active Copyright hierarchy collapses related title/franchise hints only for this overlay, choosing a root already present among the subject's candidates. It never creates a formal Character relation. Independent-IP candidates remain unresolved. Dedicated Project Voltage qualifiers use `project_voltage`, avoiding an arbitrary choice between its Pokémon and Vocaloid parents. Clear costume names or cached costume/base descriptions can reuse an existing formal or already-reviewed provisional base Browse context; this does not validate VARIANT_OF in the authority layer.

The two recognizable blocked subjects `rx-78-2_gundam` and `p-head_producer` received only provisional Browse contexts (`gundam` / `idolmaster`). Their formal identity blocks are preserved. Artist alias collisions and author-qualified published-work cases were separated from OCs (`gridman_(ssss)`, `fox_wife_(batta_(kanzume_quality))`, `devil's_hand_(ishiyumi)`).

## Main error patterns corrected

- **Cast/performer association mistaken for fictional membership.** Voice actors routed into Love Live!, Honkai and other works, real racehorses routed into Umamusume, and real-person/singer contexts were rejected. Examples: `tsukine_kona -> love_live!`, `inoue_marina -> honkai_(series)`, `sunday_silence_(racehorse) -> umamusume`. Generic Minecraft YouTube association does not resolve the person/avatar distinction.
- **Nested artist qualifiers were missed.** Three HIGH entries and other MEDIUM entries such as artist-specific female Sensei / Kemono Friends designs were rejected; bracket balancing exposes the full canonical artist qualifier.
- **Guest/event context selected as HOME.** `family_computer_robot` changes from `super_smash_bros.` to `nintendo`; `english_miku` changes from `2026_fifa_world_cup` to `vocaloid`. These are provisional brand preferences, not origin authority.
- **Over-conservative related-root/variant handling.** Obvious related title/franchise and costume families were added together. Project Voltage retains its dedicated collaborative scope rather than losing one participating IP.

Top500's remaining ten are mainly independent VTubers without a specific existing brand root, an artist-qualified OC/fan identity and a still-ambiguous mascot. They were inspected and deliberately retained unresolved; no generic VTuber bucket or fabricated Copyright was forced on them. Top2000 counts use the original frozen 13,983-cohort ranks.

## Artifacts and reconstruction

- `PROVISIONAL_BROWSE_HOME_AUDIT_V1.csv`: all verdicts and audited Browse roots; `formal_authority_eligible=NO` throughout.
- `PROVISIONAL_BROWSE_HOME_AUDIT_GROUPS_V1.csv`: 2,355 reproducible groups by original HOME/reason/evidence pattern/verdict/result/rule, with counts and member samples.
- `PROVISIONAL_BROWSE_HOME_AUDIT_HINTS_V1.csv/.json`: compact frozen hazard/base-context flags and source hashes.
- `PROVISIONAL_BROWSE_HOME_AUDIT_CHECKPOINT_V1.json`: counts, stage breakdown and immutable original/authority fingerprints.

Rebuild: `python scripts/issue216/audit_provisional_browse_home.py`. The builder checks immutable formal/source/provisional input hashes, frozen hints, unique subjects and existing roots, and writes only the new audit artifacts. A repeated build reproduced them byte for byte; the original overlay and all three formal ledgers also match the base commit byte for byte. `git diff --check` passed. No new tests were added or locally run for this fast audit; the existing branch CI continues to guard formal coverage. No main merge or production apply.
