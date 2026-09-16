#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

# Explicitly curated after reviewing the Issue #104 strict adult queue against the
# current Special design, Issue #94 final outcomes, and current Danbooru tag-group/wiki
# semantics. These are audit candidates only, never automatic production promotions.
STRICT_SPECIAL_CANDIDATES = {
    # breast / nipple / areola morphology, exposure and actions
    'breast_milk_in_container', 'saliva_on_breasts', 'breast_curtains', 'perky_breasts',
    'veiny_breasts', 'breasts_on_glass', 'face_to_breasts', 'sweaty_breasts',
    'single_breast_curtain', 'pointy_breasts', 'light_areolae', 'speckled_areolae',
    'handsfree_breast_squeeze', "poking_another's_breast", 'dark_areolae', 'breast_zipper',
    'asymmetrical_breasts', 'extra_breasts', 'male_with_breasts', 'breast_implants',
    'breast_pillow', 'breasts_on_head', 'covering_one_breast', "covering_another's_breasts",
    'breast_on_breast', 'tickling_breasts', 'breast_massage', 'slapping_breasts',
    'kissing_breast', "foot_on_another's_breast", 'lube_on_breasts', 'breast_pull',
    'breast_crush', 'tied_breast', 'breast_punch', 'slapping_with_breasts', 'weighing_breasts',
    'compressed_breasts', 'breasts_on_thighs', 'fluid_on_breasts', 'breast_size_switch',
    'breast_size_difference', 'mole_on_areola', 'pov_breasts', 'breast_shake', 'areola_measuring',
    # resolved definition-review breast/body states
    'breast_drop', 'single_breast', 'powerful_breasts', 'breast_reduction',
    # genital / anal / explicit state
    'futa_without_balls', 'cospussy', 'cunt_punt', 'extreme_gaping',
    # restraint / BDSM topology and perspective
    'viewer_holding_leash', 'viewer_on_leash', 'straitjacket', 'upright_restraints',
    'shared_handcuffs', 'shackle_piercing', 'standing_restraints', 'open-chest_straitjacket',
    'offering_leash',
    # sexual acts / exposure / fluid relation / niche pose
    'extended_downblouse', 'buttjob_over_clothes', 'saliva_swap', 'cooperative_buttjob',
    'extended_upskirt', 'buttjob_under_clothes', "unzipping_another's_clothes",
    'groping_motion', 'uterus_pose',
    # device / reproduction / nonhuman / R18G
    'electrostimulation', 'artificial_insemination', 'female_fertilization',
    'implied_egg_laying', 'intestine_clothing',
}

# Final definition-level routing for strict adult/fetish-name hits that do not merit
# separate Special identity despite being valid Danbooru General tags.
STRICT_GENERAL_ONLY = {
    'saliva_pool', 'excessive_saliva', 'breast_band',
}

# Independent rescue from the full uncovered General inventory. These were missed by
# the strict canonical adult-name heuristic but are concrete fetish/sexual/body-site
# structures worth Special review.
SUPPLEMENTAL_SPECIAL_CANDIDATES = {
    'condom_in_mouth', 'presenting_own_armpit', 'sweaty_armpits', 'armpit_focus',
    'smelly_armpits', 'smelling_armpit', 'face_in_armpit', 'sweaty_feet',
    "feet_on_another's_face", 'rope_marks', 'shibarikini', 'male_underwear_aside',
    "hand_in_another's_panties", 'used_condom_in_clothes', 'broken_condom',
    'sabotaged_condom', 'condom_in_ass', 'condom_on_tongue', 'condom_on_ass',
    'putting_on_condom', 'condom_pull', 'drinking_from_condom', 'condom_thigh_strap',
    'condom_wrapper_in_clothes', 'wet_male_underwear', 'stained_panties',
    # resolved rescue queue
    'rope_around_neck', 'pointless_condom',
}

SUPPLEMENTAL_ALREADY_COVERED = {
    # Current Special already contains direct `cuffs`, `handcuffs`, `shackles`, and
    # structured `bound wrists`; a separate deep identity for the adjectival state
    # would add little discovery value.
    'cuffed',
}

SUPPLEMENTAL_GENERAL_ONLY = {
    # Danbooru lists this under male-underwear color/trim variants; "edging" here is
    # garment edging, not sexual edging.
    'edging_underwear',
}

