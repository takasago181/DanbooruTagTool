#!/usr/bin/env python3
"""Apply one deterministic offline authority join to the frozen #216 cohort.

The join consumes only validated Issue #180 family/root mappings, accepted exact
#216 source memberships, and validated exact variant/base rows. Candidate hints,
post counts, popularity, co-occurrence, and fuzzy identity matching are excluded.
"""
from __future__ import annotations

import argparse
import csv
import os
import tempfile
from collections import defaultdict
from pathlib import Path

from authority_coverage import (
    BASELINE_SIZE, DECISION_FIELDS, MEMBER_FIELDS, SOURCE_FIELDS,
    deterministic_source_id, read_csv, validate,
)

ROOT = Path(__file__).resolve().parents[2]
ISSUE216 = ROOT / "docs/issue216"
ISSUE180 = ROOT / "docs/issue180"
COHORT = ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv"
SOURCES = ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv"
MEMBERS = ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv"
DECISIONS = ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv"
ROOTS = ISSUE216 / "COPYRIGHT_ROOTS_V1.csv"
SEED = ISSUE180 / "v3/migrated_evidence_seed_v3.csv"
ROOT_MAP = ISSUE180 / "evidence/exact_root_semantic_authority_batch02.csv"
VARIANTS = ISSUE180 / "autonomous/decisions/variants_verified_v4.csv"
REVIEW_DATE = "2026-09-30"
REVIEWER = "Codex deterministic cohort-wide authority join"
ISSUE180_URL = "https://github.com/takasago181/DanbooruTagTool/issues/180"


