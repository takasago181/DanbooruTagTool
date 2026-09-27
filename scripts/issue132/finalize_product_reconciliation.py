from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

EXPECTED = 31_003
EXISTING_ROUTES = {
    "ACTION_CONTACT", "BODY_SITE", "CLOTHING_EXPOSURE", "COLOR_PATTERN_SHAPE",
    "COMPOSITION_CAMERA", "CONTENT_RATING", "EXPRESSION_GAZE", "FLUID_EXCRETION",
    "HAIR_FACE", "LIGHT_TIME_WEATHER", "LIVING", "NONHUMAN_TRANSFORM", "PEOPLE_COUNT",
    "POSE_POSITION", "RELATION_ROLE", "SCENE_BACKGROUND", "STYLE_PROCESSING", "TEXT_SYMBOL",
    "TOOL_OBJECT",
}
SYSTEMIC_ROUTES = {"COLOR_PATTERN_SHAPE", "NONHUMAN_TRANSFORM"}
SUPPORTING_HIGH_VALUE_ROUTES = {
    "ACTION_CONTACT", "BODY_SITE", "CLOTHING_EXPOSURE", "COMPOSITION_CAMERA",
    "FLUID_EXCRETION", "PEOPLE_COUNT", "POSE_POSITION", "RELATION_ROLE", "SCENE_BACKGROUND",
    "TOOL_OBJECT",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_json_list(value: str) -> list[str]:
    value = value or "[]"
    parsed = json.loads(value)
    if not isinstance(parsed, list) or any(not isinstance(x, str) for x in parsed):
        raise ValueError("expected JSON string array")
    return parsed


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        parsed = list(csv.DictReader(f))
    if len(parsed) != len(rows) or any(set(row) != set(fields) for row in parsed):
        raise SystemExit(f"CSV parse-back validation failed: {path}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    args = ap.parse_args()
    root = Path(args.root)
    out = root / "docs/issue132/product-reconciliation"
    ledger_path = out / "product_reconciliation_ledger.csv"
    diff_path = out / "pass_b_full_diff.csv"
    context_path = out / "pass-b-product-context/identity_audit.csv"
    ledger = read_csv(ledger_path)
    diff = read_csv(diff_path)
    context = read_csv(context_path)
    summary = read_json(out / "pass_b_summary.json")
    if any(len(rows) != EXPECTED for rows in (ledger, diff, context)):
        raise SystemExit("Pass B/C population is not exactly 31,003")

    context_by = {r["identity_key"]: r for r in context}
    diff_by = {r["identity_key"]: r for r in diff}
    if len(context_by) != EXPECTED or len(diff_by) != EXPECTED:
        raise SystemExit("duplicate identity key in Pass B inputs")
    if {r["identity_key"] for r in ledger} != context_by.keys() or context_by.keys() != diff_by.keys():
        raise SystemExit("identity set mismatch in reconciliation inputs")

    additions: list[dict] = []
    upstream_routes: list[dict] = []
    search_only_rows: list[dict] = []
    unresolved_rows: list[dict] = []
    candidate_rows: list[dict] = []
    status_counts = Counter()
    route_status_counts = Counter()
    systemic_route_rows: dict[str, list[dict]] = defaultdict(list)

    for row in ledger:
        key = row["identity_key"]
        ctx = context_by[key]
        d = diff_by[key]
        core = read_json_list(d["missing_core_routes"])
        supporting = read_json_list(d["missing_supporting_routes"])
        current_routes = read_json_list(d["current_routes"])
        current_local = read_json_list(d["current_local_refinements"])
        missing_local = read_json_list(d["missing_local_refinements"])
        current_body = read_json_list(d["current_body_sites"])
        missing_body = read_json_list(d["missing_body_sites"])
        current_themes = read_json_list(d["current_themes"])
        missing_themes = read_json_list(d["missing_themes"])
        missing = [(route, "CORE") for route in core] + [(route, "SUPPORTING") for route in supporting]
        if any(route not in EXISTING_ROUTES for route, _ in missing):
            raise SystemExit(f"{key}: non-existing Unified route in candidate queue")

        route_dispositions = []
        for route, strength in missing:
            if row["discovery_mode"] == "SEMANTIC_UNRESOLVED":
                disposition = "SEMANTIC_UNRESOLVED"
                reason = "Effective Pass-A state is unresolved."
            elif row["browseable_before"] != "YES":
                disposition = "UPSTREAM_REVIEW"
                reason = "The identity is not browseable today; #132 cannot grant first browse authority."
            elif missing_local:
                disposition = "UPSTREAM_REVIEW"
                reason = "Missing local refinement belongs to the #64 owner."
            elif read_json_list(d["current_routes_not_reproduced"]):
                disposition = "UPSTREAM_REVIEW"
                reason = "A current route is not reproduced by the independent map; the existing route owner must review it."
            elif row["route_vocabulary_gap"] == "YES":
                disposition = "UPSTREAM_REVIEW"
                reason = "Route-vocabulary gaps are default-deny and need a systemic route/refinement review."
            elif route in SYSTEMIC_ROUTES:
                disposition = "UPSTREAM_REVIEW"
                if route == "COLOR_PATTERN_SHAPE":
                    reason = "Full-population color-modifier concentration points to a #64 secondary-path/facet issue; do not emit row overrides first."
                else:
                    reason = "The General LIVING_NATURE/CREATURE and nonhuman boundary is concentrated enough to require owner mapping review before row overrides."
            elif strength == "CORE":
                disposition = "ADD_SECONDARY_CANDIDATE"
                reason = "Confirmed CORE visual axis, already-browseable identity, no owner gap, and existing route shelf remains coherent at this growth."
            elif row["issue118_content_intent"] in {"SEXUAL", "CONTEXTUAL"} and route in SUPPORTING_HIGH_VALUE_ROUTES:
                disposition = "ADD_SECONDARY_CANDIDATE"
                reason = "Confirmed SUPPORTING axis for the existing Sexual/GeneralPurpose lens; route adds a distinct user-controlled browse path without changing content/facet authority."
            else:
                disposition = "SEARCH_ONLY"
                reason = "SUPPORTING route adds little beyond current route/local path and Japanese/English/alias search at the full shelf level."

            route_dispositions.append({"route_id": route, "strength": strength, "disposition": disposition, "reason": reason})
            route_status_counts[(route, disposition, strength)] += 1
            if disposition == "ADD_SECONDARY_CANDIDATE":
                additions.append({"identity_key": key, "route_id": route})
            elif disposition == "UPSTREAM_REVIEW":
                upstream_routes.append({
                    "identity_key": key, "route_id": route, "strength": strength, "reason": reason,
                    "current_routes": row["current_routes"], "general_paths": row["general_paths"],
                    "issue118_content_intent": row["issue118_content_intent"],
                })
            elif disposition == "SEMANTIC_UNRESOLVED":
                unresolved_rows.append({"identity_key": key, "route_id": route, "strength": strength, "reason": reason})
            else:
                search_only_rows.append({
                    "identity_key": key, "route_id": route, "strength": strength, "reason": reason,
                    "display_ja": row["display_ja"], "search_ja": row["search_ja"], "aliases": row["aliases"],
                })
            if route in SYSTEMIC_ROUTES and disposition == "UPSTREAM_REVIEW":
                systemic_route_rows[route].append({"identity_key": key, "route_id": route, "strength": strength, "general_paths": row["general_paths"], "current_routes": row["current_routes"]})

        if row["discovery_mode"] == "SEMANTIC_UNRESOLVED":
            final_status = "SEMANTIC_UNRESOLVED"
        elif route_dispositions and any(x["disposition"] == "ADD_SECONDARY_CANDIDATE" for x in route_dispositions):
            final_status = "ADD_SECONDARY_CANDIDATE"
        elif route_dispositions and any(x["disposition"] == "UPSTREAM_REVIEW" for x in route_dispositions):
            final_status = "UPSTREAM_REVIEW"
        elif (
            missing_local
            or read_json_list(d["current_routes_not_reproduced"])
            or row["route_vocabulary_gap"] == "YES"
            or (row["membership"] == "GENERAL_ONLY" and (missing_body or missing_themes))
            or (row["browseable_before"] != "YES" and row["discovery_mode"] in {"BROWSE_WORTHY", "MIXED"} and (core or supporting))
        ):
            final_status = "UPSTREAM_REVIEW"
        elif row["discovery_mode"] == "SEARCH_ORIENTED" or not route_dispositions or all(x["disposition"] == "SEARCH_ONLY" for x in route_dispositions):
            final_status = "SEARCH_ONLY"
        else:
            final_status = "UPSTREAM_REVIEW"
        row["product_disposition"] = final_status
        row["route_dispositions"] = json.dumps(route_dispositions, ensure_ascii=False, separators=(",", ":"))
        row["candidate_routes"] = json.dumps([x["route_id"] for x in route_dispositions if x["disposition"] == "ADD_SECONDARY_CANDIDATE"], ensure_ascii=False, separators=(",", ":"))
        row["product_decision_note"] = "; ".join(sorted({x["reason"] for x in route_dispositions}))
        row["has_any_local_refinement"] = "YES" if current_local else "NO"
        row["has_any_body_facet"] = "YES" if current_body else "NO"
        row["has_any_theme_facet"] = "YES" if current_themes else "NO"
        row["top_level_only_before"] = "YES" if not (current_local or current_body or current_themes) else "NO"
        status_counts[final_status] += 1
        if final_status == "ADD_SECONDARY_CANDIDATE":
            for item in route_dispositions:
                if item["disposition"] == "ADD_SECONDARY_CANDIDATE":
                    candidate_rows.append({
                        "identity_key": key, "route_id": item["route_id"], "route_strength": item["strength"],
                        "issue118_content_intent": row["issue118_content_intent"],
                        "discovery_mode": row["discovery_mode"], "display_ja": row["display_ja"],
                        "search_ja": row["search_ja"], "aliases": row["aliases"],
                        "current_routes": row["current_routes"], "current_local_refinements": row["current_local_refinements"],
                        "current_body_sites": row["current_body_sites"], "current_themes": row["current_themes"],
                        "top_level_only_before": "YES" if row["current_local_refinements"] == "[]" and row["current_body_sites"] == "[]" and row["current_themes"] == "[]" else "NO",
                        "missing_body_sites_research_only": row["missing_body_sites"],
                        "missing_themes_research_only": row["missing_themes"],
                        "runtime_cost_assessment": "One static route membership in the existing UnifiedBrowseIndex; no query-time evaluation or new schema. 274 memberships are about 0.81% of the 33,688 ordinary catalog backing rows; actual build/memory/latency measurement remains a pre-promotion gate.",
                        "reason": item["reason"],
                    })

    additions.sort(key=lambda x: (x["identity_key"], x["route_id"]))
    if len(additions) != len({(x["identity_key"], x["route_id"]) for x in additions}):
        raise SystemExit("duplicate ADD_SECONDARY_CANDIDATE pair")
    write_csv(out / "ADD_SECONDARY_CANDIDATES.csv", ["identity_key", "route_id"], additions)
    write_csv(out / "ADD_SECONDARY_CANDIDATE_REVIEW.csv", list(candidate_rows[0].keys()) if candidate_rows else ["identity_key", "route_id"], candidate_rows)
    upstream_identity_rows = []
    search_identity_rows = []
    unresolved_identity_rows = []
    for row in ledger:
        d = diff_by[row["identity_key"]]
        context_row = context_by[row["identity_key"]]
        if row["product_disposition"] == "UPSTREAM_REVIEW":
            reasons = [x["reason"] for x in json.loads(row["route_dispositions"]) if x["disposition"] == "UPSTREAM_REVIEW"]
            if not reasons:
                if read_json_list(d["missing_local_refinements"]): reasons.append("Missing local refinement belongs to #64.")
                if read_json_list(d["current_routes_not_reproduced"]): reasons.append("Current route needs owner review.")
                if row["route_vocabulary_gap"] == "YES": reasons.append("Route-vocabulary gap requires design review.")
                if row["membership"] == "GENERAL_ONLY" and (read_json_list(d["missing_body_sites"]) or read_json_list(d["missing_themes"])):
                    reasons.append("General-only facet finding is recorded as a Unified facet architecture candidate; no route overlay is used to represent it.")
                if row["browseable_before"] != "YES": reasons.append("Non-browseable identity cannot receive a #132 first-route overlay.")
            upstream_identity_rows.append({
                "identity_key": row["identity_key"], "missing_routes": json.dumps(read_json_list(d["missing_core_routes"]) + read_json_list(d["missing_supporting_routes"]), ensure_ascii=False, separators=(",", ":")),
                "disposition": "UPSTREAM_REVIEW", "reason": "; ".join(sorted(set(reasons))),
                "current_routes": d["current_routes"], "general_paths": context_row.get("general_paths", ""),
                "issue118_content_intent": row["issue118_content_intent"], "diff_flags": d["diff_flags"],
                "missing_body_sites_research_only": d["missing_body_sites"], "missing_themes_research_only": d["missing_themes"],
            })
        elif row["product_disposition"] == "SEARCH_ONLY":
            search_identity_rows.append({
                "identity_key": row["identity_key"], "missing_routes": json.dumps(read_json_list(d["missing_core_routes"]) + read_json_list(d["missing_supporting_routes"]), ensure_ascii=False, separators=(",", ":")),
                "disposition": "SEARCH_ONLY", "reason": "No #132 browse delta passed the incremental-value gate; current route/local path and exact Japanese/English/alias search remain available.",
                "display_ja": row["display_ja"], "search_ja": row["search_ja"], "aliases": row["aliases"],
                "current_routes": d["current_routes"], "issue118_content_intent": row["issue118_content_intent"],
            })
        elif row["product_disposition"] == "SEMANTIC_UNRESOLVED":
            unresolved_identity_rows.append({
                "identity_key": row["identity_key"], "disposition": "SEMANTIC_UNRESOLVED",
                "reason": "Effective Pass-A semantic state remains unresolved; no production route decision is made.",
                "current_routes": d["current_routes"], "issue118_content_intent": row["issue118_content_intent"],
            })
    write_csv(out / "UPSTREAM_REVIEW.csv", ["identity_key", "missing_routes", "disposition", "reason", "current_routes", "general_paths", "issue118_content_intent", "diff_flags", "missing_body_sites_research_only", "missing_themes_research_only"], upstream_identity_rows)
    write_csv(out / "SEARCH_ONLY.csv", ["identity_key", "missing_routes", "disposition", "reason", "display_ja", "search_ja", "aliases", "current_routes", "issue118_content_intent"], search_identity_rows)
    write_csv(out / "SEMANTIC_UNRESOLVED.csv", ["identity_key", "disposition", "reason", "current_routes", "issue118_content_intent"], unresolved_identity_rows)

    ledger_fields = list(ledger[0].keys()) + [
        "product_disposition", "route_dispositions", "candidate_routes", "product_decision_note",
        "has_any_local_refinement", "has_any_body_facet", "has_any_theme_facet", "top_level_only_before",
    ]
    write_csv(out / "product_reconciliation_ledger.csv", ledger_fields, ledger)

    # Shelf-level before/after statistics for all nineteen accepted Unified routes.
    current_counts = Counter()
    current_gp = Counter()
    current_sex = Counter()
    after_counts = Counter()
    after_gp = Counter()
    after_sex = Counter()
    selected = {(x["identity_key"], x["route_id"]): x for x in additions}
    route_shelf = []
    for row in ledger:
        key = row["identity_key"]
        intent = row["issue118_content_intent"]
        gp = intent in {"NON_SEXUAL", "CONTEXTUAL"}
        sex = intent in {"SEXUAL", "CONTEXTUAL"}
        for route in read_json_list(row["current_routes"]):
            current_counts[route] += 1
            after_counts[route] += 1
            if gp:
                current_gp[route] += 1; after_gp[route] += 1
            if sex:
                current_sex[route] += 1; after_sex[route] += 1
        for (ident, route) in selected:
            if ident != key or route in read_json_list(row["current_routes"]):
                continue
            after_counts[route] += 1
            if gp:
                after_gp[route] += 1
            if sex:
                after_sex[route] += 1
    by_route_candidate = defaultdict(list)
    for c in candidate_rows:
        by_route_candidate[c["route_id"]].append(c)
    for route in sorted(EXISTING_ROUTES):
        rows = by_route_candidate[route]
        count_core = sum(x["route_strength"] == "CORE" for x in rows)
        count_support = len(rows) - count_core
        local_yes = sum(x["current_local_refinements"] != "[]" for x in rows)
        body_yes = sum(x["current_body_sites"] != "[]" for x in rows)
        theme_yes = sum(x["current_themes"] != "[]" for x in rows)
        no_refinement = sum(x["top_level_only_before"] == "YES" for x in rows)
        sexual_adds = sum(x["issue118_content_intent"] in {"SEXUAL", "CONTEXTUAL"} for x in rows)
        gp_adds = sum(x["issue118_content_intent"] in {"NON_SEXUAL", "CONTEXTUAL"} for x in rows)
        route_shelf.append({
            "route_id": route,
            "current_identity_count": current_counts[route],
            "candidate_additions": len(rows),
            "after_identity_count": after_counts[route],
            "generalpurpose_before": current_gp[route],
            "generalpurpose_candidate_additions": gp_adds,
            "generalpurpose_after": after_gp[route],
            "sexual_lens_before": current_sex[route],
            "sexual_lens_candidate_additions": sexual_adds,
            "sexual_lens_after": after_sex[route],
            "core_derived_candidates": count_core,
            "supporting_derived_candidates": count_support,
            "candidate_with_local_refinement": local_yes,
            "candidate_without_local_refinement": len(rows) - local_yes,
            "candidate_with_body_facet": body_yes,
            "candidate_without_body_facet": len(rows) - body_yes,
            "candidate_with_theme_facet": theme_yes,
            "candidate_without_theme_facet": len(rows) - theme_yes,
            "top_level_only_candidates": no_refinement,
            "route_growth_percent": round((len(rows) / current_counts[route] * 100) if current_counts[route] else (100.0 if rows else 0.0), 2),
        })
    write_csv(out / "shelf_before_after.csv", list(route_shelf[0].keys()), route_shelf)

    family_counts = Counter()
    for c in candidate_rows:
        row = context_by[c["identity_key"]]
        root_path = (row.get("general_paths", "").split("|")[0].split("/", 1)[0] or "SPECIAL_OR_NO_GENERAL_PATH")
        family_counts[(c["route_id"], root_path, c["route_strength"])] += 1
    family_rows = [
        {"route_id": route, "current_general_path_root": family, "route_strength": strength, "candidate_additions": count,
         "share_of_route_candidates_percent": round(count / max(1, sum(v for (r, _, _), v in family_counts.items() if r == route)) * 100, 2)}
        for (route, family, strength), count in sorted(family_counts.items(), key=lambda x: (x[0][0], -x[1], x[0][1], x[0][2]))
    ]
    write_csv(out / "candidate_family_concentration.csv", ["route_id", "current_general_path_root", "route_strength", "candidate_additions", "share_of_route_candidates_percent"], family_rows)

    # General-only facet architecture findings remain separate from route candidates.
    general_only = [r for r in ledger if r["membership"] == "GENERAL_ONLY"]
    facet_findings = []
    for kind, field, label in (("BODY", "missing_body_sites", "facet_id"), ("THEME", "missing_themes", "facet_id")):
        counts = Counter()
        sex_counts = Counter()
        gp_counts = Counter()
        browseable_counts = Counter()
        for row in general_only:
            facets = read_json_list(row[field])
            for facet in facets:
                counts[facet] += 1
                if row["issue118_content_intent"] in {"SEXUAL", "CONTEXTUAL"}:
                    sex_counts[facet] += 1
                if row["issue118_content_intent"] in {"NON_SEXUAL", "CONTEXTUAL"}:
                    gp_counts[facet] += 1
                if row["browseable_before"] == "YES":
                    browseable_counts[facet] += 1
        for facet in sorted(counts):
            facet_findings.append({
                "finding_type": kind, "facet_id": facet,
                "general_only_identity_count": counts[facet],
                "generalpurpose_lens_identity_count": gp_counts[facet],
                "sexual_lens_identity_count": sex_counts[facet],
                "already_browseable_identity_count": browseable_counts[facet],
                "implementation_status": "RESEARCH_ONLY_UNIFIED_FACET_ARCHITECTURE_CANDIDATE",
            })
    write_csv(out / "body_theme_architecture_findings.csv", ["finding_type", "facet_id", "general_only_identity_count", "generalpurpose_lens_identity_count", "sexual_lens_identity_count", "already_browseable_identity_count", "implementation_status"], facet_findings)
    general_body_ids = {r["identity_key"] for r in general_only if read_json_list(r["missing_body_sites"])}
    general_theme_ids = {r["identity_key"] for r in general_only if read_json_list(r["missing_themes"])}
    general_sex_body = {r["identity_key"] for r in general_only if read_json_list(r["missing_body_sites"]) and r["issue118_content_intent"] in {"SEXUAL", "CONTEXTUAL"}}
    general_sex_theme = {r["identity_key"] for r in general_only if read_json_list(r["missing_themes"]) and r["issue118_content_intent"] in {"SEXUAL", "CONTEXTUAL"}}
    general_body_assignments = sum(len(read_json_list(r["missing_body_sites"])) for r in general_only)
    general_theme_assignments = sum(len(read_json_list(r["missing_themes"])) for r in general_only)
    general_facet_rows = [r for r in general_only if read_json_list(r["missing_body_sites"]) or read_json_list(r["missing_themes"])]
    candidate_identity_ids = {r["identity_key"] for r in candidate_rows}
    body_candidate_overlap = len(general_body_ids & candidate_identity_ids)
    theme_candidate_overlap = len(general_theme_ids & candidate_identity_ids)
    facet_route_overlap = Counter()
    facet_search_coverage = Counter(r["search_surface_level"] for r in general_facet_rows)
    for row in general_facet_rows:
        for route in read_json_list(row["current_routes"]):
            facet_route_overlap[route] += 1
    facet_route_rows = [
        {"route_id": route, "general_only_missing_facet_identities": facet_route_overlap[route]}
        for route in sorted(facet_route_overlap)
    ]
    write_csv(out / "body_theme_route_overlap.csv", ["route_id", "general_only_missing_facet_identities"], facet_route_rows)
    facet_md = [
        "# Issue #132 body/theme architecture findings",
        "",
        "These are research-only facet gaps for General identities. The route-candidate CSV contains only identity + existing-route membership pairs; facet IDs are never candidate additions and facet gaps do not qualify an identity for a route. A single identity can independently appear in both reports when it has separate evidence for an existing route and a missing facet.",
        "",
        f"- General-only identities missing at least one body facet: **{len(general_body_ids)}** ({general_body_assignments} facet assignments).",
        f"- General-only identities missing at least one theme facet: **{len(general_theme_ids)}** ({general_theme_assignments} facet assignments).",
        f"- General-only identities missing either: **{len({r['identity_key'] for r in general_facet_rows})}**.",
        f"- Sexual-lens subset (SEXUAL + CONTEXTUAL): body **{len(general_sex_body)}**, theme **{len(general_sex_theme)}**.",
        f"- Identity overlap with route candidates (independent findings only): body **{body_candidate_overlap}**, theme **{theme_candidate_overlap}**.",
        "- The existing Japanese/English/alias search stays available for every row; these facets would narrow browse results by a generation axis.",
        "- Route overlap and exact search-surface counts are in `body_theme_route_overlap.csv` and the full ledger.",
        "",
        "## Facet membership sizes",
        "",
        "| Axis | Facet | General-only identities | GeneralPurpose lens | Sexual lens | Already browseable |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in facet_findings:
        facet_md.append(f"| {row['finding_type']} | {row['facet_id']} | {row['general_only_identity_count']} | {row['generalpurpose_lens_identity_count']} | {row['sexual_lens_identity_count']} | {row['already_browseable_identity_count']} |")
    facet_md += [
        "",
        "## Product judgment",
        "",
        "The concentrated body-site gaps include 55 Sexual-lens identities for BREAST_NIPPLE, 25 for BUTTOCK_ANAL, and 20 for MOUTH_ORAL. That is a practical specialized browse axis even though the full-population share is small. Record this as `UNIFIED_FACET_ARCHITECTURE_CANDIDATE` for a separate owner/schema/UI/performance gate.",
        "Theme gaps are smaller (12 General-only identities in the Sexual lens across the three themes), so they remain findings for the same architecture review rather than a separate v1 implementation proposal.",
        "",
        "No result-filter latency, startup-memory, or index-build measurement was taken. The current product has no General body/theme runtime facet surface; performance and bake-boundary evidence must precede any implementation decision.",
    ]
    (out / "BODY_THEME_ARCHITECTURE_FINDINGS.md").write_text("\n".join(facet_md) + "\n", encoding="utf-8")

    # Explicit systemic report, based on full-population repeated pattern counts.
    nonhuman = systemic_route_rows["NONHUMAN_TRANSFORM"]
    color = systemic_route_rows["COLOR_PATTERN_SHAPE"]
    pending_by_key = {r["identity_key"]: r for r in ledger if r.get("provisional_disposition") == "PENDING_PRODUCT_VALUE_REVIEW"}
    eligible_systemic = {
        route: [
            r for r in pending_by_key.values()
            if route in read_json_list(r["missing_core_routes"]) + read_json_list(r["missing_supporting_routes"])
        ]
        for route in SYSTEMIC_ROUTES
    }
    nonhuman_eligible = eligible_systemic["NONHUMAN_TRANSFORM"]
    nonhuman_by_current = Counter((x["current_routes"], x["general_paths"].split("|")[0].split("/", 1)[0] if x["general_paths"] else "SPECIAL_OR_NO_GENERAL_PATH") for x in nonhuman_eligible)
    current_route_not_reproduced = Counter()
    missing_by_core_route = Counter()
    missing_by_supporting_route = Counter()
    for row in diff:
        for route in read_json_list(row["current_routes_not_reproduced"]):
            current_route_not_reproduced[route] += 1
        for route in read_json_list(row["missing_core_routes"]):
            missing_by_core_route[route] += 1
        for route in read_json_list(row["missing_supporting_routes"]):
            missing_by_supporting_route[route] += 1
    sys_text = [
        "# Issue #132 systemic product findings",
        "",
        "Pass B is a mechanical diff. These Pass C findings prevent repeated identity rows from hiding a route/projection or refinement issue.",
        "",
        "## Color / pattern",
        "",
        f"The Pass-B map has {missing_by_core_route['COLOR_PATTERN_SHAPE']} CORE and {missing_by_supporting_route['COLOR_PATTERN_SHAPE']} SUPPORTING missing route memberships ({missing_by_core_route['COLOR_PATTERN_SHAPE'] + missing_by_supporting_route['COLOR_PATTERN_SHAPE']} total). The product-eligible queue contains {sum('COLOR_PATTERN_SHAPE' in read_json_list(r['missing_core_routes']) + read_json_list(r['missing_supporting_routes']) for r in eligible_systemic['COLOR_PATTERN_SHAPE'])} additions after browseability/local-owner checks, all routed to #64 upstream review.",
        "The existing General pattern audit independently finds 1,791 color-modifier rows without a COLOR_APPEARANCE secondary path. This is a repeated owner-taxonomy omission, not a set of independent #132 exceptions. No row from this cluster is emitted in ADD_SECONDARY_CANDIDATES.csv.",
        "",
        "## LIVING / NONHUMAN_TRANSFORM boundary",
        "",
        f"Pass B has {missing_by_core_route['NONHUMAN_TRANSFORM']} CORE and {missing_by_supporting_route['NONHUMAN_TRANSFORM']} SUPPORTING missing route memberships. The product-eligible queue contains {sum('NONHUMAN_TRANSFORM' in read_json_list(r['missing_core_routes']) + read_json_list(r['missing_supporting_routes']) for r in eligible_systemic['NONHUMAN_TRANSFORM'])} additions before systemic screening; the largest product-eligible current-route/source-path clusters are {nonhuman_by_current.most_common(8)}.",
        "This cluster mixes creature/race identity, nonhuman anatomy, and transformation concepts. A global LIVING mapping change would be too broad, while a 93-row identity overlay would conceal the General taxonomy boundary. All product-eligible rows are returned to #64/#76 ownership review before identity-level candidates.",
        "",
        "## Current routes not independently reproduced",
        "",
        f"{sum(current_route_not_reproduced.values())} route memberships across {summary['flag_counts'].get('CURRENT_ROUTE_NOT_REPRODUCED', 0)} identities are not reproduced by the independent map. Largest route counts: {current_route_not_reproduced.most_common(8)}. #132 does not remove or counter-route them; current-route corrections remain with the owning taxonomy.",
        "",
        "## Local refinements and vocabulary",
        "",
        f"{summary['flag_counts'].get('MISSING_LOCAL_REFINEMENT', 0)} identities have local-refinement gaps and {summary['flag_counts'].get('ROUTE_VOCABULARY_GAP', 0)} have vocabulary gaps. These go upstream/design review; neither is represented as a runtime row overlay.",
        "",
        "## Review order",
        "",
        "1. #64 General secondary path and route projection review for color-modifier families.",
        "2. #64/#76 review of General creature and nonhuman-transformation boundaries.",
        "3. Owner review of unreproduced current routes and missing local refinements.",
        "4. Treat only isolated, already-browseable, route-coherent exceptions as #132 candidates.",
    ]
    (out / "systemic_issue_report.md").write_text("\n".join(sys_text) + "\n", encoding="utf-8")

    sexual_routes = {"ACTION_CONTACT", "POSE_POSITION", "BODY_SITE", "CLOTHING_EXPOSURE", "FLUID_EXCRETION", "RELATION_ROLE", "TOOL_OBJECT", "NONHUMAN_TRANSFORM"}
    sexual_rows = [r for r in route_shelf if r["route_id"] in sexual_routes]
    write_csv(out / "sexual_lens_impact.csv", list(sexual_rows[0].keys()), sexual_rows)

    summary_out = {
        "schema_version": "issue132-product-reconciliation-summary-v1",
        "research_semantic_head": "d74352be827c52a24888fbfc8bf71b8982627130",
        "live_main_head": "e5d0f7d954ff491c1a5661a0652e6142f2b0d08d",
        "pass_b_population": EXPECTED,
        "pass_b_flag_counts_nonexclusive": summary["flag_counts"],
        "pass_b_unique_identity_count": EXPECTED,
        "pass_c_disposition_identity_counts": dict(sorted(status_counts.items())),
        "add_secondary_candidate_pairs": len(additions),
        "add_secondary_candidate_identities": len({x["identity_key"] for x in additions}),
        "add_secondary_candidates_by_route": dict(sorted(Counter(x["route_id"] for x in additions).items())),
        "add_secondary_candidate_core_pairs": sum(x["route_strength"] == "CORE" for x in candidate_rows),
        "add_secondary_candidate_supporting_pairs": sum(x["route_strength"] == "SUPPORTING" for x in candidate_rows),
        "generalpurpose_lens_candidate_pairs": sum(x["issue118_content_intent"] in {"NON_SEXUAL", "CONTEXTUAL"} for x in candidate_rows),
        "sexual_lens_candidate_pairs": sum(x["issue118_content_intent"] in {"SEXUAL", "CONTEXTUAL"} for x in candidate_rows),
        "sexual_lens_definition": "#118 SEXUAL or CONTEXTUAL, matching UnifiedBrowse ContentIntentFilter.Sexual",
        "generalpurpose_lens_definition": "#118 NON_SEXUAL or CONTEXTUAL, matching UnifiedBrowse ContentIntentFilter.GeneralPurpose",
        "upstream_review_route_rows": len(upstream_routes),
        "upstream_review_identity_count": len(upstream_identity_rows),
        "search_only_route_rows": len(search_only_rows),
        "search_only_identity_count": len(search_identity_rows),
        "semantic_unresolved_route_rows": len(unresolved_rows),
        "semantic_unresolved_identity_count": len({x["identity_key"] for x in unresolved_rows}) or status_counts.get("SEMANTIC_UNRESOLVED", 0),
        "general_only_missing_body_facet_identity_count": len(general_body_ids),
        "general_only_missing_body_facet_assignment_count": general_body_assignments,
        "general_only_missing_theme_facet_identity_count": len(general_theme_ids),
        "general_only_missing_theme_facet_assignment_count": general_theme_assignments,
        "general_only_sexual_lens_missing_body_facet_identity_count": len(general_sex_body),
        "general_only_sexual_lens_missing_theme_facet_identity_count": len(general_sex_theme),
        "unified_facet_architecture_candidate": bool(general_body_ids or general_theme_ids),
        "runtime_cost": "not measured; Pass C research only and no implementation was requested",
        "runtime_cost_estimate": "274 static route memberships through the existing index, about 0.81% of 33,688 ordinary backing rows; no per-query work. Build/memory/latency must be measured before any production apply.",
        "route_decisions": "existing routes only; no new routes/facets; supporting candidates accepted only where a separate Sexual/GeneralPurpose generation axis adds clear path value",
    }
    (out / "final_reconciliation_summary.json").write_text(json.dumps(summary_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md = [
        "# Issue #132 Pass B/C reconciliation summary",
        "",
        f"- Research semantic HEAD: `{summary_out['research_semantic_head']}`",
        f"- Live main HEAD: `{summary_out['live_main_head']}`",
        f"- Pass B population: **{EXPECTED:,} / {EXPECTED:,}**",
        "- Product candidate gate: already-browseable identities only; existing route IDs only; no quota.",
        "- Sexual lens uses #118 SEXUAL + CONTEXTUAL, matching current app behavior. GeneralPurpose uses NON_SEXUAL + CONTEXTUAL.",
        "",
        "## Pass B flags",
        "",
        "Counts are nonexclusive identity flags; a row can carry several flags.",
        "",
        "| Flag | Identities |",
        "|---|---:|",
    ]
    for flag, count in sorted(summary["flag_counts"].items()):
        md.append(f"| {flag} | {count:,} |")
    md += [
        "",
        "## Pass C dispositions",
        "",
        "| Disposition | Identities |",
        "|---|---:|",
    ]
    for status, count in sorted(status_counts.items()):
        md.append(f"| {status} | {count:,} |")
    md += [
        "",
        f"ADD_SECONDARY candidate pairs: **{len(additions):,}** across **{summary_out['add_secondary_candidate_identities']:,}** identities.",
        f"- CORE: {summary_out['add_secondary_candidate_core_pairs']:,}; SUPPORTING: {summary_out['add_secondary_candidate_supporting_pairs']:,}.",
        f"- Sexual-lens: {summary_out['sexual_lens_candidate_pairs']:,}; GeneralPurpose-lens: {summary_out['generalpurpose_lens_candidate_pairs']:,}.",
        f"- UPSTREAM_REVIEW: {summary_out['upstream_review_identity_count']:,} identities; SEARCH_ONLY: {summary_out['search_only_identity_count']:,}; SEMANTIC_UNRESOLVED: {summary_out['semantic_unresolved_identity_count']:,}.",
        f"- General-only missing facets: body {len(general_body_ids):,} identities/{summary_out['general_only_missing_body_facet_assignment_count']:,} assignments; theme {len(general_theme_ids):,} identities/{summary_out['general_only_missing_theme_facet_assignment_count']:,} assignments.",
        f"- These facet findings are a separate architecture report. Candidate rows contain only existing route membership pairs; independent identity overlap is body {body_candidate_overlap:,}, theme {theme_candidate_overlap:,}. Missing facets never enter candidate route decisions.",
        "",
        "The systemic report and all 19 route before/after counts are in this directory. Runtime cost estimate: 274 static route memberships (about 0.81% of 33,688 catalog backing rows) through the existing index, with no query-time work. Actual build, memory, and latency cost remains unmeasured and is a pre-promotion gate.",
    ]
    (out / "FINAL_RECONCILIATION_SUMMARY.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(summary_out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
