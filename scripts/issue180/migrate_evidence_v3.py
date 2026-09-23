#!/usr/bin/env python3
"""Migrate independently cited v2 decisions and approved Issue #180 evidence to a unified ledger."""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _issue180_v3_common import *

LEDGER = OUT / "evidence_ledger_v3.csv"
FIELDS = ["evidence_id", "subject_type", "subject_key", "relation_type", "object_key", "authority_type", "source_url", "source_claim", "review_state", "source_provenance"]

def main() -> None:
    characters, copyrights, char_by = load_catalog()
    root_set = {r["canonical_tag"] for r in copyrights}
    char_set = set(char_by)
    candidates = read_csv(OUT / "structure_graph_v3.csv")
    family_members: dict[str, list[str]] = {}
    for r in candidates:
        if r["relation_type"] == "MEMBER_OF":
            family_members.setdefault(r["object_key"], []).append(r["subject_key"])

    rows: dict[str, dict[str, str]] = {}
    migrated_decision_count = 0
    rejected: dict[str, int] = {}

    def add(subject_type: str, subject: str, relation: str, object_key: str,
            authority: str, url: str, claim: str, provenance: str) -> str:
        if not is_valid_citation(url, claim):
            rejected["citation_missing_or_weak"] = rejected.get("citation_missing_or_weak", 0) + 1
            return ""
        if relation in {"DIRECT_HOME", "FAMILY_HOME"} and object_key not in root_set:
            rejected["copyright_root_missing"] = rejected.get("copyright_root_missing", 0) + 1
            return ""
        if relation == "DIRECT_HOME" and subject not in char_set:
            rejected["character_missing"] = rejected.get("character_missing", 0) + 1
            return ""
        if relation == "VARIANT_OF" and (subject not in char_set or object_key not in char_set):
            rejected["variant_endpoint_missing"] = rejected.get("variant_endpoint_missing", 0) + 1
            return ""
        eid = evidence_id(subject_type, subject, relation, object_key, authority, url, claim)
        if eid in rows:
            provenance_set = set(rows[eid]["source_provenance"].split(" | "))
            provenance_set.add(provenance)
            rows[eid]["source_provenance"] = " | ".join(sorted(x for x in provenance_set if x))
        else:
            rows[eid] = {"evidence_id": eid, "subject_type": subject_type, "subject_key": subject,
                         "relation_type": relation, "object_key": object_key, "authority_type": authority,
                         "source_url": url.strip(), "source_claim": " ".join(claim.split()),
                         "review_state": "VALIDATED", "source_provenance": provenance}
        return eid

    family_evidence: dict[str, list[str]] = {}
    decisions = load_decisions()
    for d in decisions:
        if d.get("validation_state") != "PASS":
            continue
        scope, key, home = d.get("scope", ""), d.get("key", ""), d.get("home_copyright", "")
        authority, url, claim = d.get("authority_type", ""), d.get("evidence_url", ""), d.get("evidence_claim", "")
        provenance = f"{d['_source_file']}:{d['_source_line']}"
        if scope == "DIRECT_CHARACTER":
            eid = add("Character", key, "DIRECT_HOME", home, authority, url, claim, provenance)
        elif scope == "FAMILY_QUALIFIER":
            eid = add("Family", key, "FAMILY_HOME", home, authority, url, claim, provenance)
            if eid:
                family_evidence.setdefault(key, []).append(eid)
        elif scope == "VARIANT_CHARACTER":
            eid = add("Character", key, "DIRECT_HOME", home, authority, url, claim, provenance)
            if eid:
                migrated_decision_count += 1
            base = d.get("base_character", "")
            if base:
                add("Character", key, "VARIANT_OF", base, authority, url, claim, provenance)
            continue
        else:
            continue
        migrated_decision_count += bool(eid)

    # Approved root evidence files can establish a HOME for the family named in that evidence row.
    # Generic source catalogs without an exact family/object mapping are intentionally skipped.
    for path in sorted(EVIDENCE_DIR.glob("*.csv")):
        name = path.name
        if name == "ISSUE179_ORIGIN_HANDOFF_V1.csv":
            continue
        for line, r in enumerate(read_csv(path), start=2):
            family = r.get("family", "").strip()
            home = (r.get("home_copyright") or "").strip()
            state = (r.get("root_review") or "").strip()
            url = (r.get("evidence_url") or "").strip()
            claim = (r.get("scope_note") or r.get("evidence_claim") or "").strip()
            authority = (r.get("evidence_type") or "").strip()
            if family and home and state == "PASS":
                eid = add("Family", family, "FAMILY_HOME", home, authority, url, claim, f"{relpath(path)}:{line}")
                if eid:
                    family_evidence.setdefault(family, []).append(eid)
            tag, direct_home = (r.get("canonical_tag") or "").strip(), (r.get("home_copyright") or "").strip()
            if tag and direct_home and (r.get("evidence_url") or "").strip():
                add("Character", tag, "DIRECT_HOME", direct_home, authority, url,
                    r.get("evidence_claim") or r.get("scope_note") or authority, f"{relpath(path)}:{line}")

    # Preserve links to v2 applied provenance for auditability, but never import its HOME values
    # or generated rows as authority/evidence.
    lineage_links = 0
    if V2_APPLIED.exists():
        applied_rows = read_csv(V2_APPLIED)
        for evidence in rows.values():
            for old in applied_rows:
                same_target = old.get("home_copyright", "") == evidence.get("object_key", "")
                relates = (evidence["relation_type"] == "DIRECT_HOME" and old.get("canonical_tag", "") == evidence["subject_key"])
                relates |= (evidence["relation_type"] == "FAMILY_HOME" and old.get("family", "") == evidence["subject_key"])
                if same_target and relates and old.get("source_provenance"):
                    evidence["source_provenance"] += " | v2-applied:" + old.get("source_provenance", "")
                    lineage_links += 1

    # A reviewed FAMILY_QUALIFIER authority plus the exact catalog qualifier establishes membership;
    # bare parsed candidates without such a cited family decision remain CANDIDATE only.
    for family, eids in sorted(family_evidence.items()):
        home_rows = [rows[e] for e in sorted(set(eids)) if e in rows]
        for member in sorted(set(family_members.get(family, []))):
            for h in home_rows:
                add("Character", member, "MEMBER_OF", family,
                    "VALIDATED_FAMILY_QUALIFIER_MEMBERSHIP", h["source_url"],
                    f"Reviewed family authority: {h['source_claim']} Exact catalog terminal qualifier associates this Character with family {family}.",
                    f"membership derived from {h['evidence_id']} + {relpath(CATALOG)}")

    ordered = [rows[k] for k in sorted(rows)]
    write_csv(LEDGER, ordered, FIELDS)
    # The final research graph is the union of candidate structure and evidence-validated edges.
    graph_fields = ["subject_type", "subject_key", "relation_type", "object_type", "object_key", "review_state", "evidence_id", "derivation"]
    graph_rows = read_csv(OUT / "structure_graph_v3.csv")
    for e in ordered:
        graph_rows.append({"subject_type": e["subject_type"], "subject_key": e["subject_key"],
                           "relation_type": e["relation_type"],
                           "object_type": "Copyright" if e["relation_type"] in {"DIRECT_HOME", "FAMILY_HOME"} else ("Family" if e["relation_type"] == "MEMBER_OF" else "Character"),
                           "object_key": e["object_key"], "review_state": "VALIDATED",
                           "evidence_id": e["evidence_id"], "derivation": "independently cited validated Evidence Ledger relation"})
    graph_rows.sort(key=lambda r: (r["subject_type"], r["subject_key"], r["relation_type"], r["object_key"], r["review_state"], r["evidence_id"]))
    write_csv(OUT / "structure_graph_v3.csv", graph_rows, graph_fields)
    summary = {
        "ledger_rows": len(ordered), "validated_decision_facts": migrated_decision_count,
        "relation_counts": dict(sorted(__import__("collections").Counter(r["relation_type"] for r in ordered).items())),
        "rejected_candidates": rejected,
        "source_rule": "Decision CSV values are not evidence by themselves; rows enter VALIDATED only with an independently cited URL and substantive claim or approved evidence-file citation.",
        "applied_authority_ledger_used_as": "provenance cross-check only; never a HOME authority source",
        "v2_applied_provenance_exists": V2_APPLIED.exists(),
        "v2_applied_provenance_links": lineage_links,
        "v2_decision_self_certification": False,
    }
    write_json(OUT / "evidence_ledger_summary_v3.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
