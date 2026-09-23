#!/usr/bin/env python3
"""Migrate independently cited v2 decisions and approved Issue #180 evidence to a unified ledger."""
from __future__ import annotations
import json
import csv
import io
import re
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _issue180_v3_common import *

LEDGER = OUT / "evidence_ledger_v3.csv"
FIELDS = ["evidence_id", "subject_type", "subject_key", "relation_type", "object_key", "authority_type", "evidence_basis", "source_url", "source_claim", "review_state", "source_provenance"]
SEED_FIELDS = ["subject_type", "subject_key", "relation_type", "object_key", "authority_type", "evidence_basis", "source_url", "source_claim", "review_state", "source_provenance", "migration_class"]

def build_foundation_seed() -> None:
    """One-time conversion of v2's validated foundation outputs into tracked evidence facts.

    The v2 master is comparison-only. Foundation facts are sourced from the v2 validated
    provenance table and rejoined to the exact second-review source rows/policy mapping.
    """
    artifact = ROOT / "artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW/MASTER_HOME_V2"
    family_path = artifact / "FAMILY_AUTHORITY_PROVENANCE_V2.csv"
    direct_path = artifact / "BASE_DIRECT_AUTHORITY_V2.csv"
    applied_path = artifact / "APPLIED_AUTHORITY_LEDGER_V2.csv"
    master_path = artifact / "CHARACTER_HOME_MASTER_V2.csv"
    for path in (family_path, direct_path, applied_path, master_path):
        if not path.exists():
            raise SystemExit(f"seed migration requires existing validated v2 checkpoint: {path}")
    family_rows = read_csv(family_path)
    second_review_paths = {
        "ROOT_REVIEW_BATCH_A_SECOND_REVIEW_V1.csv": artifact.parents[1] / "ROOT_REVIEW_BATCH_A_SECOND_REVIEW_V1.csv",
        "BATCH_A_REMAINING_7_SECOND_REVIEW_V2.csv": artifact.parents[1] / "BATCH_A_REMAINING_7_SECOND_REVIEW_V2.csv",
        "P1_P3_AUTHORITY_SECOND_REVIEW_V1.csv": artifact.parents[1] / "P1_P3_AUTHORITY_SECOND_REVIEW_V1.csv",
        "GLOBAL_EXACT_COPYRIGHT_SECOND_REVIEW_V1.csv": artifact.parents[1] / "GLOBAL_EXACT_COPYRIGHT_SECOND_REVIEW_V1.csv",
    }
    source_rows: dict[tuple[str, str, str], dict[str, str]] = {}
    for name, path in second_review_paths.items():
        if not path.exists():
            continue
        for r in read_csv(path):
            family = (r.get("family") or r.get("qualifier") or "").strip().lower()
            home = (r.get("candidate_root_hint") or r.get("proposed_root") or r.get("candidate_root") or "").strip()
            passed = r.get("second_review") == "PASS" or r.get("authority_decision") == "SECOND_REVIEW_PASS_RESEARCH_ONLY"
            if family and home and passed:
                source_rows[(name, family, home)] = r
    policy_path = ROOT / "docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    root_map = {str(k).lower(): str(v) for k, v in policy.get("root_policy_normalization", {}).items()}
    seed: dict[tuple[str, str, str], dict[str, str]] = {}
    family_basis_counts: dict[str, int] = {}
    for f in family_rows:
        if f.get("foundation_state") != "PASS_FASTPATH":
            continue
        family, home = f["family"].strip().lower(), f["candidate_home"].strip()
        basis, source_file = f.get("authority_basis", ""), f.get("source_file", "")
        if basis == "EXACT_COPYRIGHT_REVIEWED":
            src_name = "GLOBAL_EXACT_COPYRIGHT_SECOND_REVIEW_V1.csv"
            sr = source_rows.get((src_name, family, home))
            if not sr or sr.get("candidate_authority") != "EXACT_QUALIFIER_EQUALS_COPYRIGHT_TAG":
                raise SystemExit(f"exact qualifier review row not found/approved: {family} -> {home}")
            eb = "REVIEWED_QUALIFIER_COPYRIGHT"
            url = ""
            if sr.get("hint_state") != "EXACT_CATALOG_HINT" or sr.get("hint_count") != "1":
                raise SystemExit(f"exact qualifier review lacks a unique exact catalog hint: {family} -> {home}")
            claim = f"Second-reviewed Issue #180 exact qualifier review: the terminal family key {family!r} has one exact catalog root candidate {home!r}; hint_state=EXACT_CATALOG_HINT, hint_count=1, candidate_authority=EXACT_QUALIFIER_EQUALS_COPYRIGHT_TAG."
            prov = f"{source_file}; second-review={src_name}; key={family}; candidate_root_hint={home}; state=PASS"
        elif basis == "FIRST_PARTY_REVIEWED":
            matches = [(name, source_rows.get((name, family, home))) for name in second_review_paths]
            matches = [(name, r) for name, r in matches if r]
            if not matches:
                raise SystemExit(f"first-party second-review row not found: {family} -> {home}")
            src_name, sr = matches[0]
            url = (sr.get("official_source_url") or "").strip()
            claim = (sr.get("official_source_claim") or "").strip()
            if not is_valid_citation(url, claim):
                raise SystemExit(f"first-party review citation incomplete: {family} -> {home}")
            eb = "EXTERNAL_AUTHORITY"
            prov = f"{source_file}; second-review={src_name}; key={family}; candidate_root={home}; state=PASS"
        elif basis == "POLICY_ROOT_NORMALIZATION":
            if root_map.get(family) != home:
                raise SystemExit(f"policy root normalization is not an exact policy mapping: {family} -> {home}")
            eb = "ROOT_POLICY_NORMALIZATION"
            url = ""
            claim = f"Exact Issue #180 policy mapping root_policy_normalization[{family!r}]={home!r}; no prefix or approximate matching used."
            prov = f"docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json#root_policy_normalization:{family}"
        else:
            raise SystemExit(f"foundation basis requires revalidation and is not seedable: {family} ({basis})")
        fact = {"subject_type": "Family", "subject_key": family, "relation_type": "FAMILY_HOME",
                "object_key": home, "authority_type": basis, "evidence_basis": eb, "source_url": url,
                "source_claim": claim, "review_state": "VALIDATED", "source_provenance": prov,
                "migration_class": "SAFE_TO_MIGRATE"}
        seed[("Family", family, home)] = fact
        family_basis_counts[basis] = family_basis_counts.get(basis, 0) + 1

    # Direct foundation rows are migrated only where their row-level second-review provenance
    # still supplies a concrete external citation; applied HOME values are not consumed here.
    for d in read_csv(direct_path):
        url, claim = (d.get("evidence_url") or "").strip(), (d.get("evidence_claim") or "").strip()
        if not is_valid_citation(url, claim) or claim.lower().startswith("migrated from second-reviewed"):
            continue
        tag, home = d["canonical_tag"].strip(), d["home_copyright"].strip()
        seed[("Character", tag, home)] = {"subject_type": "Character", "subject_key": tag,
            "relation_type": "DIRECT_HOME", "object_key": home, "authority_type": d.get("authority_type", "V2_BASE_DIRECT"),
            "evidence_basis": "EXTERNAL_AUTHORITY", "source_url": url, "source_claim": claim,
            "review_state": "VALIDATED", "source_provenance": d.get("source_provenance", "BASE_DIRECT_AUTHORITY_V2.csv"),
            "migration_class": "SAFE_TO_MIGRATE"}
    write_csv(V3_SEED, (seed[k] for k in sorted(seed)), SEED_FIELDS)

    # Preserve the previously published, pre-repair gap exactly once so every former
    # migration loss can be individually accounted for after the adapter is repaired.
    prior = subprocess.run(["git", "show", "HEAD:docs/issue180/v3/reports/MIGRATION_COMPARISON_V3.csv"],
                           cwd=ROOT, capture_output=True, check=True)
    prior_text = prior.stdout.decode("utf-8-sig")
    prior_rows = list(csv.DictReader(io.StringIO(prior_text)))
    original_gap = [r for r in prior_rows if r.get("migration_state") == "V3_UNRESOLVED"]
    V3_PRE_REPAIR_GAP.parent.mkdir(parents=True, exist_ok=True)
    write_csv(V3_PRE_REPAIR_GAP, original_gap, list(prior_rows[0].keys()) if prior_rows else ["canonical_tag", "migration_state"])

    applied = read_csv(applied_path)
    master = read_csv(master_path)
    confirmed = {r["canonical_tag"]: r["home_copyright"] for r in master if r.get("final_state") == "HOME_CONFIRMED"}
    baseline = []
    for r in applied:
        tag = r["canonical_tag"]
        if tag not in confirmed or r["home_copyright"] != confirmed[tag]:
            continue
        baseline.append({"canonical_tag": tag, "home_copyright": confirmed[tag],
            "v2_resolution_route": r.get("authority_scope", ""), "authority_scope": r.get("authority_scope", ""),
            "authority_type": r.get("authority_type", ""), "source_provenance": r.get("source_provenance", ""),
            "evidence_url": r.get("evidence_url", ""), "evidence_claim": r.get("evidence_claim", ""),
            "family": r.get("family", ""), "base_character": ""})
    baseline_fields = ["canonical_tag", "home_copyright", "v2_resolution_route", "authority_scope", "authority_type", "source_provenance", "evidence_url", "evidence_claim", "family", "base_character"]
    write_csv(V3_BASELINE, sorted(baseline, key=lambda r: r["canonical_tag"]), baseline_fields)
    sources = [family_path, direct_path, applied_path, master_path, policy_path, *[p for p in second_review_paths.values() if p.exists()]]
    write_json(V3_MIGRATION_MANIFEST, {
        "schema_version": 1,
        "purpose": "v2-to-v3 lineage record; evidence seed is authority, baseline is comparison-only",
        "sources": [{"path": relpath(p), "sha256": sha256_file(p)} for p in sorted(set(sources))],
        "source_roles": {relpath(master_path): "comparison baseline only; never evidence",
                         relpath(applied_path): "lineage and state cross-check only; never HOME authority",
                         relpath(family_path): "validated foundation provenance index, cross-checked to second-review rows",
                         relpath(direct_path): "row-level citations only; uncited rows excluded"},
        "family_basis_counts": family_basis_counts,
        "seed_rows": len(seed), "baseline_confirmed_rows": len(baseline),
        "unsupported_or_non_fastpath_family_rows_excluded": sum(r.get("foundation_state") != "PASS_FASTPATH" for r in family_rows),
        "policy_mappings_are_exact_only": True,
    })
    print(json.dumps({"seed_rows": len(seed), "family_basis_counts": family_basis_counts,
                      "baseline_rows": len(baseline), "manifest": relpath(V3_MIGRATION_MANIFEST)}, indent=2))

