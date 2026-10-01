# Issue #180 — Major Copyright roster expansion plan

## Why the first full export is rejected
The 35,890-row first user-review export is a safety baseline, not a freeze candidate. It over-relied on terminal qualifiers and therefore left obvious official characters such as unqualified roster members unresolved.

## Revised authority order
1. OFFICIAL/CURATED COPYRIGHT ROSTER membership (direct Character -> canonical home root)
2. accepted exact qualifier/root authority
3. accepted variant/base-character inheritance where base HOME is already confirmed
4. otherwise HOME_UNRESOLVED

Legacy RelatedCopyright and co-occurrence remain non-authoritative.

## Bulk-first execution
Do not review 35,890 characters one by one. Work by high-yield Copyright family/roster, then expand membership deterministically across all matching Character rows.

Priority families include:
blue_archive, touhou, pokemon, hololive, kantai_collection, fate_(series), Piapro/VOCALOID-family policy, genshin_impact, goddess_of_victory:_nikke, umamusume, azur_lane, arknights, honkai:_star_rail, wuthering_waves, girls'_frontline, granblue_fantasy and other high-volume roots.

## Required gates
- direct roster evidence must identify the character, not merely the title;
- one Character -> max one HOME;
- variants may inherit only after base identity mapping is proven;
- umbrella/subseries conflicts remain unresolved;
- no old RelatedCopyright fallback;
- no production/main/accepted-source mutation;
- regenerate all 35,890 rows only after roster expansion and full regression.

## User synchronization rule
Batch all independent roster work and validation into long bounded runs. Do not stop merely because one small CI job completed. Ask the user to wait only when an external CI run is genuinely still executing and its result is required for the next dependent stage.
