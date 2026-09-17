#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

SOURCE = Path('docs/issue118/special_only_explicit_v21/residual_unclassified_v21.csv')
OUT = Path('docs/issue118/special_only_explicit_v21_1')

# Discovery-only patterns. These intentionally target explicit sexual concepts,
# common aliases/misspellings, and sexual-position/fetish terms. They are NOT
# classification authority; candidates must pass independent review.
PATTERNS = {
    'anal_or_ass_sexual': re.compile(
        r'(?:^|_)(?:analbeads|analingus|annilingus|anal_play|ass_play|ass_spread|assfuck|assjob|buttfuck|buttsex|buttplug|butt_plug|butt_hole|butthole|ass_hole|asshole|bare_ass)(?:_|$)'
    ),
    'genital_anatomy_or_slang': re.compile(
        r'(?:^|_)(?:clit|clitslip|clit_slip|labia|manko|genitalia|genitals|foreskin|camel_toe|covered_erection|erect_clit|invisicock|dickgirl|dickhead|horsecock)(?:_|$)'
    ),
    'oral_sex_alias': re.compile(
        r'(?:^|_)(?:bj|blow_job|boobjob|breastjob|deep_throat|facefuck|face_sitting|felatio|cunilingus|cunillingus|cunnillingus|foot_lick|foot_licking|ball_licking|ball_sucking|lick_balls)(?:_|$)'
    ),
    'masturbation_alias': re.compile(
        r'(?:^|_)(?:masturbate|masturbating|jerk_off|jerking_off|jerkoff)(?:_|$)'
    ),
    'cum_or_orgasm_alias': re.compile(
        r'(?:^|_)(?:climaxing|coming|cumming|jizz|cream_pie|bukake|bukakke|cumflation|cumpool|cumstring|cumswap|multiple_cumshots)(?:_|$)'
    ),
    'penetration_or_insertion': re.compile(
        r'(?:^|_)(?:deep_insertion|extreme_insertion|huge_insertion|imminent_insertion|multiple_insertion|doublepenetration|double_penetration|dp|intercrural)(?:_|$)'
    ),
    'sexual_position': re.compile(
        r'(?:^|_)(?:doggy|doggy_style|cowgirl|female_on_top|male_on_top|guy_on_top|missionary_position|mating_press_position|from_behind_position|face-down_ass-up|face_down_ass_up)(?:_|$)'
    ),
    'group_sex_alias': re.compile(
        r'(?:^|_)(?:fourway|gangrape|gangsex|groupsex)(?:_|$)'
    ),
    'sexual_assault_or_consent': re.compile(
        r'(?:^|_)(?:dubcon|dubious_consent|non-consensual|nonconsensual|molester|molesting|gangrape)(?:_|$)'
    ),
    'explicit_fetish_or_bdsm': re.compile(
        r'(?:^|_)(?:age_play|autoerotic_asphyxiation|ballbusting|ball_busting|ballgag|bitgag|breath_play|breeding_kink|chastity_device|choking_play|coaching_\(sexual\)|coprophilia|crotchrope|egg_vibrators|erotic_asphyxiation|golden_shower_play|hogtied|hotdogging|love_egg|milking_device)(?:_|$)'
    ),
    'nudity_or_explicit_exposure': re.compile(
        r'(?:^|_)(?:bottom_less|full_nudity|nip_slip|nippleslip|nipslip|exposed_genitals|hadaka_apron|nakedapron|nakedribbon)(?:_|$)'
    ),
    'sexual_content_synonym': re.compile(
        r'(?:^|_)(?:ecchi|ero|eroguro|explicit|hardcore|innuendo)(?:_|$)'
    ),
    'sexual_contact_or_grinding': re.compile(
        r'(?:^|_)(?:fondle|fondling|grope|grinding_\(sexual\)|cooperative_grinding_\(sexual\)|tribadism|scissoring|frotting|hotdogging)(?:_|$)'
    ),
    'sexual_role_or_preference': re.compile(
        r'(?:^|_)(?:bottom_\(sexual_preference\)|futa|futa_with_cuntboy|cuntboy_with_cuntboy|cuntboy_with_female|newhalf)(?:_|$)'
    ),
    'explicit_machine_or_device': re.compile(
        r'(?:^|_)(?:fuckmachine|humbler|chastity_device|egg_vibrators|milking_device)(?:_|$)'
    ),
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def stable_rank(key: str) -> str:
    return hashlib.sha256(('issue118-special-explicit-v21.1|' + key).encode('utf-8')).hexdigest()


def main() -> int:
    rows = read_csv(SOURCE)
    if len(rows) != 467:
        raise SystemExit(f'expected 467 v21 residual rows, got {len(rows)}')

    candidates = []
    residual = []
    counts = Counter()
    for row in rows:
        key = row['identity_key']
        hits = [name for name, pattern in PATTERNS.items() if pattern.search(key.lower())]
        if hits:
            candidates.append({
                'identity_key': key,
                'state': 'EXPLICIT_SEXUAL_CANDIDATE_V21_1',
                'evidence_flags': '+'.join(hits),
            })
            for hit in hits:
                counts[hit] += 1
        else:
            residual.append({'identity_key': key, 'state': 'SPECIAL_ONLY_RESIDUAL_UNCLASSIFIED_V21_1'})

    holdout_keys = sorted((r['identity_key'] for r in candidates), key=stable_rank)[:120]
    holdout = [
        {'identity_key': key, 'candidate_state': 'EXPLICIT_SEXUAL_HOLDOUT_V21_1', 'human_intent': '', 'review_note': ''}
        for key in holdout_keys
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / 'explicit_sexual_candidate_v21_1.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','state','evidence_flags'], lineterminator='\n')
        w.writeheader(); w.writerows(candidates)
    with (OUT / 'residual_unclassified_v21_1.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','state'], lineterminator='\n')
        w.writeheader(); w.writerows(residual)
    with (OUT / 'fresh_holdout_template_v21_1.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n')
        w.writeheader(); w.writerows(holdout)

    summary = {
        'issue': 118,
        'mode': 'SPECIAL_ONLY_EXPLICIT_SEXUAL_DISCOVERY_V21_1_ALIASES',
        'source_rows': len(rows),
        'explicit_candidate_rows': len(candidates),
        'residual_unclassified_rows': len(residual),
        'evidence_flag_counts': dict(sorted(counts.items())),
        'fresh_holdout_template_rows': len(holdout),
        'selection_rules_use': 'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'excludes_generic_violence_alone': 'YES',
        'excludes_minor_or_child_terms_alone': 'YES',
        'holdout_verdicts_generated': 'NO',
        'auto_promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
        'next_gate': 'independently review fixed candidate holdout; if candidate set is <=120, review all candidates',
    }
    (OUT / 'summary_v21_1.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
