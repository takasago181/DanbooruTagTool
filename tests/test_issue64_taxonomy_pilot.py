"""Pilot contracts and failure modes, without requiring local protected inputs."""
import copy
import json
from pathlib import Path

import pytest

from tools import issue64_taxonomy_pilot as pilot

WORK = Path(__file__).resolve().parents[1] / "docs/issue64"


def inputs():
    return (pilot.read_json(WORK / "pilot_sidecar.json"),
            pilot.read_json(WORK / "artifacts/pilot_samples.json"),
            pilot.read_json(WORK / "taxonomy.json"))


def test_exact_committed_population_and_pilot_partition():
    content = (WORK / "artifacts/population.txt").read_bytes()
    names = content.decode("utf-8").splitlines()
    evidence = pilot.read_json(WORK / "artifacts/population_evidence.json")
    assert len(names) == len(set(names)) == 30629
    assert names == sorted(names)
    assert pilot.hashlib.sha256(content).hexdigest() == evidence["population_sha256_sorted_utf8_lf"]
    sidecar, samples, taxonomy = inputs()
    pilot.validate_sidecar(sidecar, samples, taxonomy)
    assert set(samples) <= set(names)
    assert len(samples) == 253
    assert sum(r["classification_status"] == "PROPOSED" for r in sidecar["entries"].values()) == 248
    assert sum(r["classification_status"] == "UNRESOLVED" for r in sidecar["entries"].values()) == 5


def test_sampling_deterministic_disjoint_and_target_only():
    entries = {f"tag_part_{i}": {} for i in range(400)}
    usage = {t: {"post_count": 200000 if i < 80 else 2000 if i < 220 else 100} for i,t in enumerate(entries)}
    first = pilot.select_pilot(entries, usage, ["tag_part_1"])
    second = pilot.select_pilot(dict(reversed(list(entries.items()))), usage, ["tag_part_1"])
    assert first == second
    assert len(first) == 128
    compound = {t for t,r in first.items() if "compound_hash32_disjoint" in r}
    assert len(compound) == 32
    assert all(len(first[t]) == 1 for t in compound)
    with pytest.raises(ValueError, match="non-population"):
        pilot.select_pilot(entries, usage, ["not_in_overlay"])
    with pytest.raises(ValueError, match="Pilot size cap"):
        pilot.select_pilot(entries, usage, list(entries))


@pytest.mark.parametrize("count,expected", [(999,"rare"),(1000,"ordinary"),(99999,"ordinary"),(100000,"high_usage")])
def test_usage_boundaries(count, expected):
    assert pilot.band(count) == expected


@pytest.mark.parametrize("mutation", ["unknown_tag", "missing_tag", "unknown_genre", "unknown_subgenre", "third_level", "duplicate_path", "unresolved_path", "review_promotion", "unknown_status", "missing_primary", "blank_reason", "overlay_field"])
def test_sidecar_rejects_drift_and_silent_promotion(mutation):
    sidecar, samples, taxonomy = inputs()
    rows = sidecar["entries"]
    row = rows["1girl"]
    if mutation == "unknown_tag": rows["non_target"] = copy.deepcopy(row)
    elif mutation == "missing_tag": rows.pop("1girl")
    elif mutation == "unknown_genre": row["primary_path"]["genre_id"] = "UNKNOWN"
    elif mutation == "unknown_subgenre": row["primary_path"]["subgenre_id"] = "MISSING"
    elif mutation == "third_level": row["primary_path"]["third_level"] = "TOO_DEEP"
    elif mutation == "duplicate_path": row["secondary_paths"] = [copy.deepcopy(row["primary_path"])]
    elif mutation == "unresolved_path": row["classification_status"] = "UNRESOLVED"
    elif mutation == "review_promotion": row["reviewed"] = True
    elif mutation == "unknown_status": row["classification_status"] = "ACCEPTED"
    elif mutation == "missing_primary": row["primary_path"] = None
    elif mutation == "blank_reason": row["classification_reason"] = ""
    elif mutation == "overlay_field": row["display_ja"] = "unauthorized mixed schema"
    with pytest.raises(ValueError):
        pilot.validate_sidecar(sidecar, samples, taxonomy)


def test_audit_counts_all_paths_and_unresolved_without_double_counting():
    sidecar, samples, taxonomy = inputs()
    usage = {t: {"post_count": s["post_count"]} for t,s in samples.items()}
    expected = pilot.read_json(WORK / "artifacts/pilot_audit.json")
    # Selection reasons are carried in sample metadata, not its keys.
    selected = {t:s["selection_reasons"] for t,s in samples.items()}
    actual = pilot.audit(sidecar, selected, usage, taxonomy)
    assert actual == expected
    assert sum(actual["primary_counts"].values()) == 248
    assert sum(actual["all_path_counts"].values()) == 275
    assert actual["production_classified_count"] == actual["reviewed_count"] == 0
    assert actual["visible_catch_all_count"] == 0


