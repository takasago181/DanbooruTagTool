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
REVIEWS = ROOT / "docs/issue180/v3/research_unit_terminal_reviews_v3.csv"
CLOSURE = ROOT / "docs/issue180/v3/reports/RESEARCH_UNIT_CLOSURE_SWEEP_V3.csv"
FIELDS = ["unit_id", "unit_type", "subject", "member_count", "member_ids/tags", "missing_evidence_type", "known_home_if_any", "priority", "status"]
REVIEW_FIELDS = {"unit_id", "member_ids_sha256", "terminal_status", "authority_source", "source_claim", "review_provenance"}
CLOSURE_FIELDS = ["unit_id", "member_ids_sha256", "classification", "examined_paths", "candidate_roots", "rejection_reason", "terminal_reason"]
TERMINAL_STATUSES = {"RESOLVED", "PARTIALLY_RESOLVED", "NO_SAFE_EVIDENCE", "POLICY_BLOCKED", "IDENTITY_BLOCKED", "SUPERSEDED_BY_NEW_UNIT"}

def member_hash(tags: list[str]) -> str:
    return sha256_text("\n".join(sorted(tags)))

def apply_terminal_reviews(units: list[dict[str, str]]) -> None:
    if not REVIEWS.exists():
        return
    reviews = read_csv(REVIEWS)
    if reviews and not REVIEW_FIELDS.issubset(reviews[0]):
        raise SystemExit("terminal review ledger schema is incomplete")
    by_id = {r["unit_id"]: r for r in reviews}
    if len(by_id) != len(reviews):
        raise SystemExit("duplicate Research Unit terminal review IDs")
    current = {u["unit_id"]: u for u in units}
    origin_rows = {r["canonical_tag"]: r for r in read_csv(ORIGIN)}
    for uid, review in by_id.items():
        unit = current.get(uid)
        if not unit:
            if review["terminal_status"] == "SUPERSEDED_BY_NEW_UNIT":
                if not review["authority_source"].startswith("docs/issue180/") or len(review["source_claim"].strip()) < 40 or len(review["review_provenance"].strip()) < 20:
                    raise SystemExit(f"supersession record lacks grounded provenance: {uid}")
                continue
            raise SystemExit(f"stale terminal review references absent unit: {uid}; record supersession explicitly")
        tags = json.loads(unit["member_ids/tags"])
        if review["member_ids_sha256"] != member_hash(tags):
            raise SystemExit(f"terminal review member set changed: {uid}; re-review required")
        if review["terminal_status"] not in TERMINAL_STATUSES:
            raise SystemExit(f"invalid terminal status for {uid}: {review['terminal_status']}")
        if not review["authority_source"].startswith("docs/issue180/") or len(review["source_claim"].strip()) < 40 or len(review["review_provenance"].strip()) < 20:
            raise SystemExit(f"terminal review lacks grounded source/claim/notes: {uid}")
        if review["terminal_status"] == "IDENTITY_BLOCKED":
            for tag in tags:
                origin = origin_rows.get(tag, {})
                if origin.get("origin_class") != "UNKNOWN" or origin.get("row_id", "") not in review["review_provenance"]:
                    raise SystemExit(f"IDENTITY_BLOCKED is not supported by an exact #179 UNKNOWN row: {uid} / {tag}")
        unit["status"] = review["terminal_status"]

