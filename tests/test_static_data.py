from pathlib import Path
import csv
import hashlib

ROOT = Path(__file__).resolve().parents[1]

def test_raw_danbooru_is_headerless_4_columns_and_124016_rows():
    p = ROOT / "data/source/danbooru-2026-09-02.csv"
    count = 0
    cats = set()
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        first = next(r)
        assert len(first) == 4
        assert first[0] != "tag"
        assert first[1].isdigit()
        cats.add(int(first[1]))
        count = 1
        for row in r:
            assert len(row) == 4
            cats.add(int(row[1]))
            count += 1
    assert count == 124016
    assert cats <= {0,1,3,4,5}

def test_special_snapshot_counts():
    p = ROOT / "data/special2788/illustrious_tag_knowledge_base_2788.csv"
    counts = {}
    total = 0
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            total += 1
            counts[row["Layer"]] = counts.get(row["Layer"],0) + 1
    assert total == 2788
    assert counts == {"Core":759,"Extended":915,"Alias":778,"Semantic":336}

def test_semantic_bridge_has_336_unique_unmapped_rows():
    p = ROOT / "data/semantic/semantic_bridge_v1.csv"
    ids=set()
    rows=0
    with p.open("r",encoding="utf-8-sig",newline="") as f:
        for row in csv.DictReader(f):
            rows += 1
            assert row["semantic_id"] not in ids
            ids.add(row["semantic_id"])
            assert row["relation_type"] == "UNMAPPED"
            assert row["candidate_canonical"] == ""
    assert rows == 336

def test_verified_linkage_counts():
    p = ROOT / "data/derived/special2788_VERIFIED_LINKAGE.csv"
    counts={}
    resolved=0
    ambiguous=0
    with p.open("r",encoding="utf-8-sig",newline="") as f:
        for row in csv.DictReader(f):
            typ=row["SourceMatchType"]
            counts[typ]=counts.get(typ,0)+1
            if row["ChosenCanonicalTag"]:
                resolved += 1
            if typ=="alias_ambiguous_multiple":
                ambiguous += 1
    assert counts["canonical"] == 1674
    assert counts["alias_unique"] == 767
    assert counts["alias_ambiguous_curated"] == 2
    assert counts["alias_ambiguous_multiple"] == 9
    assert counts["semantic_unmapped"] == 336
    assert resolved == 2443
    assert ambiguous == 9