def main() -> None:
    if "--seed-foundation" in sys.argv:
        build_foundation_seed()
        return
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
            authority: str, url: str, claim: str, provenance: str, basis: str = "EXTERNAL_AUTHORITY") -> str:
        valid_basis = ((basis == "EXTERNAL_AUTHORITY" and is_valid_citation(url, claim))
                       or (basis == "REVIEWED_QUALIFIER_COPYRIGHT" and relation == "FAMILY_HOME" and bool(claim))
                       or (basis == "ROOT_POLICY_NORMALIZATION" and relation == "FAMILY_HOME" and bool(claim))
                       or (basis == "APPROVED_REPO_EVIDENCE" and (provenance.startswith("docs/issue180/evidence/") or provenance.startswith("membership derived from ")) and len(claim) >= 35)
                       or (basis == "REVIEWED_VARIANT_AUTHORITY" and relation == "VARIANT_OF" and is_valid_citation(url, claim)))
        if not valid_basis:
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
        eid = evidence_id(subject_type, subject, relation, object_key, authority + ":" + basis, url, claim)
        if eid in rows:
            provenance_set = set(rows[eid]["source_provenance"].split(" | "))
            provenance_set.add(provenance)
            rows[eid]["source_provenance"] = " | ".join(sorted(x for x in provenance_set if x))
        else:
            rows[eid] = {"evidence_id": eid, "subject_type": subject_type, "subject_key": subject,
                         "relation_type": relation, "object_key": object_key, "authority_type": authority, "evidence_basis": basis,
                         "source_url": url.strip(), "source_claim": " ".join(claim.split()),
                         "review_state": "VALIDATED", "source_provenance": provenance}
        return eid

    family_evidence: dict[str, list[str]] = {}
    alias_to_roots: dict[str, set[str]] = {}
    for root in copyrights:
        for alias in [root.get("canonical_tag", ""), *(root.get("aliases", "") or "").split("|")]:
            if alias.strip(): alias_to_roots.setdefault(alias.strip().lower(), set()).add(root["canonical_tag"])
    # Foundation seed was derived from reviewed v2 source records/policy, not the v2 master.
    policy = json.loads((ROOT / "docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json").read_text(encoding="utf-8"))
    root_map = {str(k).lower(): str(v) for k, v in policy.get("root_policy_normalization", {}).items()}
    for s in read_csv(V3_SEED):
        basis = s["evidence_basis"]
        if basis == "ROOT_POLICY_NORMALIZATION" and root_map.get(s["subject_key"].lower()) != s["object_key"]:
            raise SystemExit(f"seed violates exact root policy mapping: {s['subject_key']} -> {s['object_key']}")
        eid = add(s["subject_type"], s["subject_key"], s["relation_type"], s["object_key"],
                  s["authority_type"], s["source_url"], s["source_claim"], s["source_provenance"], basis)
        if eid and s["relation_type"] == "FAMILY_HOME":
            family_evidence.setdefault(s["subject_key"], []).append(eid)
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
            base = d.get("base_character", "")
            if base:
                eid = add("Character", key, "VARIANT_OF", base, authority, url, claim, provenance, "REVIEWED_VARIANT_AUTHORITY")
                migrated_decision_count += bool(eid)
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
            if name == "direct_official_character_roster_batch05.csv" and tag and direct_home:
                claim = f"Approved Issue #180 direct roster evidence row {line} explicitly pairs Character tag {tag!r} with canonical HOME Copyright {direct_home!r}; authority_type={r.get('evidence_type','')}."
                add("Character", tag, "DIRECT_HOME", direct_home, authority, url, claim,
                    f"{relpath(path)}:{line}; exact reviewed tag-to-root row", "APPROVED_REPO_EVIDENCE")
                continue
            if name == "splatoon_official_roster_v1.csv":
                base = (r.get("canonical_base") or "").strip()
                canonical = f"{base}_(splatoon)"
                roots = alias_to_roots.get(home.lower(), set()) if home else set()
                if canonical in char_set and len(roots) == 1:
                    normalized_home = next(iter(roots))
                    claim = f"Approved Issue #180 curated Splatoon character roster row {line} names canonical base {base!r}; exact Issue #70 catalog alias {home!r} resolves uniquely to Copyright root {normalized_home!r}."
                    add("Character", canonical, "DIRECT_HOME", normalized_home, authority, url, claim,
                        f"{relpath(path)}:{line}; exact canonical_base match", "APPROVED_REPO_EVIDENCE")
                continue
            if tag and direct_home and (r.get("evidence_url") or "").strip():
                add("Character", tag, "DIRECT_HOME", direct_home, authority, url,
                    r.get("evidence_claim") or r.get("scope_note") or authority, f"{relpath(path)}:{line}")

    # The applied v2 ledger is deliberately not read by the active v3 pipeline.
    # Its row-level provenance has already been captured in the tracked comparison baseline.
    lineage_links = 0

    # A reviewed FAMILY_QUALIFIER authority plus the exact catalog qualifier establishes membership;
    # bare parsed candidates without such a cited family decision remain CANDIDATE only.
    policy = json.loads((ROOT / "docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json").read_text(encoding="utf-8"))
    excluded_families = set(policy["attribute_families"]) | set(policy["variant_qualifier_families"]) | set(policy["non_home_families"])
    broad_families = set(policy["broad_families"])
    ordinal = re.compile(policy["ordinal_costume_regex"])
    for family, eids in sorted(family_evidence.items()):
        home_rows = [rows[e] for e in sorted(set(eids)) if e in rows]
        for member in sorted(set(family_members.get(family, []))):
            tag = member
            suffix = f"_({family})"
            nested = tag.lower().endswith(suffix.lower()) and tag[:-len(suffix)].endswith(")")
            if family in excluded_families or family in broad_families or ordinal.match(family) or nested:
                continue
            for h in home_rows:
                add("Character", member, "MEMBER_OF", family,
                    "VALIDATED_FAMILY_QUALIFIER_MEMBERSHIP", h["source_url"],
                    f"Issue #70 accepted Character catalog tag {member!r} has exact final qualifier {family!r}; v2 family fastpath policy excludes nested/attribute/broad/non-home qualifiers.",
                    f"membership derived from {h['evidence_id']} + {relpath(CATALOG)}",
                    "APPROVED_REPO_EVIDENCE")

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
        "evidence_basis_counts": dict(sorted(__import__("collections").Counter(r["evidence_basis"] for r in ordered).items())),
        "external_source_url_count": len({r["source_url"] for r in ordered if r["evidence_basis"] == "EXTERNAL_AUTHORITY" and r["source_url"]}),
        "rejected_candidates": rejected,
        "source_rule": "Decision CSV values are not evidence by themselves; evidence basis is explicit and repository seed facts carry source hashes/provenance.",
        "applied_authority_ledger_used_as": "provenance cross-check only; never a HOME authority source",
        "v2_applied_provenance_exists": False,
        "v2_applied_provenance_links": lineage_links,
        "v2_decision_self_certification": False,
    }
    write_json(OUT / "evidence_ledger_summary_v3.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