def write_atomic(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    temp_path: Path | None = None
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=path.parent,
                                     prefix=path.name + ".", suffix=".tmp", delete=False) as stream:
        temp_path = Path(stream.name)
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def build() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], dict[str, int]]:
    validate(COHORT, SOURCES, MEMBERS, DECISIONS, expected_size=BASELINE_SIZE, roots_path=ROOTS)
    cohort = read_csv(COHORT)
    sources = read_csv(SOURCES)
    members = read_csv(MEMBERS)
    decisions = read_csv(DECISIONS)
    roots = {row["copyright_canonical"] for row in read_csv(ROOTS)}
    cohort_tags = {row["canonical_character"] for row in cohort}
    decision_by_tag = {row["canonical_character"]: row for row in decisions}
    source_by_id = {row["source_id"]: row for row in sources}
    open_tags = {tag for tag, row in decision_by_tag.items() if row["research_state"] == "UNRESEARCHED"}

    # Every mapping comes from a validated Issue #180 Family -> FAMILY_HOME row.
    family_homes: dict[str, set[str]] = defaultdict(set)
    family_evidence: dict[tuple[str, str], dict[str, str]] = {}
    for row in read_csv(SEED):
        if (row.get("subject_type") == "Family" and row.get("relation_type") == "FAMILY_HOME"
                and row.get("review_state") == "VALIDATED"):
            family = row["subject_key"].strip()
            home = row["object_key"].strip()
            if family and home:
                family_homes[family].add(home)
                family_evidence[(family, home)] = row
    for row in read_csv(ROOT_MAP):
        if row.get("root_review") == "PASS":
            family = row["family"].strip()
            home = row["home_copyright"].strip()
            if family and home:
                family_homes[family].add(home)
                family_evidence.setdefault((family, home), {
                    "source_url": row.get("evidence_url", ""),
                    "source_claim": row.get("scope_note", ""),
                    "evidence_basis": row.get("evidence_type", ""),
                })

    # A deterministic candidate row carries exact provenance and optional HOME priority.
    candidates: dict[str, list[dict[str, str]]] = defaultdict(list)
    qualifier_candidates = 0
    for tag in sorted(open_tags):
        for family, homes in sorted(family_homes.items()):
            suffix = f"_({family})"
            if (len(homes) != 1 or not tag.endswith(suffix)
                    or ")_(" in tag[:-len(suffix)]):
                continue
            home = next(iter(homes))
            if home not in roots:
                continue
            evidence = family_evidence[(family, home)]
            url = evidence.get("source_url", "").strip() or ISSUE180_URL
            owner = "DanbooruTagTool Issue #180 validated family/root evidence"
            scope = (f"Exact terminal canonical Copyright qualifier _({family}) only; "
                     "nested qualifier chains excluded; HOME uses the validated Issue #180 Family/FAMILY_HOME mapping.")
            source_id = deterministic_source_id(url, owner, scope)
            candidates[tag].append({
                "home": home, "kind": "QUALIFIER", "source_id": source_id, "url": url,
                "owner": owner, "scope": scope, "claim": (
                    f"Validated Issue #180 family mapping {family} -> {home}; exact terminal tag qualifier "
                    f"_({family}) on canonical Character {tag}. {evidence.get('source_claim', evidence.get('evidence_basis', ''))}"
                ), "surface": tag,
                "mapping_evidence": f"Exact canonical terminal qualifier _({family}); validated FAMILY_HOME mapping in migrated_evidence_seed_v3.csv.",
                "tier": "", "basis": "",
            })
            qualifier_candidates += 1

    # Reuse accepted exact curated/official memberships as a cohort-wide join.
    accepted: dict[str, list[tuple[dict[str, str], dict[str, str]]]] = defaultdict(list)
    for member in members:
        source = source_by_id.get(member["source_id"])
        tag = member["canonical_character"]
        if (source and tag in cohort_tags and tag in open_tags
                and source["source_status"] == "ACCEPTED"
                and member["mapping_status"] == "EXACT_COVERED"
                and source["copyright_canonical"] in roots):
            accepted[tag].append((source, member))
    curated_candidates = 0
    for tag, pairs in accepted.items():
        homes = {source["copyright_canonical"] for source, _ in pairs}
        for source, member in pairs:
            home = source["copyright_canonical"]
            candidates[tag].append({
                "home": home, "kind": "ACCEPTED_MEMBERSHIP", "source_id": source["source_id"],
                "url": source["source_url"], "owner": source["authority_owner"],
                "scope": source["source_scope"], "claim": source["source_claim"],
                "surface": member["matched_surface"], "mapping_evidence": member["mapping_evidence"],
                "tier": member.get("browse_home_tier", "").strip(),
                "basis": member.get("browse_home_basis", "").strip(),
            })
        if len(homes) == 1:
            curated_candidates += 1

    # Only a PASS official variant edge to an already confirmed, same-root base inherits HOME.
    variant_candidates = 0
    for row in read_csv(VARIANTS):
        tag = row.get("key", "").strip()
        base = row.get("base_character", "").strip()
        home = row.get("home_copyright", "").strip()
        base_decision = decision_by_tag.get(base, {})
        if (row.get("scope") != "VARIANT_CHARACTER" or row.get("validation_state") != "PASS"
                or row.get("officiality_state") != "OFFICIAL_VARIANT" or tag not in open_tags
                or tag not in cohort_tags or home not in roots
                or base_decision.get("research_state") != "HOME_CONFIRMED"
                or base_decision.get("home_copyright") != home):
            continue
        owner = "DanbooruTagTool Issue #180 validated variant/base ledger"
        scope = f"Exact validated VARIANT_CHARACTER edge {tag} -> {base}; HOME inherited from confirmed base only."
        url = row.get("evidence_url", "").strip() or ISSUE180_URL
        source_id = deterministic_source_id(url, owner, scope)
        candidates[tag].append({
            "home": home, "kind": "INHERITANCE", "source_id": source_id, "url": url,
            "owner": owner, "scope": scope, "claim": row["evidence_claim"], "surface": tag,
            "mapping_evidence": f"Exact PASS VARIANT_CHARACTER edge {tag} -> {base}; confirmed base HOME {home}.",
            "tier": "1", "basis": f"Validated exact variant identity inherits Browse HOME from confirmed base {base}.",
        })
        variant_candidates += 1

    # A single root is sufficient. Multiple roots require explicit, complete Browse HOME priority.
    applied: dict[str, dict[str, str]] = {}
    blocked_conflicts = 0
    secondary_only = 0
    for tag, evidence in sorted(candidates.items()):
        homes = {row["home"] for row in evidence}
        if len(homes) == 1:
            home = next(iter(homes))
            eligible = [row for row in evidence if row["home"] == home and row["tier"] != "5"]
            if not eligible:
                secondary_only += 1
                continue
        else:
            tiers: dict[str, set[int]] = defaultdict(set)
            complete = True
            for row in evidence:
                try:
                    tier = int(row["tier"])
                except (TypeError, ValueError):
                    complete = False
                    break
                if tier not in {1, 2, 3, 4, 5} or not row["basis"]:
                    complete = False
                    break
                tiers[row["home"]].add(tier)
            if not complete or any(len(values) != 1 for values in tiers.values()):
                blocked_conflicts += 1
                continue
            eligible = [root for root in homes if next(iter(tiers[root])) < 5]
            if not eligible:
                secondary_only += 1
                continue
            best = min(next(iter(tiers[root])) for root in eligible)
            winners = sorted(root for root in eligible if next(iter(tiers[root])) == best)
            if len(winners) != 1:
                blocked_conflicts += 1
                continue
            home = winners[0]
            eligible = [row for row in evidence if row["home"] == home]

        chosen_ids = sorted({row["source_id"] for row in eligible})
        if not chosen_ids:
            continue
        claims = sorted({row["claim"] for row in eligible if row["claim"]})
        provenance = sorted({f"{row['kind']}:{row['source_id']} {row['url']} | {row['mapping_evidence']}"
                             for row in eligible})
        kinds = {row["kind"] for row in eligible}
        authority = ("APPROVED_REPO_EVIDENCE" if kinds <= {"QUALIFIER", "INHERITANCE"}
                     else next((source_by_id[sid]["source_type"] for sid in chosen_ids if sid in source_by_id),
                               "APPROVED_REPO_EVIDENCE"))
        applied[tag] = {
            "home": home, "source_ids": "|".join(chosen_ids), "authority_type": authority,
            "source_claim": " || ".join(claims), "provenance": " || ".join(provenance),
        }

    merged_sources = {row["source_id"]: dict(row) for row in sources}
    merged_members = {(row["source_id"], row["canonical_character"]): dict(row) for row in members}
    merged_decisions = {row["canonical_character"]: dict(row) for row in decisions}
    new_members = 0
    for tag, record in sorted(applied.items()):
        for candidate in candidates[tag]:
            if candidate["home"] != record["home"]:
                continue
            sid = candidate["source_id"]
            if sid not in merged_sources:
                merged_sources[sid] = {
                    "source_id": sid, "copyright_canonical": candidate["home"],
                    "source_url": candidate["url"], "source_type": "APPROVED_REPO_EVIDENCE",
                    "authority_owner": candidate["owner"], "source_status": "ACCEPTED",
                    "source_scope": candidate["scope"], "exact_roster_available": "false",
                    "reviewed_at": REVIEW_DATE, "source_claim": candidate["claim"],
                    "provenance": "Deterministic cohort-wide join of validated Issue #180 source records; no new external lookups.",
                    "reusable": "true", "notes": "Exact validated mapping scope only; no name inference or scope expansion.",
                }
            member_row = {
                "source_id": sid, "canonical_character": tag, "matched_surface": candidate["surface"],
                "mapping_method": "DOCUMENTED_IDENTITY_MAPPING" if candidate["kind"] == "INHERITANCE" else "EXACT_CANONICAL",
                "mapping_evidence": candidate["mapping_evidence"], "reviewed_at": REVIEW_DATE,
                "reviewer": REVIEWER, "mapping_status": "EXACT_COVERED",
                "browse_home_tier": candidate["tier"], "browse_home_basis": candidate["basis"],
            }
            key = (sid, tag)
            old_member = merged_members.get(key)
            if old_member and old_member != member_row:
                # Never rewrite an earlier accepted source/member decision.
                if any(old_member.get(field, "") != member_row.get(field, "") for field in
                       ("matched_surface", "mapping_method", "mapping_status")):
                    continue
            else:
                merged_members[key] = member_row
                new_members += 1
        decision = merged_decisions[tag]
        if decision["research_state"] != "UNRESEARCHED":
            continue
        decision.update({
            "research_state": "HOME_CONFIRMED", "home_copyright": record["home"],
            "authority_type": record["authority_type"], "source_ids": record["source_ids"],
            "source_claim": record["source_claim"], "provenance": record["provenance"],
            "reviewed_at": REVIEW_DATE, "reason_code": "COHORT_WIDE_VALIDATED_AUTHORITY_JOIN",
            "reason_detail": "Unique Browse HOME from exact validated qualifier, accepted membership, or verified base inheritance; deterministic cohort-wide join.",
            "validated_home_candidates": "",
        })

    result_sources = sorted(merged_sources.values(), key=lambda row: row["source_id"])
    result_members = sorted(merged_members.values(), key=lambda row: (row["source_id"], row["canonical_character"]))
    result_decisions = [merged_decisions[row["canonical_character"]] for row in decisions]
    validate(COHORT, SOURCES, MEMBERS, DECISIONS, expected_size=BASELINE_SIZE, roots_path=ROOTS)
    counts = {
        "cohort_size": len(cohort), "initial_unresearched": len(open_tags),
        "terminalized": len(applied), "qualifier_candidate_memberships": qualifier_candidates,
        "accepted_membership_tags_joined": len(accepted), "accepted_unique_root_tags": curated_candidates,
        "validated_variant_inheritance_matches": variant_candidates,
        "conflict_or_incomplete_priority_tags_skipped": blocked_conflicts,
        "secondary_only_tags_skipped": secondary_only, "new_source_members": new_members,
        "source_registry_count": len(result_sources),
        "home_confirmed_after": sum(row["research_state"] == "HOME_CONFIRMED" for row in result_decisions),
        "unresearched_after": sum(row["research_state"] == "UNRESEARCHED" for row in result_decisions),
    }
    return result_sources, result_members, result_decisions, counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="report deterministic join without writing")
    args = parser.parse_args()
    sources, members, decisions, counts = build()
    print("cohort-wide offline authority harvest:")
    for key, value in counts.items():
        print(f"  {key}: {value}")
    if args.check:
        return
    write_atomic(SOURCES, SOURCE_FIELDS, sources)
    write_atomic(MEMBERS, MEMBER_FIELDS, members)
    write_atomic(DECISIONS, DECISION_FIELDS, decisions)
    validate(COHORT, SOURCES, MEMBERS, DECISIONS, expected_size=BASELINE_SIZE, roots_path=ROOTS)


if __name__ == "__main__":
    main()
