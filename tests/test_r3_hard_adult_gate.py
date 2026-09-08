from translation_quarantine.r3.r3_hard_adult_gate import (
    score_ambiguity_results,
    validate_design,
)


def _challenge_rows():
    quotas = {
        "ANATOMY_BOUNDARY": 6,
        "SEXUAL_ACTION": 10,
        "INSERTION_TOY_MACHINE": 12,
        "BDSM_RESTRAINT_DOMINATION": 12,
        "FLUID_EXCRETION_CONTAMINATION": 12,
        "TENTACLE_NONHUMAN": 8,
        "REPRODUCTION_LACTATION": 4,
    }
    rows = []
    number = 0
    for stratum, count in quotas.items():
        for _ in range(count):
            number += 1
            rows.append(
                {
                    "challenge_id": f"HAC-{number:03d}",
                    "stratum": stratum,
                    "special_id": number,
                    "canonical": f"c{number}",
                }
            )
    return rows


def test_design_and_scoring():
    rows = _challenge_rows()
    probes = [
        {
            "probe_id": "p1",
            "expected_behavior": "RESOLVE_ONE",
            "expected_canonicals": ["c1"],
            "forbid_singleton_auto_ready": False,
        },
        {
            "probe_id": "p2",
            "expected_behavior": "RETURN_SET",
            "minimum_expected_candidates": ["c2", "c3"],
            "forbid_singleton_auto_ready": True,
        },
        {
            "probe_id": "p3",
            "expected_behavior": "REVIEW_DECOMPOSE",
            "candidate_hints": ["c4"],
            "forbid_singleton_auto_ready": True,
        },
    ]
    for index in range(4, 17):
        probes.append(
            {
                "probe_id": f"p{index}",
                "expected_behavior": "RESOLVE_ONE",
                "expected_canonicals": [f"c{index}"],
                "forbid_singleton_auto_ready": False,
            }
        )
    assert validate_design(rows, probes)["ok"]

    results = [
        {
            "probe_id": "p1",
            "resolved_canonicals": ["c1"],
            "auto_ready_canonical": "c1",
            "decision": "READY_ONE",
        },
        {
            "probe_id": "p2",
            "resolved_canonicals": ["c2", "c3"],
            "auto_ready_canonical": "",
            "decision": "RETURN_SET",
        },
        {
            "probe_id": "p3",
            "resolved_canonicals": ["c4"],
            "auto_ready_canonical": "",
            "decision": "REVIEW_DECOMPOSE",
        },
    ]
    for index in range(4, 17):
        results.append(
            {
                "probe_id": f"p{index}",
                "resolved_canonicals": [f"c{index}"],
                "auto_ready_canonical": f"c{index}",
                "decision": "READY_ONE",
            }
        )
    assert score_ambiguity_results(probes, results)["ok"]


def test_broad_probe_singleton_is_false_ready():
    probes = [
        {
            "probe_id": "p",
            "expected_behavior": "RETURN_SET",
            "minimum_expected_candidates": ["a", "b"],
            "forbid_singleton_auto_ready": True,
        }
    ]
    scored = score_ambiguity_results(
        probes,
        [
            {
                "probe_id": "p",
                "resolved_canonicals": ["a"],
                "auto_ready_canonical": "a",
                "decision": "READY_ONE",
            }
        ],
    )
    assert not scored["ok"]
    assert scored["metrics"]["false_singleton_ready"] >= 1