# Known broad/basic or lexical false-positive families should remain General unless a
# separate concrete deep-discovery reason is established. This is not a content filter.
NONPRODUCT_NAME_FALSE_POSITIVES = {
    'tit_(bird)', 'long-tailed_tit', 'bleeding_heart_(flower)', 'yaoi_(object)', 'yuri_(object)',
    'mixed-sex_combat',
    # Gameplay/user-interface control, not a breast-state identity.
    'breast_slider',
}

OFFICIAL_EVIDENCE = {
    'breast_group': 'https://shima.donmai.us/wiki_pages/tag_group%3Abreasts_tags',
    'body_parts': 'https://shima.donmai.us/wiki_pages/tag_group%3Abody_parts',
    'tag_checklist': 'https://safebooru.donmai.us/wiki_pages/howto%3Atag_checklist',
    'leash': 'https://safebooru.donmai.us/wiki_pages/leash?z=2',
    'holding_own_leash': 'https://safebooru.donmai.us/wiki_pages/holding_own_leash',
    'groping_motion': 'https://safebooru.donmai.us/wiki_pages/groping_motion',
    'cuffs': 'https://safebooru.donmai.us/wiki_pages/cuffs',
    'bound_wrists': 'https://safebooru.donmai.us/wiki_pages/bound_wrists',
    'male_underwear': 'https://shima.donmai.us/wiki_pages/male_underwear',
    'saliva_pool': 'https://safebooru.donmai.us/posts?tags=saliva_pool',
    'gameplay_mechanics': 'https://safebooru.donmai.us/posts?page=9&tags=gameplay_mechanics',
    'standing_restraints': 'https://safebooru.donmai.us/wiki_pages/standing_restraints?z=2',
    'breast_zipper': 'https://safebooru.donmai.us/wiki_pages/breast_zipper?z=2',
    'breast_curtains': 'https://safebooru.donmai.us/posts?tags=breast_curtains',
    'shibarikini': 'https://safebooru.donmai.us/wiki_pages/shibarikini',
    'hand_in_anothers_panties': "https://safebooru.donmai.us/wiki_pages/hand_in_another%27s_panties?z=1",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)


def strict_decision(row: dict[str, str]) -> tuple[str, str]:
    tag = row['canonical_tag']
    if tag in STRICT_SPECIAL_CANDIDATES:
        return 'SPECIAL_CANDIDATE', 'specific adult/fetish/body-site/action/topology identity adds deep-discovery value beyond broad General browsing'
    if tag in STRICT_GENERAL_ONLY:
        return 'GENERAL_ONLY_APPROPRIATE', 'valid canonical state but broad/nonsexual or ordinary-enough that existing General plus broader Special concepts are sufficient'
    if tag in NONPRODUCT_NAME_FALSE_POSITIVES or '(meme)' in tag:
        return 'REJECT_NONCONTENT_REASON', 'name match is a non-product lexical/meme/object/UI false positive, not rejected because of explicitness'
    return 'GENERAL_ONLY_APPROPRIATE', 'broad/basic descriptor, ordinary object/state, arbitrary Cartesian placement, color variant, or low-value scene label is better served by General'