def test_duplicate_json_canonical_rejected(tmp_path):
    path = tmp_path / "duplicate.json"
    path.write_text('{"entries":{"same":{},"same":{}}}', encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        pilot.read_json(path)


def test_population_loader_fails_closed_on_source_drift(tmp_path, monkeypatch):
    overlay = tmp_path / "overlay.json"
    source = tmp_path / "v5.csv"
    usage = tmp_path / "usage.csv"
    manifest = tmp_path / "promotion.json"
    overlay.write_text(json.dumps({"format_version":1,"entries":{"tag":{"display_ja":"表示","search_ja":["検索"]}}}),encoding="utf-8")
    source.write_text('canonical,display_ja,search_ja\ntag,表示,検索\n',encoding="utf-8")
    usage.write_text('tag,0,100,\noutside,0,999999,\n',encoding="utf-8")
    manifest.write_text(json.dumps({"overlay":{"post_sha256":pilot.sha256(overlay)},"source":{"sha256":pilot.sha256(source)}}),encoding="utf-8")
    monkeypatch.setattr(pilot,"EXPECTED_COUNT",1)
    monkeypatch.setattr(pilot,"USAGE_SHA256",pilot.sha256(usage))
    entries, counts = pilot.load_population(overlay,usage,source,manifest)
    assert set(entries) == set(counts) == {"tag"}
    for target, match in [(overlay,"overlay hash"),(source,"source hash"),(usage,"snapshot hash")]:
        before = target.read_bytes()
        target.write_bytes(before+b" ")
        with pytest.raises(ValueError, match=match):
            pilot.load_population(overlay,usage,source,manifest)
        target.write_bytes(before)


def test_supplement_preserves_original_draws_and_rejects_duplicates():
    entries = {f"tag_part_{i}": {} for i in range(400)}
    usage = {t: {"post_count": 200000 if i < 80 else 2000 if i < 220 else 100} for i,t in enumerate(entries)}
    original = pilot.select_pilot(entries, usage, ["tag_part_1"])
    new = sorted(set(entries)-set(original))[:80]
    revised = pilot.select_pilot(entries, usage, ["tag_part_1"], {"targeted":new})
    assert all(revised[t] == reasons for t,reasons in original.items())
    assert set(revised)-set(original) == set(new)
    with pytest.raises(ValueError, match="unique, new"):
        pilot.select_pilot(entries, usage, ["tag_part_1"], {"targeted":new[:-1]+[next(iter(original))]})
    with pytest.raises(ValueError, match="64–96"):
        pilot.select_pilot(entries, usage, ["tag_part_1"], {"targeted":new[:10]})


def test_revision_evidence_and_changed_verdicts_reproduce():
    sidecar, samples, _ = inputs()
    selected = {t:s["selection_reasons"] for t,s in samples.items()}
    baseline = pilot.read_json(WORK / "pilot_v1_baseline.json")
    external = pilot.read_json(WORK / "external_evidence.json")
    result = pilot.revision_audit(sidecar, selected, baseline, external)
    assert result == pilot.read_json(WORK / "artifacts/revision_audit.json")
    assert result["added_count"] == 80
    assert result["external_rechecked_rows"] == 97
    assert len(result["resolved_existing_tags"]) == 9
    assert result["changed_existing_count"] == 14
    assert len(result["remaining_existing_unresolved"]) == 3
    assert len(result["new_unresolved"]) == 2


@pytest.mark.parametrize("mutation", ["missing_new", "missing_old_unresolved", "bad_reference", "fake_acceptance", "missing_hash", "duplicate_post", "wrong_target", "removed_original"])
def test_revision_evidence_rejects_missing_or_untraceable_claims(mutation):
    sidecar, samples, _ = inputs()
    selected = {t:s["selection_reasons"] for t,s in samples.items()}
    baseline = pilot.read_json(WORK / "pilot_v1_baseline.json")
    external = pilot.read_json(WORK / "external_evidence.json")
    if mutation == "missing_new": external["entries"].pop("polka_dot")
    elif mutation == "missing_old_unresolved": external["entries"].pop("aa-12")
    elif mutation == "bad_reference": sidecar["entries"]["aa-12"]["source"] = "untraceable"
    elif mutation == "fake_acceptance": external["entries"]["aa-12"]["independent_semantic_acceptance"] = True
    elif mutation == "missing_hash": external["entries"]["aa-12"]["sources"][0]["body_sha256_utf8"] = ""
    elif mutation == "removed_original": sidecar["entries"].pop("1girl")
    else:
        source = external["entries"]["nijigasaki_7th_live!_new_tokimeki_land"]["sources"][1]
        if mutation == "duplicate_post": source["posts"][1] = copy.deepcopy(source["posts"][0])
        elif mutation == "wrong_target": source["posts"][0]["target_tag_present"] = False
    with pytest.raises(ValueError):
        pilot.revision_audit(sidecar, selected, baseline, external)
