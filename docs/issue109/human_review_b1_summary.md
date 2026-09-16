# Issue #109 B1 human reverse-audit summary — IDs 1..800

Status: audit evidence only. No production mutation.

## Result

- population reviewed: 800
- `KEEP_SPECIAL`: 785
- `GENERAL_SUFFICIENT_CANDIDATE`: 13
- `NEEDS_REVIEW`: 2

The 15 non-KEEP rows are recorded in `human_review_b1_1_800.csv`.

## Decision pattern

General exact overlap by itself was not treated as a demotion reason. Most overlapping adult/fetish rows were returned to `KEEP_SPECIAL` because they retain deep-discovery value, including:

- sex acts and sexual positions;
- insertion/contact and actor/target/body-site relations;
- sex toys and fetish implements;
- BDSM/restraint/non-consensual context;
- fluids/excretion;
- tentacle/nonhuman/R18G concepts;
- specific genital/body states;
- unusual exposure states and explicitly sexual scene context.

The B1 General-sufficient candidates are limited to bare anatomy/body-site anchors, broad umbrella concepts, broad ordinary nudity states, general character-type rows, and one general expression row where General already provides exact canonical coverage.

## Candidate IDs

`1,54,213,509,578,636,638,649,664,665,666,722,724`

## Still needs definition review

- `49 presenting own body`
- `57 take your pick`

These remain unresolved because their names look generic but may encode a more specific Danbooru composition/semantic than the wording alone suggests.

## Safety / scope boundaries

- production Special mutated: NO
- local catalog rebuilt/updated: NO
- Issue #70 mutated: NO
- UserData mutated: NO
- IDs deleted/renumbered: NO
- candidate rows automatically removed: NO