def supplemental_decision(tag: str) -> tuple[str, str]:
    if tag in SUPPLEMENTAL_SPECIAL_CANDIDATES:
        return 'SPECIAL_CANDIDATE', 'opaque rescue: concrete fetish/sexual/body-site/restraint relation missed by strict adult-name heuristic'
    if tag in SUPPLEMENTAL_ALREADY_COVERED:
        return 'ALREADY_SUBSTANTIVELY_COVERED', 'current Special already exposes the same practical restraint concept through direct implement/action identities'
    if tag in SUPPLEMENTAL_GENERAL_ONLY:
        return 'GENERAL_ONLY_APPROPRIATE', 'valid General tag but ordinary garment/color/trim semantics do not justify separate adult/fetish deep identity'
    raise AssertionError(tag)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--strict-crosswalk', required=True)
    ap.add_argument('--top-uncovered', required=True)
    ap.add_argument('--out-dir', required=True)
    args = ap.parse_args()

    strict = read_csv(Path(args.strict_crosswalk))
    top = read_csv(Path(args.top_uncovered))
    strict_new = [r for r in strict if r['issue94_crosswalk'] == 'NEW_TO_ADULT_FOCUSED_REVIEW']
    by_tag = {r['canonical_tag']: r for r in top}

    curated_strict = STRICT_SPECIAL_CANDIDATES | STRICT_GENERAL_ONLY | NONPRODUCT_NAME_FALSE_POSITIVES
    missing_strict = sorted(curated_strict - {r['canonical_tag'] for r in strict_new})
    if missing_strict:
        raise ValueError(f'curated strict tags not in new strict review set: {missing_strict}')
    curated_supp = SUPPLEMENTAL_SPECIAL_CANDIDATES | SUPPLEMENTAL_ALREADY_COVERED | SUPPLEMENTAL_GENERAL_ONLY
    missing_supp = sorted(curated_supp - set(by_tag))
    if missing_supp:
        raise ValueError(f'supplemental tags not in uncovered queue: {missing_supp}')

    reviewed: list[dict[str, object]] = []
    for r in strict_new:
        decision, reason = strict_decision(r)
        out = dict(r)
        out.update({
            'review_source': 'STRICT_CANONICAL_ADULT_PRIORITY',
            'product_fit_decision': decision,
            'product_fit_reason': reason,
        })
        reviewed.append(out)

    supplemental_rows = []
    for tag in sorted(curated_supp):
        r = dict(by_tag[tag])
        decision, reason = supplemental_decision(tag)
        r.update({
            'issue94_crosswalk': r.get('issue94_crosswalk', 'NOT_IN_ISSUE94_FINAL_REVIEW'),
            'issue94_final_status': r.get('issue94_final_status', ''),
            'issue94_final_reason': r.get('issue94_final_reason', ''),
            'review_source': 'HIGH_FREQUENCY_UNFLAGGED_RESCUE',
            'product_fit_decision': decision,
            'product_fit_reason': reason,
        })
        supplemental_rows.append(r)
        reviewed.append(r)

    reviewed.sort(key=lambda r: (-int(r['post_count']), str(r['canonical_tag'])))
    candidate_rows = [r for r in reviewed if r['product_fit_decision'] == 'SPECIAL_CANDIDATE']
    needs_rows = [r for r in reviewed if r['product_fit_decision'] == 'NEEDS_DEFINITION_REVIEW']
    candidate_rows.sort(key=lambda r: (-int(r['post_count']), str(r['canonical_tag'])))
    needs_rows.sort(key=lambda r: (-int(r['post_count']), str(r['canonical_tag'])))

    fields = list(reviewed[0].keys()) if reviewed else []
    out_dir = Path(args.out_dir)
    write_csv(out_dir/'product_fit_review_v1.csv', reviewed, fields)
    write_csv(out_dir/'special_candidate_subset_v1.csv', candidate_rows, fields)
    write_csv(out_dir/'definition_review_queue_v1.csv', needs_rows, fields)
    write_csv(out_dir/'supplemental_rescue_review_v1.csv', supplemental_rows, fields)

    counts = Counter(r['product_fit_decision'] for r in reviewed)
    strict_counts = Counter(r['product_fit_decision'] for r in reviewed if r['review_source'] == 'STRICT_CANONICAL_ADULT_PRIORITY')
    supplemental_counts = Counter(r['product_fit_decision'] for r in reviewed if r['review_source'] == 'HIGH_FREQUENCY_UNFLAGGED_RESCUE')
    summary = {
        'mode': 'ISSUE104_PRODUCT_FIT_REVIEW_V1',
        'strict_new_reviewed': len(strict_new),
        'supplemental_high_frequency_rescue_reviewed': len(supplemental_rows),
        'total_reviewed': len(reviewed),
        'decision_counts': dict(sorted(counts.items())),
        'strict_decision_counts': dict(sorted(strict_counts.items())),
        'supplemental_decision_counts': dict(sorted(supplemental_counts.items())),
        'special_candidate_count': len(candidate_rows),
        'needs_definition_review_count': len(needs_rows),
        'top_special_candidates': [
            {'tag': r['canonical_tag'], 'post_count': int(r['post_count']), 'source': r['review_source']}
            for r in candidate_rows[:120]
        ],
        'official_evidence': OFFICIAL_EVIDENCE,
        'all_issue94_prescreen_missed_strict_rows_reviewed': 'YES',
        'definition_review_queue_resolved': 'YES' if not needs_rows else 'NO',
        'uncovered_inventory_used_for_rescue': 'YES',
        'adult_content_used_as_rejection_reason': 'NO',
        'automatic_production_promotion': 'NO',
        'production_mutation': 'NO',
        'issue70_mutated': 'NO',
        'userdata_mutated': 'NO',
        'pseudo_canonical_created': 'NO',
        'content_filter_used': 'NO',
    }
    (out_dir/'product_fit_review_summary_v1.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