def classify_open_units(units: list[dict[str, str]], graph: list[dict[str, str]], ledger: list[dict[str, str]]) -> list[dict[str, str]]:
    """Deterministically classify every current OPEN unit without promoting candidates to authority."""
    graph_by_subject: dict[str, list[dict[str, str]]] = defaultdict(list)
    validated_by_subject: dict[str, list[dict[str, str]]] = defaultdict(list)
    for edge in graph:
        graph_by_subject[edge["subject_key"]].append(edge)
    for evidence in ledger:
        if evidence.get("review_state") == "VALIDATED":
            validated_by_subject[evidence["subject_key"]].append(evidence)
    policy = json.loads((ROOT / "docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json").read_text(encoding="utf-8"))
    blocked_family_keys = {
        *("family:" + key for field in ("attribute_families", "broad_families", "non_home_families", "variant_qualifiers")
          for key in policy.get(field, [])),
    }
    origins = {r["canonical_tag"]: r for r in read_csv(ORIGIN)}
    master = {r["canonical_tag"]: r for r in read_csv(OUT / "character_home_master_v3.csv")}
    closures = []
    for unit in units:
        if unit["status"] != "OPEN":
            continue
        tags = json.loads(unit["member_ids/tags"])
        candidates: set[str] = set()
        direct_homes: set[str] = set()
        admissible_edges = []
        for tag in tags:
            for edge in graph_by_subject.get(tag, []):
                if edge["relation_type"] in {"MEMBER_OF", "DISCOVERY_HINT", "VARIANT_OF"}:
                    candidates.add(edge["object_key"])
            for evidence in validated_by_subject.get(tag, []):
                if evidence["relation_type"] == "DIRECT_HOME":
                    direct_homes.add(evidence["object_key"])
                    admissible_edges.append(evidence["evidence_id"])
                elif evidence["relation_type"] in {"MEMBER_OF", "VARIANT_OF"}:
                    admissible_edges.append(evidence["evidence_id"])
        # Validated-family roots are only candidates here; resolver output remains authoritative.
        families = {e["object_key"] for tag in tags for e in graph_by_subject.get(tag, [])
                    if e["relation_type"] == "MEMBER_OF"}
        family_homes = {e["object_key"] for e in ledger if e.get("review_state") == "VALIDATED"
                        and e["relation_type"] == "FAMILY_HOME" and e["subject_key"] in families}
        candidates.update(family_homes)
        base_keys = {e["object_key"] for tag in tags for e in graph_by_subject.get(tag, [])
                     if e["relation_type"] == "VARIANT_OF"}
        base_homes = {master[b]["home_copyright"] for b in base_keys
                      if b in master and master[b]["final_state"] == "HOME_CONFIRMED"}
        candidates.update(base_homes)
        distinct_homes = direct_homes | family_homes | base_homes
        all_unknown = bool(tags) and all(origins.get(t, {}).get("origin_class") == "UNKNOWN" for t in tags)
        if len(distinct_homes) > 1:
            classification, reject, terminal = "CONFLICT_REVIEW", "validated paths point to distinct HOME roots", "EVIDENCE_CONFLICT"
        elif len(distinct_homes) == 1 and admissible_edges:
            classification, reject, terminal = "AUTO_RESOLVE_STRUCTURE", "a validated relation path exists; resolver/master reconciliation required", ""
        elif unit["subject"] in blocked_family_keys:
            classification, reject, terminal = "POLICY_BLOCKED", "exact family key is explicitly blocked by frozen Issue #180 policy", "POLICY_BLOCKED"
        elif all_unknown:
            classification, reject, terminal = "IDENTITY_BLOCKED", "all members have exact #179 UNKNOWN origin rows", "IDENTITY_REVIEW_REQUIRED"
        elif not candidates:
            classification, reject, terminal = "STRUCTURAL_NO_SAFE_PATH", "no validated direct/family/variant path, no family or discovery candidate, and no candidate Copyright root in current structure", "NO_SAFE_EVIDENCE"
        else:
            classification, reject, terminal = "BATCH_AUTHORITY_RESEARCH", "candidate family/base/discovery structure exists but is candidate-only or lacks validated authority", ""
        closures.append({"unit_id": unit["unit_id"], "member_ids_sha256": member_hash(tags),
                         "classification": classification,
                         "examined_paths": "validated DIRECT_HOME; validated FAMILY_HOME+MEMBER_OF; validated VARIANT_OF+confirmed base HOME; approved evidence ledger; candidate MEMBER_OF/DISCOVERY_HINT/VARIANT_OF; exact #179 origin rows",
                         "candidate_roots": json.dumps(sorted(candidates), ensure_ascii=False, separators=(",", ":")),
                         "rejection_reason": reject, "terminal_reason": terminal})
    write_csv(CLOSURE, closures, CLOSURE_FIELDS)
    return closures

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
    apply_terminal_reviews(units)
    closures = classify_open_units(units, graph, read_csv(OUT / "evidence_ledger_v3.csv"))
    closure_counts = dict(sorted(Counter(r["classification"] for r in closures).items()))
    write_csv(UNITS, units, FIELDS)
    summary = {"research_unit_count": len(units), "member_count": sum(int(r["member_count"]) for r in units),
               "unit_type_counts": dict(sorted(Counter(r["unit_type"] for r in units).items())),
               "unit_status_counts": dict(sorted(Counter(r["status"] for r in units).items())),
               "open_unit_count": sum(r["status"] == "OPEN" for r in units),
               "reason_counts": dict(sorted(Counter(r["missing_evidence_type"] for r in units for _ in range(int(r["member_count"]))).items())),
               "unit_ids_deterministic": True, "open_closure_classification_counts": closure_counts,
               "open_closure_classification_rows": len(closures)}
    write_json(OUT / "research_units_summary_v3.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
