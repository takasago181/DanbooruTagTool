#!/usr/bin/env python3
"""Generate exact-string roster-to-catalog candidates without deciding HOME."""
from __future__ import annotations

import argparse
import csv
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def norm(value: str) -> str:
    return "".join(unicodedata.normalize("NFKC", value).casefold().split())


def exact_tag_slug(value: str) -> str:
    """Convert an official Latin display name to the exact Danbooru tag surface."""
    return "_".join(unicodedata.normalize("NFKC", value).casefold().split())


def name_values(row: dict[str, str]):
    values = [row.get("canonical_tag", ""), row.get("display_ja", ""), row.get("display_en", "")]
    for column in ("aliases", "aliases_en", "search_en"):
        values.extend(row.get(column, "").split(" | "))
    return {norm(value) for value in values if norm(value)}


def build(roster: list[dict[str, str]], catalog_path: Path, cohort_path: Path, decisions_path: Path, sources_path: Path,
          members_path: Path | None = None, allow_reviewed_pending_source: bool = False,
          master_path: Path | None = None, graph_path: Path | None = None):
    expected = ["source_id", "source_url", "source_scope", "matched_surface"]
    if not roster or list(roster[0]) != expected:
        raise ValueError(f"roster columns must be exactly {expected}")
    cohort = {r["canonical_character"] for r in read_csv(cohort_path)}
    states = {r["canonical_character"]: r["research_state"] for r in read_csv(decisions_path)}
    sources = {r["source_id"]: r for r in read_csv(sources_path)}
    master = {r["canonical_tag"]: r for r in read_csv(master_path)} if master_path else {}
    variant_edges: dict[str, list[dict[str, str]]] = defaultdict(list)
    if graph_path:
        for edge in read_csv(graph_path):
            if edge["relation_type"] == "VARIANT_OF" and edge["review_state"] == "VALIDATED":
                variant_edges[edge["object_key"]].append(edge)
    catalog = [r for r in read_csv(catalog_path) if r.get("category") == "4"]
    canonical_tags = {row.get("canonical_tag", "") for row in catalog if row.get("canonical_tag", "")}
    index: dict[str, set[str]] = defaultdict(set)
    qualified_alias_index: dict[str, set[str]] = defaultdict(set)
    search_surface_index: dict[str, set[str]] = defaultdict(set)
    for row in catalog:
        tag = row.get("canonical_tag", "")
        if tag:
            for value in name_values(row):
                index[value].add(tag)
            for value in row.get("search_ja", "").split(" | "):
                if norm(value):
                    search_surface_index[norm(value)].add(tag)
            # Some official English rosters show a bare stage name while the
            # catalog alias includes an explicit work qualifier. Keep this
            # contextual exact-head match review-only; it is never an AUTO.
            for alias in row.get("aliases", "").split(" | "):
                alias = alias.strip()
                if " (" in alias and alias.endswith(")"):
                    head = alias.rsplit(" (", 1)[0]
                    if norm(head):
                        qualified_alias_index[norm(head)].add(tag)

    # Reuse exact identity mappings already accepted in the authority ledger.
    if members_path and members_path.exists():
        for member in read_csv(members_path):
            source = sources.get(member.get("source_id", ""))
            tag = member.get("canonical_character", "")
            if (source and source["source_status"] == "ACCEPTED"
                    and member.get("mapping_status") == "EXACT_COVERED"
                    and member.get("matched_surface") and tag):
                index[norm(member["matched_surface"])].add(tag)

    output = []
    seen = set()
    for source_row in roster:
        key = (source_row["source_id"], norm(source_row["matched_surface"]))
        if not all(source_row.values()) or key in seen:
            raise ValueError(f"blank or duplicate source roster surface: {source_row}")
        registered = sources.get(source_row["source_id"])
        allowed_status = {"ACCEPTED"}
        if allow_reviewed_pending_source:
            allowed_status.add("REVIEWED_PENDING_ACCEPTANCE")
        if (not registered or registered["source_status"] not in allowed_status
                or registered["source_url"] != source_row["source_url"]
                or registered["source_scope"] != source_row["source_scope"]):
            raise ValueError(f"roster input does not match an accepted source registry scope: {source_row}")
        seen.add(key)
        direct_candidates = set(index.get(norm(source_row["matched_surface"]), set()))
        # Official English display names often exactly match the canonical
        # Character tag after the catalog's standard whitespace-to-underscore
        # spelling (for example, "Clive Rosfield" -> "clive_rosfield").
        # Admit only an exact existing canonical tag; this is not fuzzy lookup.
        canonical_slug = exact_tag_slug(source_row["matched_surface"])
        if canonical_slug in canonical_tags:
            direct_candidates.add(canonical_slug)
        contextual_candidates = (
            qualified_alias_index.get(norm(source_row["matched_surface"]), set())
            | search_surface_index.get(norm(source_row["matched_surface"]), set())
        )
        # Contextual surfaces never independently qualify for AUTO, but they
        # remain competing identities when a direct display/alias also matches.
        candidates = sorted(direct_candidates | contextual_candidates)
        direct_selected = sorted(direct_candidates)
        selected = direct_selected[0] if len(direct_selected) == 1 else ""
        if not direct_candidates:
            if contextual_candidates:
                status = "REVIEW_REQUIRED"
                basis = "Name is present only as a qualifier-bearing alias or catalog search surface; identity review is required."
            else:
                status, basis = "NO_MATCH", "No exact normalized match in Character catalog fields."
        elif len(candidates) > 1:
            status, basis = "REVIEW_REQUIRED", "Exact normalized surface collides across canonical Character identities."
            selected = ""
        elif selected not in cohort:
            status, basis = "OUTSIDE_COHORT", "Unique exact catalog match is outside frozen #216 unresolved cohort."
            selected = ""
        elif states.get(selected) != "UNRESEARCHED":
            status, basis = "ALREADY_TERMINAL", "Unique exact match is already terminal in #216; no replacement proposed."
            selected = ""
        else:
            status, basis = "AUTO_MAPPING_CANDIDATE", "One unique exact normalized roster/catalog name match; requires source-scope review."
        output.append({
            **source_row, "canonical_character": selected, "candidate_status": status,
            "candidate_basis": basis, "competing_tags": " | ".join(candidates),
        })
        # A directory can name a baseline-confirmed base Character while the
        # unresolved cohort contains explicit variants. Inherit only through
        # a validated #180 VARIANT_OF edge and only when base HOME equals this
        # reviewed source's HOME root. These remain reviewable candidates.
        base_tag = exact_tag_slug(source_row["matched_surface"])
        base = master.get(base_tag)
        registered_root = registered.get("copyright_canonical", "")
        if (base and base.get("final_state") == "HOME_CONFIRMED"
                and base.get("home_copyright") == registered_root):
            for edge in variant_edges.get(base_tag, []):
                variant_tag = edge["subject_key"]
                if variant_tag not in cohort or states.get(variant_tag) != "UNRESEARCHED":
                    continue
                variant_key = (source_row["source_id"], norm(source_row["matched_surface"]), variant_tag)
                if variant_key in seen:
                    continue
                seen.add(variant_key)
                output.append({
                    **source_row, "canonical_character": variant_tag,
                    "candidate_status": "AUTO_MAPPING_CANDIDATE",
                    "candidate_basis": (
                        f"Exact roster base name resolves to baseline-confirmed {base_tag}; "
                        f"validated #180 VARIANT_OF evidence {edge['evidence_id']} links {variant_tag} to that base; "
                        f"base HOME {registered_root} matches the reviewed source root."
                    ),
                    "competing_tags": variant_tag,
                })
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--roster", type=Path, help="CSV with source_id/source_url/source_scope/matched_surface columns")
    group.add_argument("--surfaces", type=Path, help="one exact official roster surface per UTF-8 line")
    parser.add_argument("--source-id", help="registered accepted source ID; required with --surfaces")
    parser.add_argument("--catalog", type=Path, default=ROOT / "docs/issue70/data/runtime/issue70_catalog_overlay.csv")
    parser.add_argument("--cohort", type=Path, default=ROOT / "docs/issue216/AUTHORITY_COVERAGE_COHORT_V1.csv")
    parser.add_argument("--decisions", type=Path, default=ROOT / "docs/issue216/AUTHORITY_COVERAGE_DECISIONS_V1.csv")
    parser.add_argument("--sources", type=Path, default=ROOT / "docs/issue216/COPYRIGHT_AUTHORITY_REGISTRY_V1.csv")
    parser.add_argument("--members", type=Path, default=ROOT / "docs/issue216/AUTHORITY_SOURCE_MEMBERS_V1.csv")
    parser.add_argument("--allow-reviewed-pending-source", action="store_true",
                        help="generate candidates for an independently reviewed proposed source; HOME is still not accepted")
    parser.add_argument("--master", type=Path, help="read-only exact #180 master for validated variant inheritance candidates")
    parser.add_argument("--graph", type=Path, help="read-only #180 graph for validated VARIANT_OF edges")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.roster:
        roster = read_csv(args.roster)
    else:
        if not args.source_id:
            parser.error("--source-id is required with --surfaces")
        registered = next((r for r in read_csv(args.sources) if r["source_id"] == args.source_id), None)
        if not registered or registered["source_status"] != "ACCEPTED":
            parser.error("--source-id must name an accepted registry source")
        roster = [{
            "source_id": registered["source_id"], "source_url": registered["source_url"],
            "source_scope": registered["source_scope"], "matched_surface": surface,
        } for surface in args.surfaces.read_text(encoding="utf-8-sig").splitlines() if surface.strip()]
    rows = build(roster, args.catalog, args.cohort, args.decisions, args.sources, args.members,
                 args.allow_reviewed_pending_source, args.master, args.graph)
    fields = ["source_id", "source_url", "source_scope", "matched_surface", "canonical_character", "candidate_status", "candidate_basis", "competing_tags"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    counts = {}
    for row in rows:
        counts[row["candidate_status"]] = counts.get(row["candidate_status"], 0) + 1
    print(f"mapping candidates generated: {len(rows)} surfaces; " + ", ".join(f"{k}={v}" for k,v in sorted(counts.items())))


if __name__ == "__main__":
    main()
