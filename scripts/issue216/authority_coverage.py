#!/usr/bin/env python3
"""Validate an additive authority-coverage layer for the frozen #180 residual cohort."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE_SIZE = 13_983
STATES = {
    "UNRESEARCHED",
    "SOURCE_RESEARCHED_NO_SAFE_EVIDENCE",
    "POLICY_BLOCKED",
    "IDENTITY_BLOCKED",
    "EVIDENCE_CONFLICT",
    "HOME_CONFIRMED",
}
SOURCE_TYPES = {
    "OFFICIAL_CHARACTER_ROSTER", "OFFICIAL_CHARACTER_PROFILE", "OFFICIAL_GAME_ROSTER",
    "OFFICIAL_SERIES_DIRECTORY", "OFFICIAL_PUBLISHER_ROSTER", "ACCEPTED_CURATED_ROSTER",
    "FIRST_PARTY_OTHER", "APPROVED_REPO_EVIDENCE", "DANBOORU_ACTIVE_COPYRIGHT_IMPLICATION",
}
MULTI_ROOT_SOURCE_TYPES = {"DANBOORU_ACTIVE_COPYRIGHT_IMPLICATION"}
SOURCE_STATUSES = {"ACCEPTED", "PARTIAL", "SOURCE_UNAVAILABLE", "SOURCE_INSUFFICIENT", "REJECTED"}
MAPPING_METHODS = {
    "EXACT_CANONICAL", "VALIDATED_ALIAS", "REVIEWED_NAME_MAPPING", "DOCUMENTED_IDENTITY_MAPPING",
}
AUTHORITY_TYPES = SOURCE_TYPES | {
    "REVIEWED_QUALIFIER_COPYRIGHT", "REVIEWED_VARIANT_AUTHORITY", "ROOT_POLICY_NORMALIZATION",
    "APPROVED_REPO_EVIDENCE",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

COHORT_FIELDS = ["cohort_id", "canonical_character", "baseline_state", "baseline_home"]
SOURCE_FIELDS = [
    "source_id", "copyright_canonical", "source_url", "source_type", "authority_owner",
    "source_status", "source_scope", "exact_roster_available", "reviewed_at", "source_claim",
    "provenance", "reusable", "notes",
]
MEMBER_FIELDS = [
    "source_id", "canonical_character", "member_relation_id", "canonical_home_root",
    "matched_surface", "mapping_method", "mapping_evidence",
    "reviewed_at", "reviewer", "mapping_status", "browse_home_tier", "browse_home_basis",
]
DECISION_FIELDS = [
    "cohort_id", "canonical_character", "research_state", "home_copyright", "authority_type",
    "source_ids", "source_claim", "provenance", "reviewed_at", "reason_code", "reason_detail",
    "validated_home_candidates",
]
ROOT_FIELDS = ["copyright_canonical", "provenance"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_fields(path: Path, rows: list[dict[str, str]], expected: list[str]) -> None:
    if rows:
        actual = list(rows[0])
    else:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            actual = next(csv.reader(stream), [])
    if actual != expected:
        raise ValueError(f"{path}: expected columns {expected}, got {actual}")


def split_ids(value: str) -> list[str]:
    return sorted({item.strip() for item in value.split("|") if item.strip()})


def member_home_root(source: dict[str, str], member: dict[str, str]) -> str:
    """Resolve a member-specific root for multi-root authority sources."""
    return member.get("canonical_home_root", "").strip() or source.get("copyright_canonical", "").strip()


def deterministic_source_id(source_url: str, authority_owner: str, source_scope: str) -> str:
    key = "\n".join((source_url.strip(), authority_owner.strip(), source_scope.strip()))
    return "src-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]


def validate(cohort_path: Path, sources_path: Path, members_path: Path, decisions_path: Path,
             expected_size: int = BASELINE_SIZE, roots_path: Path | None = None) -> dict[str, object]:
    cohort, sources, members, decisions = (read_csv(path) for path in
                                           (cohort_path, sources_path, members_path, decisions_path))
    for path, rows, fields in ((cohort_path, cohort, COHORT_FIELDS), (sources_path, sources, SOURCE_FIELDS),
                               (members_path, members, MEMBER_FIELDS), (decisions_path, decisions, DECISION_FIELDS)):
        require_fields(path, rows, fields)

    known_roots: set[str] | None = None
    if roots_path is not None:
        root_rows = read_csv(roots_path)
        require_fields(roots_path, root_rows, ROOT_FIELDS)
        known_roots = {row["copyright_canonical"] for row in root_rows}
        if len(known_roots) != len(root_rows) or any(not row["copyright_canonical"] or not row["provenance"] for row in root_rows):
            raise ValueError("frozen Copyright root catalog must be unique and provenance-complete")

    errors: list[str] = []
    cohort_by_id = {row["cohort_id"]: row for row in cohort}
    if len(cohort) != expected_size or len(cohort_by_id) != len(cohort):
        errors.append(f"frozen cohort must contain {expected_size} unique rows; got {len(cohort)}")
    if any(not r["cohort_id"] or not r["canonical_character"] for r in cohort):
        errors.append("cohort IDs and canonical Characters must be non-empty")
    if any(r["baseline_state"] != "HOME_UNRESOLVED" or r["baseline_home"] for r in cohort):
        errors.append("cohort must contain only frozen baseline HOME_UNRESOLVED rows with no baseline HOME")
    if len({r["canonical_character"] for r in cohort}) != len(cohort):
        errors.append("cohort contains duplicate canonical Characters")

    source_by_id = {row["source_id"]: row for row in sources}
    if len(source_by_id) != len(sources) or any(not key for key in source_by_id):
        errors.append("source registry IDs must be unique and non-empty")
    for source in sources:
        expected_id = deterministic_source_id(source["source_url"], source["authority_owner"], source["source_scope"])
        if source["source_id"] != expected_id:
            errors.append(f"non-deterministic source_id for {source['source_id']}; expected {expected_id}")
        if source["source_type"] not in SOURCE_TYPES:
            errors.append(f"invalid source_type for {source['source_id']}: {source['source_type']}")
        if source["source_status"] not in SOURCE_STATUSES:
            errors.append(f"invalid source_status for {source['source_id']}: {source['source_status']}")
        if source["exact_roster_available"] not in {"true", "false"} or source["reusable"] not in {"true", "false"}:
            errors.append(f"invalid boolean registry field for {source['source_id']}")
        for field in ("source_url", "authority_owner", "source_scope", "reviewed_at", "source_claim", "provenance"):
            if not source[field]:
                errors.append(f"missing {field} for source {source['source_id']}")
        if source["source_status"] == "ACCEPTED":
            if source["source_type"] in MULTI_ROOT_SOURCE_TYPES:
                if source["copyright_canonical"]:
                    errors.append(f"multi-root authority source must not claim one registry HOME root: {source['source_id']}")
            elif not source["copyright_canonical"]:
                errors.append(f"ACCEPTED HOME authority requires one canonical Copyright root: {source['source_id']}")

    member_keys: set[tuple[str, str, str]] = set()
    exact_members: set[tuple[str, str]] = set()
    members_by_key: dict[tuple[str, str], list[dict[str, str]]] = {}
    accepted_exact_by_character: dict[str, list[tuple[dict[str, str], dict[str, str]]]] = {}
    for member in members:
        key = (member["source_id"], member["canonical_character"], member.get("member_relation_id", "").strip())
        if key in member_keys:
            errors.append(f"duplicate source/member mapping: {key}")
        member_keys.add(key)
        members_by_key.setdefault((member["source_id"], member["canonical_character"]), []).append(member)
        if member["source_id"] not in source_by_id:
            errors.append(f"member references unknown source: {member['source_id']}")
        if member["mapping_method"] not in MAPPING_METHODS:
            errors.append(f"member mapping is not an approved exact/reviewed method: {key}")
        if not all(member[f] for f in ("matched_surface", "mapping_evidence", "reviewed_at", "reviewer")):
            errors.append(f"member mapping lacks identity review provenance: {key}")
        tier = member.get("browse_home_tier", "").strip()
        basis = member.get("browse_home_basis", "").strip()
        if bool(tier) != bool(basis):
            errors.append(f"Browse HOME priority requires both tier and basis: {key}")
        if tier and tier not in {"1", "2", "3", "4", "5"}:
            errors.append(f"invalid Browse HOME priority tier: {key} -> {tier}")
        if member["mapping_status"] == "EXACT_COVERED":
            exact_members.add((member["source_id"], member["canonical_character"]))
            source = source_by_id.get(member["source_id"])
            if source and source["source_status"] == "ACCEPTED":
                home = member_home_root(source, member)
                if source["source_type"] in MULTI_ROOT_SOURCE_TYPES:
                    if not home:
                        errors.append(f"multi-root exact member requires its own canonical HOME root: {key}")
                    elif known_roots is not None and home not in known_roots:
                        errors.append(f"multi-root exact member references missing Copyright root: {key} -> {home}")
                elif member.get("canonical_home_root", "").strip() and member["canonical_home_root"].strip() != source["copyright_canonical"]:
                    errors.append(f"member-specific HOME root conflicts with single-root source: {key}")
                accepted_exact_by_character.setdefault(member["canonical_character"], []).append((source, member))
        elif member["mapping_status"] not in {"AMBIGUOUS_REVIEW", "REJECTED"}:
            errors.append(f"invalid mapping_status for {key}: {member['mapping_status']}")

    decision_by_id = {row["cohort_id"]: row for row in decisions}
    if len(decision_by_id) != len(decisions) or set(decision_by_id) != set(cohort_by_id):
        errors.append("coverage decisions must contain exactly one row for every frozen cohort ID")
    for decision in decisions:
        cohort_row = cohort_by_id.get(decision["cohort_id"])
        if not cohort_row:
            continue
        if decision["canonical_character"] != cohort_row["canonical_character"]:
            errors.append(f"cohort identity changed for {decision['cohort_id']}")
        state = decision["research_state"]
        if state not in STATES:
            errors.append(f"invalid research_state for {decision['cohort_id']}: {state}")
            continue
        source_ids = split_ids(decision["source_ids"])
        unknown_sources = set(source_ids) - set(source_by_id)
        if unknown_sources:
            errors.append(f"unknown source IDs for {decision['cohort_id']}: {sorted(unknown_sources)}")
        if state == "UNRESEARCHED":
            if decision["reviewed_at"] or decision["reason_code"] or decision["reason_detail"]:
                errors.append(f"UNRESEARCHED row cannot masquerade as a terminal research result: {decision['cohort_id']}")
            if decision["home_copyright"]:
                errors.append(f"UNRESEARCHED row cannot have HOME: {decision['cohort_id']}")
            continue
        if not all(decision[field] for field in ("reviewed_at", "provenance", "reason_code", "reason_detail")):
            errors.append(f"terminal row lacks review/reason provenance: {decision['cohort_id']}")
        if state == "HOME_CONFIRMED":
            if not decision["home_copyright"] or decision["authority_type"] not in AUTHORITY_TYPES:
                errors.append(f"HOME_CONFIRMED lacks one HOME or recognized authority: {decision['cohort_id']}")
            if "|" in decision["home_copyright"]:
                errors.append(f"HOME_CONFIRMED cardinality exceeds one: {decision['cohort_id']}")
            if known_roots is not None and decision["home_copyright"] not in known_roots:
                errors.append(f"HOME references missing baseline Copyright root: {decision['cohort_id']}")
            if not source_ids or not decision["source_claim"]:
                errors.append(f"HOME_CONFIRMED lacks source IDs/claim: {decision['cohort_id']}")
            covered = any((source_id, decision["canonical_character"]) in exact_members for source_id in source_ids)
            if not covered:
                errors.append(f"HOME_CONFIRMED lacks exact reviewed member mapping: {decision['cohort_id']}")
            exact_accepted_ids = [source_id for source_id in source_ids
                                  if source_id in source_by_id
                                  and source_by_id[source_id]["source_status"] == "ACCEPTED"
                                  and (source_id, decision["canonical_character"]) in exact_members]
            validated_roots = {
                member_home_root(source_by_id[source_id], member)
                for source_id in exact_accepted_ids
                for member in members_by_key.get((source_id, decision["canonical_character"]), [])
            }
            if not exact_accepted_ids:
                errors.append(f"HOME_CONFIRMED requires an ACCEPTED exact-member authority source: {decision['cohort_id']}")
            if decision["home_copyright"] not in validated_roots:
                errors.append(f"HOME lacks an exact accepted member mapping to its root: {decision['cohort_id']}")
            all_roots = {member_home_root(source, member) for source, member in
                         accepted_exact_by_character.get(decision["canonical_character"], [])}
            tiers_by_root: dict[str, set[int]] = {}
            priority_complete = True
            for source, member in accepted_exact_by_character.get(decision["canonical_character"], []):
                tier = member.get("browse_home_tier", "").strip()
                basis = member.get("browse_home_basis", "").strip()
                if not tier or not basis:
                    if len(all_roots) > 1:
                        priority_complete = False
                        break
                    continue
                tiers_by_root.setdefault(member_home_root(source, member), set()).add(int(tier))
            if len(all_roots) == 1 and tiers_by_root.get(decision["home_copyright"]) == {5}:
                errors.append(f"secondary product membership alone cannot support Browse HOME: {decision['cohort_id']}")
            elif len(all_roots) > 1:
                eligible = {root: tiers for root, tiers in tiers_by_root.items()
                            if root in all_roots and 5 not in tiers}
                if (not priority_complete or any(len(tiers) != 1 for tiers in eligible.values())
                        or set(eligible) == set()):
                    errors.append(f"multiple accepted HOME roots require explicit Browse HOME priorities: {decision['cohort_id']}")
                else:
                    best_tier = min(next(iter(tiers)) for tiers in eligible.values())
                    winners = [root for root, tiers in eligible.items() if next(iter(tiers)) == best_tier]
                    if set(winners) != {decision["home_copyright"]}:
                        errors.append(f"HOME is not the unique highest Browse HOME priority: {decision['cohort_id']}")
            if decision["home_copyright"] == cohort_row["baseline_home"] and cohort_row["baseline_home"]:
                pass
            elif cohort_row["baseline_home"]:
                errors.append(f"existing confirmed HOME mutation: {decision['cohort_id']}")
        elif decision["home_copyright"]:
            errors.append(f"non-confirmed state cannot carry a HOME: {decision['cohort_id']}")
        if state == "SOURCE_RESEARCHED_NO_SAFE_EVIDENCE" and (not source_ids or not decision["source_claim"]):
            errors.append(f"no-safe-evidence terminal requires a researched source and recorded finding: {decision['cohort_id']}")
        if state in {"POLICY_BLOCKED", "IDENTITY_BLOCKED", "EVIDENCE_CONFLICT"} and not decision["reason_code"]:
            errors.append(f"blocked/conflict state requires explicit reason: {decision['cohort_id']}")
        if state == "EVIDENCE_CONFLICT":
            candidates = split_ids(decision["validated_home_candidates"])
            exact_accepted_ids = [source_id for source_id in source_ids
                                  if source_id in source_by_id
                                  and source_by_id[source_id]["source_status"] == "ACCEPTED"
                                  and (source_id, decision["canonical_character"]) in exact_members]
            validated_roots = {
                member_home_root(source_by_id[source_id], member)
                for source_id in exact_accepted_ids
                for member in members_by_key.get((source_id, decision["canonical_character"]), [])
            }
            if len(validated_roots) < 2 or set(candidates) != validated_roots:
                errors.append(f"EVIDENCE_CONFLICT requires exact member mappings from accepted sources proving its candidate roots: {decision['cohort_id']}")
        elif decision["validated_home_candidates"]:
            errors.append(f"validated competing HOME candidates only belong on EVIDENCE_CONFLICT: {decision['cohort_id']}")

    if errors:
        raise ValueError("authority coverage validation failed:\n- " + "\n- ".join(errors[:100]))
    counts = Counter(row["research_state"] for row in decisions)
    source_membership_counts = Counter(row["source_id"] for row in members if row["mapping_status"] == "EXACT_COVERED")
    reused_members = sum(count for count in source_membership_counts.values() if count > 1)
    summary: dict[str, object] = {
        "schema_version": "issue216-authority-coverage-v1",
        "baseline_cohort_size": expected_size,
        "cohort_sha256": sha256(cohort_path),
        "accounted": len(decisions),
        "unresearched": counts["UNRESEARCHED"],
        "research_state_counts": {state: counts[state] for state in sorted(STATES)},
        "source_registry_count": len(sources),
        "exact_member_mapping_count": len(exact_members),
        "source_reused_member_count": reused_members,
        "source_reuse_ratio": round(reused_members / len(members), 6) if members else 0.0,
        "copyright_catalog_root_count": len(known_roots) if known_roots is not None else None,
        "missing_copyright_roots": sum(
            row["research_state"] == "HOME_CONFIRMED" and known_roots is not None and row["home_copyright"] not in known_roots
            for row in decisions
        ),
        "complete": len(decisions) == expected_size and counts["UNRESEARCHED"] == 0,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", type=Path, default=ROOT / "docs/issue216/AUTHORITY_COVERAGE_COHORT_V1.csv")
    parser.add_argument("--sources", type=Path, default=ROOT / "docs/issue216/COPYRIGHT_AUTHORITY_REGISTRY_V1.csv")
    parser.add_argument("--members", type=Path, default=ROOT / "docs/issue216/AUTHORITY_SOURCE_MEMBERS_V1.csv")
    parser.add_argument("--decisions", type=Path, default=ROOT / "docs/issue216/AUTHORITY_COVERAGE_DECISIONS_V1.csv")
    parser.add_argument("--roots", type=Path, default=ROOT / "docs/issue216/COPYRIGHT_ROOTS_V1.csv")
    parser.add_argument("--expected-size", type=int, default=BASELINE_SIZE)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()
    summary = validate(args.cohort, args.sources, args.members, args.decisions, args.expected_size, args.roots)
    serialized = json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.summary:
        args.summary.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    if not summary["complete"]:
        raise SystemExit("coverage is valid but incomplete; UNRESEARCHED rows remain")


if __name__ == "__main__":
    main()
