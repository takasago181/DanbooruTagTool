from tools.issue64_production_candidate_validate import validate


def test_clean_production_candidate_passes_exact_population_and_paths():
    report = validate()
    assert report["pass"] is True, report["errors"]
    assert report["population_count"] == 30_629
    assert report["totals"] == {
        "proposed": 28_226,
        "unresolved": 2_403,
        "confidence": {"HIGH": 25_097, "MEDIUM": 3_129, "LOW": 2_403},
    }
