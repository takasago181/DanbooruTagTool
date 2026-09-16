# Issue #109 B2 human reverse-audit summary — IDs 801..1600

Status: audit evidence only. No production mutation.

## Result

- population reviewed: 800
- `KEEP_SPECIAL`: 646
- `GENERAL_SUFFICIENT_CANDIDATE`: 14
- `NEEDS_REVIEW`: 140

## Bounded checkpoints

- 801..1000: KEEP_SPECIAL 125, GENERAL_SUFFICIENT_CANDIDATE 6, NEEDS_REVIEW 69
- 1001..1200: KEEP_SPECIAL 139, GENERAL_SUFFICIENT_CANDIDATE 8, NEEDS_REVIEW 53
- 1201..1400: KEEP_SPECIAL 183, GENERAL_SUFFICIENT_CANDIDATE 0, NEEDS_REVIEW 17
- 1401..1600: KEEP_SPECIAL 199, GENERAL_SUFFICIENT_CANDIDATE 0, NEEDS_REVIEW 1

The four ranges were reviewed independently and then combined by stable `special_id`; no ID was deleted, compacted, or renumbered.

## General-sufficient candidate IDs

`835,875,876,914,939,953,1021,1040,1052,1055,1082,1084,1166,1168`

These are candidates only. They are narrow broad/context/object/scope rows for which the current General canonical, Japanese overlay/search, and (where present) #64 browse path provide a practical route. Exact overlap alone was not used as a demotion rule; specialized sex acts, insertion/contact topology, sex toys, BDSM, fluids, nonhuman concepts, and special body states remain KEEP unless definition evidence is unresolved.

## Needs-review IDs

`801,805,806,809,813,815,819,820,823,824,825,827,828,829,831,833,838,839,844,845,852,854,855,857,861,862,864,865,867,868,873,874,879,883,884,885,886,888,889,890,892,899,900,902,907,909,911,913,922,928,935,941,942,943,948,950,956,957,960,963,970,971,973,978,985,986,989,991,999,1001,1002,1005,1011,1012,1013,1016,1017,1023,1026,1027,1028,1034,1037,1041,1048,1049,1057,1062,1064,1065,1068,1069,1073,1075,1076,1078,1085,1095,1098,1102,1106,1112,1116,1117,1120,1122,1123,1137,1139,1140,1145,1147,1148,1152,1161,1167,1171,1173,1180,1186,1187,1198,1203,1204,1208,1217,1218,1220,1223,1228,1231,1236,1237,1238,1239,1240,1243,1244,1308,1577`

NEEDS_REVIEW includes the mechanical review queue rows whose deep-vs-General boundary is not safe to collapse, plus old Product-Fit REVIEW/OUT_OF_SCOPE or canonical/definition conflicts that require a separate definition decision. In particular, consent, identity-sensitive context, ambiguous memes, and alias/canonical conflicts were not normalized.

## General discoverability evidence

The review uses the current #64 effective sidecar for exact canonical overlap and primary browse paths, plus the local read-only `data/runtime/japanese_overlay.json` (30,629 entries) for `display_ja` and `search_ja`. The overlay and protected production inputs were read only; they were not changed or rebuilt.

## Provenance and boundaries

- source: current production Special profile and current #109 Phase A ledger
- previous Product-Fit verdict: copied per row as supporting evidence only
- IDs 801..1600 are legacy Special IDs; no #96/#107 expansion rows are in this tranche
- production Special mutated: NO
- production Special deleted: NO
- Special IDs renumbered/compacted: NO
- local catalog rebuilt/updated: NO
- local 3,088 integration performed: NO
- Issue #70 mutated: NO
- UserData mutated: NO
- General production mutated: NO
