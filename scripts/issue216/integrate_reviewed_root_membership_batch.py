#!/usr/bin/env python3
"""Integrate exact mappings from reviewed root-scoped Danbooru list pages.

The candidate/root hints are never authority. HOME roots come only from an
exact linked canonical work heading or the reviewed root-page scope. Exact
members with no safe HOME can be terminalized as researched-no-safe-evidence.
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

try:
    from authority_coverage import (
        DECISION_FIELDS, MEMBER_FIELDS, SOURCE_FIELDS, deterministic_source_id, read_csv, validate,
    )
    from apply_validated_membership_batch import build_decisions
except ModuleNotFoundError:
    from scripts.issue216.authority_coverage import (
        DECISION_FIELDS, MEMBER_FIELDS, SOURCE_FIELDS, deterministic_source_id, read_csv, validate,
    )
    from scripts.issue216.apply_validated_membership_batch import build_decisions

ROOT = Path(__file__).resolve().parents[2]
ISSUE216 = ROOT / "docs/issue216"
DEFAULT_LANES = ROOT / ".tmp-issue216-work/official-lanes/corrected-membership-roots-201-230"
DEFAULT_CANDIDATES = DEFAULT_LANES / "potential_home_additions_contingent.csv"
DEFAULT_ROOT_UNRESOLVED = DEFAULT_LANES / "root_unresolved_members.csv"
DEFAULT_SOURCES_REVIEWED = DEFAULT_LANES / "candidate_roster_source_reviews.csv"
REVIEWED_AT = "2026-09-30"
REVIEWER = "Codex integrator exact roster review"
OWNER = "Danbooru Copyright wiki explicit Character/Member list"
LINK_RE = re.compile(r"\[\[([^\[\]|#]+)(?:\|[^\]]*)?\]\]")


def read(path: Path) -> list[dict[str, str]]:
    return read_csv(path)


def tag_slug(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"\[[^\]]+\]", "", value).strip().casefold()
    return re.sub(r"\s+", "_", value)


def exact_link_target(line: str) -> str | None:
    matches = list(LINK_RE.finditer(line))
    return matches[0].group(1).strip() if len(matches) == 1 else None


def is_list_or_table_row(line: str) -> bool:
    return bool(re.match(r"^\s*(?:\*+|-+|#+|\|)", line))


def source_scope_for(row: dict[str, str], source_review: dict[str, str]) -> tuple[str, str]:
    """Derive HOME root from exact source heading/root scope, never from a hint."""
    title = row["source_title"].strip()
    page_root = source_review["source_root"].strip()
    proposed_root = row["proposed_home_root"].strip()
    if not page_root:
        raise ValueError(f"source review has no root scope for {title}")
    valid_page_titles = {page_root, f"list_of_{tag_slug(page_root)}_characters"}
    if title.casefold() not in {value.casefold() for value in valid_page_titles}:
        raise ValueError(f"page title does not exactly scope the reviewed root: {title} -> {page_root}")
    if proposed_root == page_root:
        scope = source_review["source_scope"].strip()
        if not scope:
            raise ValueError(f"source review has no explicit scope for {title}")
        return page_root, scope

    # Narrow work roots are usable only if an explicit linked heading's exact
    # normalized title equals the canonical root. No alias/fuzzy fallback.
    heading = row["section"].strip()
    target = exact_link_target(heading)
    if not target or tag_slug(target) != proposed_root:
        raise ValueError(f"HOME root is not an exact linked work heading: {row.get('canonical_character', title)}")
    scope = (f"Danbooru wiki page {title} (page id {row['page_id']}), only direct exact Character links "
             f"under the explicit linked work heading [[{target}]]; canonical heading slug exactly equals "
             f"the validated Copyright root {proposed_root}. Other headings, prose, and unlisted Characters are excluded.")
    return proposed_root, scope


def _write(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _source(source_id: str, home: str, url: str, scope: str, count: int, status: str,
            claim: str, reusable: str) -> dict[str, str]:
    return {
        "source_id": source_id, "copyright_canonical": home, "source_url": url,
        "source_type": "ACCEPTED_CURATED_ROSTER", "authority_owner": OWNER,
        "source_status": status, "source_scope": scope, "exact_roster_available": "true",
        "reviewed_at": REVIEWED_AT, "source_claim": claim,
        "provenance": ("Cached Danbooru wiki page reviewed once; direct exact Character links and declared list scope "
                       "revalidated by the integrator." if home else
                       "Cached Danbooru wiki page reviewed once; exact positive Character links recorded. Policy cross-check: "
                       "docs/issue180/autonomous/decisions/discovery_roster_reviews_v2.csv, DISCOVERY_GROUP=kamen_rider, "
                       "requires title-specific authority and assigns no franchise-wide HOME."),
        "reusable": reusable, "notes": "Positive exact members only; unlisted identities are not implied.",
    }


def build(candidates_path: Path, unresolved_path: Path, reviews_path: Path,
          root_page_sources_path: Path | None = None, root_page_members_path: Path | None = None):
    cohort = read(ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv")
    decisions = read(ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv")
    sources = read(ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv")
    members = read(ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv")
    roots = {r["copyright_canonical"] for r in read(ISSUE216 / "COPYRIGHT_ROOTS_V1.csv")}
    cohort_tags = {r["canonical_character"] for r in cohort}
    decision_by_tag = {r["canonical_character"]: dict(r) for r in decisions}
    source_review_by_title = {r["page_title"]: r for r in read(reviews_path)}
    existing_source_by_id = {r["source_id"]: dict(r) for r in sources}
    existing_member_keys = {(r["source_id"], r["canonical_character"]) for r in members}

    candidate_rows = read(candidates_path)
    if bool(root_page_sources_path) != bool(root_page_members_path):
        raise ValueError("root-page source and member proposals must be provided together")
    if root_page_sources_path and root_page_members_path:
        proposal_sources = read(root_page_sources_path)
        proposal_members = read(root_page_members_path)
        source_by_id = {row["proposed_source_id"]: row for row in proposal_sources}
        review_by_title = dict(source_review_by_title)
        for proposal in proposal_sources:
            root = proposal["copyright_canonical"].strip()
            title = proposal["page_title"].strip()
            if (proposal.get("source_status_proposal") != "REVIEWED_PENDING_ACCEPTANCE"
                    or proposal.get("source_type") != "ACCEPTED_CURATED_ROSTER"
                    or root not in roots or "characters" not in proposal["explicit_sections"].casefold()
                    or title.casefold() != root.casefold()):
                raise ValueError(f"root-page source is not explicit, exact, and root-scoped: {title}")
            if proposal["proposed_source_id"] != deterministic_source_id(
                    proposal["source_url"], proposal["authority_owner"], proposal["source_scope"]):
                raise ValueError(f"non-deterministic root-page source ID: {proposal['proposed_source_id']}")
            review_by_title[title] = {
                "page_title": title, "source_root": root,
                "source_acceptance_recommendation": "ACCEPTED_CURATED_ROSTER_POSITIVE_ENTRIES_ONLY",
                "source_scope": proposal["source_scope"],
            }
        source_review_by_title = review_by_title
        for member in proposal_members:
            sid = member["proposed_source_id"].strip()
            proposal = source_by_id.get(sid)
            tag = member["canonical_character"].strip()
            current = decision_by_tag.get(tag, {})
            integrated_sid = deterministic_source_id(
                member["source_url"], OWNER, member["source_scope"]
            )
            same_existing_result = (
                current.get("research_state") == "HOME_CONFIRMED"
                and current.get("home_copyright") == member.get("candidate_root")
                and integrated_sid in set(current.get("source_ids", "").split("|"))
                and (integrated_sid, tag) in existing_member_keys
            )
            if (not proposal or member.get("prior_state") != "UNRESEARCHED"
                    or member.get("proposed_source_status") != "REVIEWED_PENDING_ACCEPTANCE"
                    or member.get("membership_status") != "EXACT_MAPPING_CANDIDATE"
                    or member.get("home_decision") != "NONE; source registration and Integrator review required"
                    or member.get("competing_existing_accepted_roots", "").strip()
                    or member.get("source_url") != proposal["source_url"]
                    or member.get("source_scope") != proposal["source_scope"]
                    or member.get("candidate_root") != proposal["copyright_canonical"]
                    or tag not in cohort_tags
                    or (current.get("research_state") != "UNRESEARCHED" and not same_existing_result)):
                raise ValueError(f"root-page member proposal is not current/open/exact: {tag}")
            target = exact_link_target(member["mapping_evidence"])
            surface = member["matched_surface"].strip()
            if (not target or target != surface or tag_slug(target) != tag
                    or member.get("mapping_method") != "EXACT_CANONICAL_AFTER_CASE_SPACE_NORMALIZATION"):
                raise ValueError(f"root-page identity is not an exact normalized direct link: {tag}")
            candidate_rows.append({
                "canonical_character": tag, "candidate_characters": tag,
                "catalog_candidates": tag, "surface": surface,
                "source_title": proposal["page_title"], "source_url": proposal["source_url"],
                "proposed_home_root": proposal["copyright_canonical"],
                "section": member["section_heading"], "page_id": proposal["page_id"],
                "line_excerpt": f"* [[{target}]]", "mapping_state": "AUTO_MAPPING_CANDIDATE",
                "proposal_state": "CONTINGENT_ON_SOURCE_ACCEPTANCE",
                "prior_research_state": "UNRESEARCHED", "prior_home_copyright": "",
            })
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    decisions_by_tag: dict[str, set[str]] = defaultdict(set)
    links_by_page: dict[tuple[str, str], str] = {}
    exact_mapping_count = 0
    for row in candidate_rows:
        tag = row["canonical_character"].strip()
        if (row.get("home_proposal_state", row.get("proposal_state", "")) != "CONTINGENT_ON_SOURCE_ACCEPTANCE"
                or row.get("mapping_state") != "AUTO_MAPPING_CANDIDATE"
                or row.get("prior_research_state") != "UNRESEARCHED"
                or row.get("prior_home_copyright", "").strip()
                or tag not in cohort_tags):
            raise ValueError(f"candidate is no longer open/exact or lacks accepted proposal state: {tag}")
        if row.get("catalog_candidates", "").strip() != tag:
            raise ValueError(f"identity is not a unique exact catalog match: {tag}")
        source_review = source_review_by_title.get(row["source_title"].strip())
        if not source_review or not source_review.get("source_acceptance_recommendation", "").startswith(
                ("A3_EXPLICIT_CURATED_CHARACTER_OR_MEMBER_LIST_POSITIVE_ENTRIES_ONLY",
                 "ACCEPTED_CURATED_ROSTER_POSITIVE_ENTRIES_ONLY")):
            raise ValueError(f"source page was not accepted as a positive-only curated list: {row['source_title']}")
        target = exact_link_target(row["line_excerpt"])
        surface = row["surface"].strip()
        if (not is_list_or_table_row(row["line_excerpt"]) or not target
                or target != surface or tag_slug(target) != tag):
            raise ValueError(f"source row is not an exact direct link to the unique canonical identity: {tag}")
        home, scope = source_scope_for(row, source_review)
        if home not in roots:
            raise ValueError(f"proposed source scope resolves to a missing Copyright root: {home}")
        current = decision_by_tag[tag]
        if current["research_state"] != "UNRESEARCHED":
            sid = deterministic_source_id(row["source_url"].strip(), OWNER, scope)
            current_source_ids = set(current["source_ids"].split("|"))
            if not (current["research_state"] == "HOME_CONFIRMED"
                    and current["home_copyright"] == home and sid in current_source_ids
                    and (sid, tag) in existing_member_keys):
                raise ValueError(f"existing terminal decision conflicts with curated batch: {tag}")
        key = (row["source_url"].strip(), home, scope)
        groups[key].append(row)
        decisions_by_tag[tag].add(home)
        links_by_page[(row["source_url"].strip(), tag)] = row["line_excerpt"].strip()
        exact_mapping_count += 1

    # A candidate from more than one root stays unresolved; do not accept only
    # the first row in an arbitrary order.
    conflicting_tags = {tag for tag, homes in decisions_by_tag.items() if len(homes) != 1}
    for tag in conflicting_tags:
        raise ValueError(f"candidate batch includes competing roots; review before integration: {tag}")

    out_sources = dict(existing_source_by_id)
    out_members = {(r["source_id"], r["canonical_character"]): dict(r) for r in members}
    source_ids_by_tag: dict[str, list[str]] = defaultdict(list)
    for (url, home, scope), rows in sorted(groups.items()):
        sid = deterministic_source_id(url, OWNER, scope)
        claim = (f"Explicit curated page scope lists {len({r['canonical_character'] for r in rows})} exact cohort "
                 f"Character identities under the named scope for canonical Copyright root {home}.")
        source = _source(sid, home, url, scope, len(rows), "ACCEPTED", claim, "true")
        prior = out_sources.get(sid)
        if prior and any(prior.get(k, "") != source[k] for k in
                         ("source_id", "copyright_canonical", "source_url", "source_type", "authority_owner",
                          "source_status", "source_scope", "exact_roster_available", "reusable")):
            raise ValueError(f"source registry identity/scope collision: {sid}")
        if not prior:
            out_sources[sid] = source
        for row in rows:
            tag = row["canonical_character"].strip()
            surface = row["surface"].strip()
            method = "EXACT_CANONICAL" if surface == tag else "REVIEWED_NAME_MAPPING"
            member = {
                "source_id": sid, "canonical_character": tag, "matched_surface": surface,
                "mapping_method": method,
                "mapping_evidence": (f"Direct link [[{exact_link_target(row['line_excerpt'])}]] in explicit roster/list row; "
                                     f"its exact normalized canonical identity is {tag}; unique catalog match. "
                                     f"Scope: {scope}"),
                "reviewed_at": REVIEWED_AT, "reviewer": REVIEWER, "mapping_status": "EXACT_COVERED",
                "browse_home_tier": "", "browse_home_basis": "",
            }
            existing = out_members.get((sid, tag))
            if existing and any(existing.get(k, "") != member[k] for k in
                                 ("canonical_character", "matched_surface", "mapping_method", "mapping_status")):
                raise ValueError(f"member mapping identity collision: {(sid, tag)}")
            if not existing:
                out_members[(sid, tag)] = member
            source_ids_by_tag[tag].append(sid)

    # Also account for exact Kamen Rider identity memberships where the reviewed
    # page has only broad era headings. Those rows do not support a HOME.
    unresolved_rows = read(unresolved_path)
    unresolved_groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in unresolved_rows:
        tag = row["canonical_character"].strip()
        if (row.get("mapping_state") != "EXACT_CHARACTER_IDENTITY_ROOT_UNRESOLVED"
                or row.get("proposal_state") != "REVIEW_REQUIRED_NO_EXPLICIT_WORK_SCOPE"
                or row.get("prior_research_state") != "UNRESEARCHED"
                or row.get("prior_home_copyright", "").strip()
                    or tag not in cohort_tags):
            raise ValueError(f"root-unresolved row is not an open exact identity: {tag}")
        if row.get("catalog_candidates", "").strip() != tag:
            raise ValueError(f"root-unresolved member has competing identities: {tag}")
        target = exact_link_target(row["line_excerpt"])
        if (not is_list_or_table_row(row["line_excerpt"]) or not target
                or tag_slug(target) != tag):
            raise ValueError(f"root-unresolved roster link is not an exact normalized identity: {tag}")
        current = decision_by_tag[tag]
        if current["research_state"] != "UNRESEARCHED":
            if not (current["research_state"] == "SOURCE_RESEARCHED_NO_SAFE_EVIDENCE"
                    and current["home_copyright"] == ""):
                raise ValueError(f"existing terminal decision conflicts with root-unresolved result: {tag}")
        groups_key = (row["source_url"].strip(), row["source_scope"].strip())
        unresolved_groups[groups_key].append(row)

    no_safe_tags: set[str] = set()
    for (url, scope), rows in sorted(unresolved_groups.items()):
        sid = deterministic_source_id(url, OWNER, scope)
        claim = (f"The curated list directly links {len(rows)} exact Kamen Rider Character identities, but records only "
                 "broad era sections and no supported work-specific Browse HOME; Issue #180's root review does not "
                 "authorize a franchise-wide HOME from this page alone.")
        source = _source(sid, "", url, scope, len(rows), "SOURCE_INSUFFICIENT", claim, "false")
        prior = out_sources.get(sid)
        if prior and any(prior.get(k, "") != source[k] for k in
                         ("source_id", "copyright_canonical", "source_url", "source_type", "authority_owner",
                          "source_status", "source_scope", "exact_roster_available", "reusable")):
            raise ValueError(f"root-unresolved source registry collision: {sid}")
        if not prior:
            out_sources[sid] = source
        for row in rows:
            tag = row["canonical_character"].strip()
            surface = row["surface"].strip()
            member = {
                "source_id": sid, "canonical_character": tag, "matched_surface": surface,
                "mapping_method": "REVIEWED_NAME_MAPPING" if surface != tag else "EXACT_CANONICAL",
                "mapping_evidence": (f"Direct link [[{exact_link_target(row['line_excerpt'])}]] in the curated Kamen Rider "
                                     f"list; exact normalized English identity maps uniquely to {tag}. The era-only "
                                     "section does not establish a Browse HOME."),
                "reviewed_at": REVIEWED_AT, "reviewer": REVIEWER, "mapping_status": "EXACT_COVERED",
                "browse_home_tier": "", "browse_home_basis": "",
            }
            if (sid, tag) not in out_members:
                out_members[(sid, tag)] = member
            no_safe_tags.add(tag)

    # Run the existing deterministic semantic-membership projector for all HOME
    # assignments; it preserves any non-UNRESEARCHED decision.
    validation_dir = ROOT / ".tmp-issue216-work/root-membership-validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    source_path, member_path, decision_path = (validation_dir / name for name in
                                                ("sources.csv", "members.csv", "decisions.csv"))
    _write(source_path, SOURCE_FIELDS, sorted(out_sources.values(), key=lambda r: r["source_id"]))
    _write(member_path, MEMBER_FIELDS, sorted(out_members.values(), key=lambda r: (r["source_id"], r["canonical_character"])))
    _write(decision_path, DECISION_FIELDS, decisions)
    out_decisions, applied = build_decisions(
        ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv", source_path, member_path, decision_path,
        ISSUE216 / "COPYRIGHT_ROOTS_V1.csv",
    )

    decision_out = {r["canonical_character"]: r for r in out_decisions}
    no_safe_applied = 0
    for tag in sorted(no_safe_tags):
        current = decision_out[tag]
        if current["research_state"] != "UNRESEARCHED":
            if current["research_state"] == "SOURCE_RESEARCHED_NO_SAFE_EVIDENCE" and current["source_ids"] == sid:
                continue
            raise ValueError(f"cannot replace existing terminal outcome with source-no-safe-evidence: {tag}")
        row = next(r for rows in unresolved_groups.values() for r in rows if r["canonical_character"] == tag)
        sid = deterministic_source_id(row["source_url"].strip(), OWNER, row["source_scope"].strip())
        source = out_sources[sid]
        current.update({
            "research_state": "SOURCE_RESEARCHED_NO_SAFE_EVIDENCE", "home_copyright": "",
            "authority_type": "", "source_ids": sid, "source_claim": source["source_claim"],
            "provenance": (f"{source['source_url']} | {source['source_scope']} | exact identity mapping {tag}; no Browse HOME resolved. "
                           "Policy cross-check: docs/issue180/autonomous/decisions/discovery_roster_reviews_v2.csv, "
                           "DISCOVERY_GROUP=kamen_rider."),
            "reviewed_at": REVIEWED_AT, "reason_code": "SOURCE_RESEARCHED_NO_SAFE_EVIDENCE",
            "reason_detail": "The reviewed curated source establishes the exact listed identity but provides only broad era scope; existing #180 root policy withholds a safe unique work-level Browse HOME.",
            "validated_home_candidates": "",
        })
        no_safe_applied += 1

    result_sources = sorted(out_sources.values(), key=lambda r: r["source_id"])
    result_members = sorted(out_members.values(), key=lambda r: (r["source_id"], r["canonical_character"]))
    result_decisions = [decision_out[r["canonical_character"]] for r in decisions]
    metrics = {
        "source_review_pages": len({row["source_title"] for row in candidate_rows} | {r["source_title"] for r in unresolved_rows}),
        "new_source_scopes": len(set(out_sources) - set(existing_source_by_id)),
        "exact_home_mapping_candidates": exact_mapping_count,
        "new_exact_member_rows": len(set(out_members) - existing_member_keys),
        "new_home_decisions": applied,
        "source_researched_no_safe_evidence": no_safe_applied,
        "open_root_conflict_candidates_rejected": len(conflicting_tags),
        "baseline_home_mutations": 0,
        "remaining_unresearched": sum(r["research_state"] == "UNRESEARCHED" for r in result_decisions),
    }
    vpaths = [validation_dir / "full-sources.csv", validation_dir / "full-members.csv",
              validation_dir / "full-decisions.csv"]
    for path, fields, rows in zip(vpaths, (SOURCE_FIELDS, MEMBER_FIELDS, DECISION_FIELDS),
                                  (result_sources, result_members, result_decisions)):
        _write(path, fields, rows)
    validation = validate(ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv", *vpaths,
                          roots_path=ISSUE216 / "COPYRIGHT_ROOTS_V1.csv")
    return result_sources, result_members, result_decisions, metrics, validation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--root-unresolved", type=Path, default=DEFAULT_ROOT_UNRESOLVED)
    parser.add_argument("--source-reviews", type=Path, default=DEFAULT_SOURCES_REVIEWED)
    parser.add_argument("--root-page-sources", type=Path)
    parser.add_argument("--root-page-members", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    sources, members, decisions, metrics, validation = build(
        args.candidates, args.root_unresolved, args.source_reviews,
        args.root_page_sources, args.root_page_members,
    )
    print({"batch": metrics, "validation": validation})
    if args.check:
        return
    _write(ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv", SOURCE_FIELDS, sources)
    _write(ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv", MEMBER_FIELDS, members)
    _write(ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv", DECISION_FIELDS, decisions)
    validate(ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv",
             ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv",
             ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv",
             ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv",
             roots_path=ISSUE216 / "COPYRIGHT_ROOTS_V1.csv")


if __name__ == "__main__":
    main()
