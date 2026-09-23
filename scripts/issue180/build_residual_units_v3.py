#!/usr/bin/env python3
"""Group unresolved rows into deterministic, evidence-oriented research units."""
from __future__ import annotations
import json
import sys
from collections import defaultdict, Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _issue180_v3_common import *

UNITS = OUT / "research_units_v3.csv"
FIELDS = ["unit_id", "unit_type", "subject", "member_count", "member_ids/tags", "missing_evidence_type", "known_home_if_any", "priority", "status"]

def main() -> None:
    master = read_csv(OUT / "character_home_master_v3.csv")
    graph = read_csv(OUT / "structure_graph_v3.csv")
    members: dict[str, list[str]] = defaultdict(list)
    hints: dict[str, list[str]] = defaultdict(list)
    bases: dict[str, list[str]] = defaultdict(list)
    for e in graph:
        if e["relation_type"] == "MEMBER_OF": members[e["subject_key"]].append(e["object_key"])
        elif e["relation_type"] == "DISCOVERY_HINT" and e.get("review_state") == "CANDIDATE": hints[e["subject_key"]].append(e["object_key"])
        elif e["relation_type"] == "VARIANT_OF": bases[e["subject_key"]].append(e["object_key"])
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for r in master:
        if r["final_state"] != "HOME_UNRESOLVED":
            continue
        tag = r["canonical_tag"]
        fams = sorted(set(members.get(tag, [])))
        variant_bases = sorted(set(bases.get(tag, [])))
        discovery_hints = sorted(set(hints.get(tag, [])))
        if r["reason_code"] == "VARIANT_OFFICIALITY_MISSING" and variant_bases:
            key = "base:" + (variant_bases[0] if len(variant_bases) == 1 else "|".join(variant_bases))
        elif fams:
            key = "family:" + (fams[0] if len(fams) == 1 else "|".join(fams))
        elif discovery_hints:
            key = "discovery-hint:" + discovery_hints[0]
        else:
            key = "__UNGROUPED__"
        groups[(r["reason_code"], key)].append(r)
    units = []
    for (reason, subject), rows in sorted(groups.items()):
        tags = sorted(r["canonical_tag"] for r in rows)
        unit_type = {
            "FAMILY_HOME_MISSING": "FAMILY_AUTHORITY",
            "FAMILY_MEMBERSHIP_MISSING": "ROSTER_MEMBERSHIP",
            "BASE_IDENTITY_MISSING": "BASE_IDENTITY",
            "VARIANT_OFFICIALITY_MISSING": "VARIANT_OFFICIALITY",
            "DIRECT_AUTHORITY_MISSING": "DIRECT_AUTHORITY",
            "COPYRIGHT_ROOT_MISSING": "COPYRIGHT_ROOT",
            "IDENTITY_REVIEW_REQUIRED": "IDENTITY_REVIEW",
            "EVIDENCE_CONFLICT": "EVIDENCE_CONFLICT",
            "NO_SAFE_PATH": "NO_SAFE_PATH",
        }.get(reason, reason)
        uid = "ru3-" + sha256_text(unit_type + "\x1f" + subject + "\x1f" + "\n".join(tags))[:20]
        units.append({"unit_id": uid, "unit_type": unit_type, "subject": subject,
                      "member_count": str(len(tags)), "member_ids/tags": json.dumps(tags, ensure_ascii=False, separators=(",", ":")),
                      "missing_evidence_type": reason, "known_home_if_any": "",
                      "priority": "P1" if len(tags) >= 50 else ("P2" if len(tags) >= 5 else "P3"), "status": "OPEN"})
    write_csv(UNITS, units, FIELDS)
    summary = {"research_unit_count": len(units), "member_count": sum(int(r["member_count"]) for r in units),
               "unit_type_counts": dict(sorted(Counter(r["unit_type"] for r in units).items())),
               "reason_counts": dict(sorted(Counter(r["missing_evidence_type"] for r in units for _ in range(int(r["member_count"]))).items())),
               "unit_ids_deterministic": True}
    write_json(OUT / "research_units_summary_v3.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
