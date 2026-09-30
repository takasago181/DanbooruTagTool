#!/usr/bin/env python3
"""Integrate one bulk harvest of explicit Danbooru Character/Member lists.

The harvester's candidate output remains disposable under .tmp-issue216-work.
This integrator revalidates root title scope and exact canonical links, adds
page-level accepted sources and member rows, then confirms only unique
Browse-HOME outcomes. Ambiguous identities/roots stay unresolved.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import tempfile
from collections import defaultdict
from pathlib import Path

from authority_coverage import (
    DECISION_FIELDS, MEMBER_FIELDS, SOURCE_FIELDS, deterministic_source_id,
    read_csv, validate,
)

ROOT = Path(__file__).resolve().parents[2]
ISSUE216 = ROOT / "docs/issue216"
DEFAULT_HARVEST = ROOT / ".tmp-issue216-work/danbooru-wiki-harvest-full/EXACT_DANBOORU_CHARACTER_MEMBER_LINKS.csv"
REVIEWED_AT = "2026-09-30"
REVIEWER = "Codex bulk-reviewed Danbooru curated membership"
OWNER = "Danbooru Copyright wiki explicit Character/Member lists"


def write_csv_atomic(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=path.parent,
                                     prefix=path.name + ".", suffix=".tmp", delete=False) as stream:
        temp = Path(stream.name)
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        stream.flush()
    temp.replace(path)


def tag_slug(value: str) -> str:
    return re.sub(r"\s+", "_", value.strip().lower().replace("_(series)", "_series"))


def root_aliases(roots: set[str]) -> dict[str, set[str]]:
    aliases: dict[str, set[str]] = defaultdict(set)
    for root in roots:
        aliases[tag_slug(root)].add(root)
        if root.endswith("_(series)"):
            aliases[tag_slug(root[:-len("_(series)")] + "_series")].add(root)
    for row in read_csv(ROOT / "docs/issue180/v3/migrated_evidence_seed_v3.csv"):
        if (row.get("subject_type") == "Family" and row.get("relation_type") == "FAMILY_HOME"
                and row.get("review_state") == "VALIDATED" and row.get("object_key") in roots):
            aliases[tag_slug(row["subject_key"])].add(row["object_key"])
    return aliases


def page_root(title: str, roots: set[str], aliases: dict[str, set[str]]) -> str | None:
    if title in roots:
        return title
    prefix = "list_of_"
    if not title.lower().startswith(prefix):
        return None
    remainder = title.lower()[len(prefix):]
    matches = {
        root
        for alias, mapped_roots in aliases.items()
        if alias and remainder.startswith(alias)
        and (len(remainder) == len(alias) or remainder[len(alias)] == "_")
        for root in mapped_roots
    }
    return next(iter(matches)) if len(matches) == 1 else None


def build(harvest_path: Path) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], dict[str, object]]:
    cohort = read_csv(ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv")
    decisions = read_csv(ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv")
    sources = read_csv(ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv")
    members = read_csv(ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv")
    roots = {row["copyright_canonical"] for row in read_csv(ISSUE216 / "COPYRIGHT_ROOTS_V1.csv")}
    aliases = root_aliases(roots)
    cohort_by_tag = {row["canonical_character"]: row for row in cohort}
    decision_by_tag = {row["canonical_character"]: row for row in decisions}
    source_by_id = {row["source_id"]: row for row in sources}
    member_by_key = {(row["source_id"], row["canonical_character"]): row for row in members}

    raw = read_csv(harvest_path)
    exact_links: dict[tuple[str, str, str, str], dict[str, str]] = {}
    invalid_scope = 0
    rejected_rows = 0
    for row in raw:
        tag, home = row["canonical_character"], row["semantic_root"]
        if (tag not in cohort_by_tag or home not in roots or row["mapping_method"] != "EXACT_CANONICAL"
                or row["matched_surface"] != tag or not row["section_heading"]
                or not re.search(r"\b(?:characters?|members?)\b", row["section_heading"], re.I)):
            rejected_rows += 1
            continue
        if page_root(row["page_title"], roots, aliases) != home:
            invalid_scope += 1
            continue
        # Links are accepted only from the direct canonical target in the export.
        key = (row["page_id"], home, tag, row["section_heading"])
        exact_links[key] = row

    by_page_root: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in exact_links.values():
        by_page_root[(row["page_id"], row["semantic_root"])].append(row)

    merged_sources = dict(source_by_id)
    merged_members = dict(member_by_key)
    new_source_ids: set[str] = set()
    new_member_rows = 0
    source_id_for_link: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for (page_id, home), page_rows in sorted(by_page_root.items()):
        first = page_rows[0]
        headings = sorted({row["section_heading"] for row in page_rows})
        title = first["page_title"]
        url = first["source_url"]
        if any(row["page_title"] != title or row["source_url"] != url for row in page_rows):
            raise ValueError(f"page metadata disagreement for page {page_id}")
        scope = (f"Danbooru wiki page {title} (page id {page_id}), scoped to canonical Copyright root {home}; "
                 f"explicit section(s): {', '.join(headings)}; only direct [[canonical_character]] links "
                 "on list/table rows are accepted. Other prose, sections, and unlisted Characters are excluded.")
        sid = deterministic_source_id(url, OWNER, scope)
        source = {
            "source_id": sid, "copyright_canonical": home, "source_url": url,
            "source_type": "ACCEPTED_CURATED_ROSTER", "authority_owner": OWNER,
            "source_status": "ACCEPTED", "source_scope": scope, "exact_roster_available": "true",
            "reviewed_at": REVIEWED_AT,
            "source_claim": (f"The root-scoped Danbooru wiki page explicitly lists {len({r['canonical_character'] for r in page_rows})} "
                             f"cohort Characters in the named Character/Member section(s): {', '.join(headings)}."),
            "provenance": (f"Bulk-read Danbooru wiki page {page_id}; explicit section and direct canonical link rows "
                           "were parsed once, then title/root scope and cohort identity were revalidated."),
            "reusable": "true", "notes": "Exact linked members only; page absence is not evidence.",
        }
        prior = merged_sources.get(sid)
        if prior and prior != source:
            raise ValueError(f"deterministic source identity collision: {sid}")
        merged_sources[sid] = source
        if prior is None:
            new_source_ids.add(sid)
        for row in sorted(page_rows, key=lambda item: (item["canonical_character"], item["section_heading"])):
            tag = row["canonical_character"]
            key = (sid, tag)
            member = {
                "source_id": sid, "canonical_character": tag, "matched_surface": tag,
                "mapping_method": "EXACT_CANONICAL",
                "mapping_evidence": (f"Direct wiki link [[{tag}]] in explicit {row['section_heading']} section on "
                                     f"{title}; root determined by exact page title/canonical validated alias {home}."),
                "reviewed_at": REVIEWED_AT, "reviewer": REVIEWER, "mapping_status": "EXACT_COVERED",
                "browse_home_tier": "", "browse_home_basis": "",
            }
            previous = merged_members.get(key)
            if previous:
                if previous != member:
                    immutable = ("canonical_character", "matched_surface", "mapping_method", "mapping_status")
                    if any(previous[field] != member[field] for field in immutable):
                        raise ValueError(f"exact mapping identity collision: {key}")
                member = previous
            else:
                new_member_rows += 1
            merged_members[key] = member
            source_id_for_link[(tag, home, row["section_heading"])].add(sid)

    accepted_by_tag: dict[str, list[tuple[dict[str, str], dict[str, str]]]] = defaultdict(list)
    for member in merged_members.values():
        src = merged_sources.get(member["source_id"])
        if src and src["source_status"] == "ACCEPTED" and member["mapping_status"] == "EXACT_COVERED":
            accepted_by_tag[member["canonical_character"]].append((src, member))

    changed_decisions: dict[str, dict[str, str]] = {}
    no_unique_home = 0
    for tag in sorted({row["canonical_character"] for row in raw}):
        current = decision_by_tag.get(tag)
        if not current or current["research_state"] != "UNRESEARCHED":
            continue
        evidence = accepted_by_tag.get(tag, [])
        roots_for_tag = {src["copyright_canonical"] for src, _ in evidence}
        if not roots_for_tag:
            continue
        tiers: dict[str, set[int]] = defaultdict(set)
        complete = True
        for src, member in evidence:
            tier = member.get("browse_home_tier", "").strip()
            basis = member.get("browse_home_basis", "").strip()
            if not tier or not basis:
                complete = False
                continue
            tiers[src["copyright_canonical"]].add(int(tier))
        home: str | None = None
        if len(roots_for_tag) == 1:
            candidate = next(iter(roots_for_tag))
            if tiers.get(candidate) != {5}:
                home = candidate
        elif complete and all(len(tiers.get(root, set())) == 1 for root in roots_for_tag):
            eligible = {root for root in roots_for_tag if next(iter(tiers[root])) < 5}
            if eligible:
                best = min(next(iter(tiers[root])) for root in eligible)
                winners = sorted(root for root in eligible if next(iter(tiers[root])) == best)
                if len(winners) == 1:
                    home = winners[0]
        if home is None:
            no_unique_home += 1
            continue
        new_exact = [(src, member) for src, member in evidence
                     if src["source_id"] in new_source_ids and src["copyright_canonical"] == home]
        if not new_exact:
            continue
        chosen = [(src, member) for src, member in evidence if src["copyright_canonical"] == home]
        source_ids = sorted({src["source_id"] for src, _ in chosen})
        source_claims = sorted({src["source_claim"] for src, _ in chosen})
        provenance = sorted({f"{src['source_url']} | exact [[{tag}]] member in {src['source_scope']}" for src, _ in chosen})
        updated = dict(current)
        updated.update({
            "research_state": "HOME_CONFIRMED", "home_copyright": home,
            "authority_type": "ACCEPTED_CURATED_ROSTER", "source_ids": "|".join(source_ids),
            "source_claim": " || ".join(source_claims), "provenance": " || ".join(provenance),
            "reviewed_at": REVIEWED_AT, "reason_code": "EXACT_CURATED_MEMBERSHIP_UNIQUE_HOME",
            "reason_detail": ("Explicit Danbooru Copyright wiki Character/Member roster lists this exact canonical "
                              "Character under the validated unique HOME root; candidate hint and co-occurrence were not used."),
            "validated_home_candidates": "",
        })
        baseline_home = next(row["baseline_home"] for row in cohort if row["canonical_character"] == tag)
        if baseline_home and baseline_home != home:
            raise ValueError(f"baseline #180 HOME mutation attempted: {tag}")
        changed_decisions[tag] = updated

    out_sources = sorted(merged_sources.values(), key=lambda row: row["source_id"])
    out_members = sorted(merged_members.values(), key=lambda row: (row["source_id"], row["canonical_character"]))
    out_decisions = [changed_decisions.get(row["canonical_character"], row) for row in decisions]
    metadata = {
        "harvest_input_rows": len(raw), "strict_unique_link_groups": len(exact_links),
        "source_page_root_groups": len(by_page_root), "new_sources": len(new_source_ids),
        "new_member_rows": new_member_rows, "new_home_decisions": len(changed_decisions),
        "exact_membership_rows_without_unique_home": no_unique_home,
        "rejected_scope_rows": invalid_scope, "rejected_or_nonopen_rows": rejected_rows,
        "newly_terminalized_per_new_source_review": round(len(changed_decisions) / len(new_source_ids), 4) if new_source_ids else 0.0,
        "newly_terminalized_per_wiki_page_fetched": round(len(changed_decisions) / 1596, 4),
    }
    return out_sources, out_members, out_decisions, metadata


def validate_proposed(sources: list[dict[str, str]], members: list[dict[str, str]], decisions: list[dict[str, str]]) -> dict[str, object]:
    temp = ROOT / ".tmp-issue216-work"
    paths = {"sources": temp / "wiki-validation-sources.csv", "members": temp / "wiki-validation-members.csv",
             "decisions": temp / "wiki-validation-decisions.csv"}
    for name, rows, fields in (("sources", sources, SOURCE_FIELDS), ("members", members, MEMBER_FIELDS),
                               ("decisions", decisions, DECISION_FIELDS)):
        with paths[name].open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    return validate(ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv", paths["sources"], paths["members"],
                    paths["decisions"], roots_path=ISSUE216 / "COPYRIGHT_ROOTS_V1.csv")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--harvest", type=Path, default=DEFAULT_HARVEST)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    sources, members, decisions, summary = build(args.harvest)
    validation = validate_proposed(sources, members, decisions)
    print(json.dumps({"integration": summary, "validation": validation}, ensure_ascii=False, indent=2))
    if args.check:
        return
    for path, rows, fields in (
        (ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv", sources, SOURCE_FIELDS),
        (ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv", members, MEMBER_FIELDS),
        (ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv", decisions, DECISION_FIELDS),
    ):
        write_csv_atomic(path, fields, rows)
    validate(ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv",
             ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv",
             ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv",
             ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv",
             roots_path=ISSUE216 / "COPYRIGHT_ROOTS_V1.csv")


if __name__ == "__main__":
    main()
