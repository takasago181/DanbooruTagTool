#!/usr/bin/env python3
# Non-mutating audit helper for Issue #70 semantic review.
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/issue70/data/source/issue70_translation_source_with_relations.csv"
RESULTS = ROOT / "docs/issue70/data/runtime/issue70_translation_results.csv"
OUTDIR = ROOT / "artifacts/issue70-semantic-risk-scan"
OUTDIR.mkdir(parents=True, exist_ok=True)

JP_RE = re.compile(r"[ぁ-んァ-ヶ一-龯々〆ヵヶ]")
PAREN_RE = re.compile(r"\([^)]*\)")


def split_pipe(value: str):
    return [x.strip() for x in (value or "").split("|") if x.strip()]


def has_jp(value: str) -> bool:
    return bool(JP_RE.search(value or ""))


def canonical_surface(tag: str) -> str:
    return (tag or "").replace("_", " ")


def load_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


source_rows = load_csv(SOURCE)
result_rows = load_csv(RESULTS)
source_by_id = {r["row_id"]: r for r in source_rows}

if len(source_rows) != 92739 or len(result_rows) != 92739:
    raise SystemExit(f"row-count mismatch source={len(source_rows)} results={len(result_rows)}")

combined = []
display_groups = defaultdict(list)
for r in result_rows:
    s = source_by_id.get(r["row_id"])
    if not s:
        raise SystemExit(f"missing source row: {r['row_id']}")
    for key in ("canonical_tag", "category"):
        if r[key] != s[key]:
            raise SystemExit(f"identity mismatch {r['row_id']} field={key}")
    row = {**s, **{f"result_{k}": v for k, v in r.items()}}
    combined.append(row)
    display_groups[(s["category_name"], r["display_ja"].strip())].append(r["row_id"])

collision_ids = set()
for (_, display), ids in display_groups.items():
    if display and len(ids) > 1:
        collision_ids.update(ids)

flag_counts = Counter()
category_counts = Counter()
status_counts = Counter()
candidates = []

for row in combined:
    rid = row["row_id"]
    category = row["category_name"]
    canonical = row["canonical_tag"]
    display = row["result_display_ja"].strip()
    search = row["result_search_ja"].strip()
    status = row["result_translation_status"].strip()
    note = row["result_translation_note"].strip()
    post_count = int(row.get("post_count") or 0)
    search_terms = split_pipe(search)
    rejected = set(split_pipe(row.get("existing_rejected_ja", "")))
    candidate_evidence = set(split_pipe(row.get("existing_candidate_ja", "")))
    search_evidence = set(split_pipe(row.get("existing_search_ja", "")))
    display_evidence = set(split_pipe(row.get("existing_display_ja", "")))
    evidence_all = candidate_evidence | search_evidence | display_evidence

    flags = []
    score = 0

    if status == "REVIEW_REQUIRED":
        flags.append("REVIEW_REQUIRED")
        score += 100

    if display in rejected:
        flags.append("DISPLAY_EQUALS_REJECTED")
        score += 90

    rejected_in_search = sorted(set(search_terms) & rejected)
    if rejected_in_search:
        flags.append("SEARCH_CONTAINS_REJECTED")
        score += 90

    if rid in collision_ids:
        flags.append("DISPLAY_COLLISION")
        score += 65

    if len(search_terms) >= 5:
        flags.append("SEARCH_MANY_TERMS")
        score += 10

    extra_symbolic = [t for t in search_terms if t != display and ("♂" in t or "♀" in t)]
    if extra_symbolic:
        flags.append("SEARCH_SYMBOLIC_VARIANT")
        score += 20

    long_extra = [t for t in search_terms if t != display and len(t) >= 12 and display not in t and t not in display]
    if long_extra:
        flags.append("SEARCH_LONG_EXTRA_TERM")
        score += 8

    if category in {"Character", "Copyright"} and not has_jp(display) and any(has_jp(x) for x in evidence_all):
        flags.append("JP_EVIDENCE_BUT_NONJP_DISPLAY")
        score += 40

    if category == "Artist" and has_jp(display) and display not in evidence_all:
        flags.append("ARTIST_JP_DISPLAY_NOT_IN_SOURCE_EVIDENCE")
        score += 30

    if category == "Character":
        related_raw = row.get("related_copyright_candidates", "") or "[]"
        try:
            related = json.loads(related_raw)
        except json.JSONDecodeError:
            related = []
            flags.append("RELATION_JSON_INVALID")
            score += 80
        if not related:
            flags.append("CHAR_NO_COPYRIGHT_CONTEXT")
            score += 25
        elif post_count >= 1000:
            top_cov = float(related[0].get("character_coverage") or 0.0)
            if top_cov < 0.50:
                flags.append("CHAR_WEAK_TOP_COPYRIGHT_CONTEXT")
                score += 20

    if PAREN_RE.search(canonical) and "（" not in display and "(" not in display:
        flags.append("CANONICAL_DISAMBIG_NOT_VISIBLE")
        score += 12

    if post_count >= 10000:
        impact_tier = "P0"
    elif post_count >= 1000:
        impact_tier = "P1"
    elif post_count >= 100:
        impact_tier = "P2"
    else:
        impact_tier = "P3"

    if flags:
        for f in flags:
            flag_counts[f] += 1
        category_counts[category] += 1
        status_counts[status] += 1
        candidates.append({
            "row_id": rid,
            "canonical_tag": canonical,
            "category": category,
            "post_count": post_count,
            "impact_tier": impact_tier,
            "risk_score": score,
            "risk_flags": "|".join(flags),
            "display_ja": display,
            "search_ja": search,
            "translation_status": status,
            "translation_note": note,
            "existing_display_ja": row.get("existing_display_ja", ""),
            "existing_search_ja": row.get("existing_search_ja", ""),
            "existing_candidate_ja": row.get("existing_candidate_ja", ""),
            "existing_rejected_ja": row.get("existing_rejected_ja", ""),
            "verified_aliases": row.get("verified_aliases", ""),
            "related_copyright_candidates": row.get("related_copyright_candidates", ""),
        })

candidates.sort(key=lambda r: (-r["risk_score"], -r["post_count"], r["row_id"]))

fields = list(candidates[0].keys()) if candidates else []
with (OUTDIR / "audit_candidates.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(candidates)

with (OUTDIR / "top_candidates.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(candidates[:1000])

summary = {
    "source_rows": len(source_rows),
    "result_rows": len(result_rows),
    "candidate_rows": len(candidates),
    "flag_counts": dict(flag_counts.most_common()),
    "candidate_category_counts": dict(category_counts),
    "candidate_status_counts": dict(status_counts),
    "policy": {
        "production_mutation": False,
        "post_count_role": "priority_only_not_correctness",
        "review_required": "always_candidate",
        "display_and_search": "audited_separately",
    },
}
with (OUTDIR / "summary.json").open("w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(json.dumps(summary, ensure_ascii=False, indent=2))
