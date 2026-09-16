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
    # genital / anal / explicit state
    'futa_without_balls', 'cospussy', 'cunt_punt', 'extreme_gaping',
    # restraint / BDSM topology and perspective
    'viewer_holding_leash', 'viewer_on_leash', 'straitjacket', 'upright_restraints',
    'shared_handcuffs', 'shackle_piercing', 'standing_restraints', 'open-chest_straitjacket',
    # sexual acts / exposure / fluid relation
    'extended_downblouse', 'buttjob_over_clothes', 'saliva_swap', 'cooperative_buttjob',
    'extended_upskirt', 'buttjob_under_clothes', "unzipping_another's_clothes",
    # device / reproduction / nonhuman / R18G
    'electrostimulation', 'artificial_insemination', 'implied_egg_laying', 'intestine_clothing',
}

STRICT_NEEDS_DEFINITION_REVIEW = {
    'breast_drop', 'groping_motion', 'uterus_pose', 'offering_leash', 'single_breast',
    'breast_slider', 'powerful_breasts', 'saliva_pool', 'excessive_saliva',
    'female_fertilization', 'breast_reduction', 'breast_band',
}

# Independent rescue from the high-post-count uncovered queue. These were missed by
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
}

SUPPLEMENTAL_NEEDS_DEFINITION_REVIEW = {
    'rope_around_neck', 'cuffed', 'edging_underwear', 'pointless_condom',
}

# Known broad/basic or lexical false-positive families should remain General unless a
# separate concrete deep-discovery reason is established. This is not a content filter.
NONPRODUCT_NAME_FALSE_POSITIVES = {
    'tit_(bird)', 'long-tailed_tit', 'bleeding_heart_(flower)', 'yaoi_(object)', 'yuri_(object)',
    'mixed-sex_combat',
}

OFFICIAL_EVIDENCE = {
    'breast_group': 'https://shima.donmai.us/wiki_pages/tag_group%3Abreasts_tags',
    'body_parts': 'https://shima.donmai.us/wiki_pages/tag_group%3Abody_parts',
    'tag_checklist': 'https://safebooru.donmai.us/wiki_pages/howto%3Atag_checklist',
    'leash': 'https://safebooru.donmai.us/wiki_pages/leash?z=2',
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
    if tag in STRICT_NEEDS_DEFINITION_REVIEW:
        return 'NEEDS_DEFINITION_REVIEW', 'surface appears potentially relevant but exact Danbooru semantics or product boundary needs definition-level confirmation'
    if tag in NONPRODUCT_NAME_FALSE_POSITIVES or '(meme)' in tag:
        return 'REJECT_NONCONTENT_REASON', 'name match is a non-product lexical/meme/object false positive, not rejected because of explicitness'
    return 'GENERAL_ONLY_APPROPRIATE', 'broad/basic descriptor, ordinary object/state, arbitrary Cartesian placement, color variant, or low-value scene label is better served by General'


def supplemental_decision(tag: str) -> tuple[str, str]:
    if tag in SUPPLEMENTAL_SPECIAL_CANDIDATES:
        return 'SPECIAL_CANDIDATE', 'high-frequency/opaque rescue: concrete fetish/sexual/body-site relation missed by strict adult-name heuristic'
    if tag in SUPPLEMENTAL_NEEDS_DEFINITION_REVIEW:
        return 'NEEDS_DEFINITION_REVIEW', 'high-frequency rescue surface needs exact definition or duplicate/substantive-coverage check before Special admission'
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

    missing_strict = sorted((STRICT_SPECIAL_CANDIDATES | STRICT_NEEDS_DEFINITION_REVIEW | NONPRODUCT_NAME_FALSE_POSITIVES) - {r['canonical_tag'] for r in strict_new})
    if missing_strict:
        raise ValueError(f'curated strict tags not in new strict review set: {missing_strict}')
    missing_supp = sorted((SUPPLEMENTAL_SPECIAL_CANDIDATES | SUPPLEMENTAL_NEEDS_DEFINITION_REVIEW) - set(by_tag))
    if missing_supp:
        raise ValueError(f'supplemental tags not in top uncovered queue: {missing_supp}')

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
    for tag in sorted(SUPPLEMENTAL_SPECIAL_CANDIDATES | SUPPLEMENTAL_NEEDS_DEFINITION_REVIEW):
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
            for r in candidate_rows[:100]
        ],
        'official_evidence': OFFICIAL_EVIDENCE,
        'all_issue94_prescreen_missed_strict_rows_reviewed': 'YES',
        'top_queue_rescue_is_exhaustive_all_5000': 'NO',
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
