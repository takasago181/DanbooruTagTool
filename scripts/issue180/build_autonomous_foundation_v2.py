#!/usr/bin/env python3
"""Issue #180 autonomous completion foundation v2.

Research-only. Converts the already-reviewed work into a compact, reusable
foundation for one-pass autonomous completion. It deliberately separates:
- current direct authority already accepted by the research master,
- reusable qualifier-family authority,
- variant/nested identity work,
- unqualified roster discovery,
- higher-reasoning/policy exceptions.

No production or accepted Issue #70 source is modified.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parents[2]
A = R / "artifacts/issue180-full-preflight"
D = A / "POST_NORMALIZED_REVIEW"
M1 = D / "MASTER_HOME"
O = D / "MASTER_HOME_V2"
O.mkdir(parents=True, exist_ok=True)

CAT = R / "docs/issue70/data/runtime/issue70_catalog_overlay.csv"
CENSUS = A / "CHARACTER_QUALIFIER_CENSUS.csv"
MASTER1 = M1 / "CHARACTER_HOME_MASTER_V1.csv"
PRIORITY1 = M1 / "UNRESOLVED_PRIORITY_V1.csv"
LEDGER1 = D / "MEGABATCH_AUTHORITY/AUTHORITY_LEDGER_V1.csv"
MAJOR = A / "MAJOR_ROSTER_EXPANSION_V1.csv"
OLD_GLOBAL = A / "GLOBAL_APPROVED_QUALIFIER_HOME_V1.csv"

EXPECTED = 35890

ATTR = {
    "new_year", "summer", "casual", "school_uniform", "female", "male", "young",
    "timeskip", "stand", "racehorse", "human", "character", "cat",
}
ORDINAL_COSTUME = re.compile(r"^[0-9]+(?:st|nd|rd|th)_costume$")
BROAD = {
    "disney", "marvel", "final_fantasy", "idolmaster", "precure", "yu-gi-oh!",
    "nijisanji", "dragon_ball", "mega_man", "tales", "persona", "megami_tensei",
    "zelda", "kirby", "naruto", "neptunia", "nanoha", "x-men", "transformers",
    "mario", "vtuber", "cookie",
}
PIAPRO_POLICY = {
    "hatsune_miku", "kagamine_rin", "kagamine_len", "megurine_luka",
    "meiko_(vocaloid)", "kaito_(vocaloid)",
}

# A Copyright tag can be a real tag without being a valid canonical HOME.
# These families describe collaborations/projects/appearances and therefore
# must never pass the reusable qualifier fast-path by exact-name equality.
NON_HOME_EXACT_FAMILIES = {
    "project_voltage",
}

# Existing Issue #180 product policy prefers a stable canonical root instead
# of title-by-title appearance HOME for these already-reviewed ecosystems.
ROOT_POLICY_REVIEW_HINT_PREFIXES = [
    ("fire_emblem_", "fire_emblem"),
    ("fire_emblem:", "fire_emblem"),
    ("mega_man_", "mega_man_(series)"),
    ("mega_man:", "mega_man_(series)"),
    ("xenoblade_", "xenoblade_chronicles_(series)"),
    ("sekaiju_", "sekaiju_no_meikyuu"),
    ("tales_", "tales_of_(series)"),
    ("kirby_", "kirby_(series)"),
    ("naruto_", "naruto_(series)"),
    ("zelda_", "the_legend_of_zelda"),
    ("sailor_moon_", "bishoujo_senshi_sailor_moon"),
    ("sonic_", "sonic_(series)"),
    ("mario_", "mario_(series)"),
    ("super_mario_", "mario_(series)"),
    ("pikmin_", "pikmin_(series)"),
    ("symphogear_", "senki_zesshou_symphogear"),
]
ROOT_POLICY_REVIEW_HINT_EXACT = {
    "jojolion": "jojo_no_kimyou_na_bouken",
}


def root_policy_review_hint(family: str) -> str:
    if family in ROOT_POLICY_REVIEW_HINT_EXACT:
        return ROOT_POLICY_REVIEW_HINT_EXACT[family]
    for prefix, root in ROOT_POLICY_REVIEW_HINT_PREFIXES:
        if family.startswith(prefix):
            return root
    return ""


ROOT_POLICY_NORMALIZATION = {
    "fate/zero": "fate_(series)",
    "fate/extra": "fate_(series)",
    "fate/apocrypha": "fate_(series)",
    "fate/grand_order": "fate_(series)",
    "fate/prototype": "fate_(series)",
    "fate/stay_night": "fate_(series)",
    "fate/strange_fake": "fate_(series)",
    "fate/grand_order_arcade": "fate_(series)",
    "fate/samurai_remnant": "fate_(series)",
    "pokemon_go": "pokemon",
    "pokemon_masters_ex": "pokemon",
    "pokemon_legends:_z-a": "pokemon",
    "pokemon_adventures": "pokemon",
    "pokemon_pokopia": "pokemon",
    "splatoon_3": "splatoon_(series)",
    "splatoon_raiders": "splatoon_(series)",
}


def read(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"missing required input: {path}")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows and fields is None:
        raise SystemExit(f"cannot infer fields for empty output: {path}")
    fields = fields or list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def is_attribute_family(family: str) -> bool:
    return family in ATTR or bool(ORDINAL_COSTUME.match(family or ""))


def nested_final_qualifier(tag: str, family: str) -> bool:
    if not family:
        return False
    suffix = f"_({family})"
    if not tag.lower().endswith(suffix.lower()):
        return False
    return tag[:-len(suffix)].endswith(")")


def split_final_qualifier(tag: str) -> tuple[str, str]:
    m = re.search(r"_\(([^()]*)\)$", tag)
    return (tag[:m.start()], m.group(1)) if m else ("", "")


def select_base_character(tag: str, family: str, char_by: dict[str, dict[str, str]], predicted_home: dict[str, str]) -> tuple[str, str]:
    """Select a structural base candidate without proving variant officiality.

    For name_(variant)_(ip), prefer name_(ip) when that Character exists.
    For ordinary attribute suffixes, prefer direct suffix removal.
    If multiple plausible existing bases have conflicting confirmed HOMEs,
    return an explicit ambiguity state instead of choosing.
    """
    prefix, outer = split_final_qualifier(tag)
    candidates: list[tuple[str, str]] = []
    if prefix and prefix in char_by:
        candidates.append(("DIRECT_SUFFIX_STRIP", prefix))
    inner_base, inner = split_final_qualifier(prefix) if prefix else ("", "")
    if outer and inner:
        keep_outer = f"{inner_base}_({outer})"
        if keep_outer in char_by:
            candidates.append(("DROP_INNER_VARIANT_KEEP_OUTER", keep_outer))
        if inner_base in char_by:
            candidates.append(("DROP_BOTH_QUALIFIERS", inner_base))

    unique: list[tuple[str, str]] = []
    seen = set()
    for kind, candidate in candidates:
        if candidate not in seen:
            unique.append((kind, candidate))
            seen.add(candidate)
    if not unique:
        return "", "BASE_NOT_FOUND_OR_NONTRIVIAL"

    confirmed = [(kind, candidate, predicted_home[candidate]) for kind, candidate in unique if candidate in predicted_home]
    confirmed_homes = {home for _, _, home in confirmed}
    if len(confirmed_homes) > 1:
        return "", "BASE_CANDIDATE_HOME_CONFLICT"

    if nested_final_qualifier(tag, family) and not is_attribute_family(family):
        preferred_order = ["DROP_INNER_VARIANT_KEEP_OUTER", "DIRECT_SUFFIX_STRIP", "DROP_BOTH_QUALIFIERS"]
    else:
        preferred_order = ["DIRECT_SUFFIX_STRIP", "DROP_INNER_VARIANT_KEEP_OUTER", "DROP_BOTH_QUALIFIERS"]

    if confirmed:
        for kind in preferred_order:
            for ck, candidate, _ in confirmed:
                if ck == kind:
                    return candidate, "BASE_HOME_READY_OFFICIALITY_REVIEW"
    for kind in preferred_order:
        for ck, candidate in unique:
            if ck == kind:
                return candidate, "BASE_EXISTS_HOME_PENDING"
    return "", "BASE_NOT_FOUND_OR_NONTRIVIAL"


def first_float(value: str) -> int:
    try:
        return int(float(value or "0"))
    except ValueError:
        return 0


def main() -> None:
    catalog = read(CAT)
    chars = [r for r in catalog if r.get("category_name") == "Character"]
    copyrights = [r for r in catalog if r.get("category_name") == "Copyright"]
    if len(chars) != EXPECTED:
        raise SystemExit(f"Character population drift: {len(chars)} != {EXPECTED}")
    char_by = {r["canonical_tag"]: r for r in chars}
    if len(char_by) != EXPECTED:
        raise SystemExit("duplicate Character canonical_tag in catalog")
    copyright_by = {r["canonical_tag"]: r for r in copyrights}
    copyright_alias_index: dict[str, set[str]] = defaultdict(set)
    for row in copyrights:
        copyright_alias_index[row["canonical_tag"].lower()].add(row["canonical_tag"])
        for alias in (row.get("aliases", "") or "").split("|"):
            alias = alias.strip().lower()
            if alias:
                copyright_alias_index[alias].add(row["canonical_tag"])
    root_normalizations: Counter[str] = Counter()

    def canonical_root(value: str) -> str:
        value = (value or "").strip()
        if value in copyright_by:
            return value
        hits = copyright_alias_index.get(value.lower(), set())
        if len(hits) == 1:
            root = next(iter(hits))
            root_normalizations[f"{value}->{root}"] += 1
            return root
        if not hits:
            raise SystemExit(f"HOME root absent from Copyright catalog and aliases: {value}")
        raise SystemExit(f"ambiguous Copyright alias HOME root: {value} -> {sorted(hits)}")

    census_rows = read(CENSUS)
    census = {r["canonical_tag"]: r for r in census_rows}
    if len(census) != EXPECTED:
        raise SystemExit("census population drift")
    master1_rows = read(MASTER1)
    master1 = {r["canonical_tag"]: r for r in master1_rows}
    if len(master1) != EXPECTED:
        raise SystemExit("v1 master population drift")
    priority1 = {r["canonical_tag"]: r for r in read(PRIORITY1)}

    ledger1_rows = read(LEDGER1)
    ledger1 = {r["canonical_tag"]: r for r in ledger1_rows}
    major_rows = read(MAJOR)
    major = {r["canonical_tag"]: r for r in major_rows}
    base_direct: list[dict[str, str]] = []
    direct_home: dict[str, str] = {}

    for tag, row in ledger1.items():
        source_home = row.get("home_copyright", "")
        if not source_home:
            raise SystemExit(f"empty v1 ledger home: {tag}")
        home = canonical_root(source_home)
        direct_home[tag] = home
        base_direct.append({
            "canonical_tag": tag,
            "home_copyright": home,
            "authority_scope": "DIRECT_CHARACTER",
            "authority_type": row.get("evidence_type", "") or "V1_REVIEWED_AUTHORITY",
            "evidence_url": row.get("evidence_url", ""),
            "evidence_claim": "Migrated from second-reviewed Issue #180 authority ledger v1",
            "source_provenance": row.get("source_file", "AUTHORITY_LEDGER_V1.csv"),
            "validation_state": "PASS",
            "provenance_quality": "EXPLICIT_EVIDENCE",
            "production_approved": "false",
        })

    migrated_current_master = 0
    for tag, row in master1.items():
        if row.get("final_state") != "HOME_CONFIRMED" or tag in direct_home:
            continue
        source_home = row.get("home_copyright", "")
        if not source_home:
            raise SystemExit(f"empty current-master migrated home: {tag}")
        home = canonical_root(source_home)
        mr = major.get(tag, {})
        direct_home[tag] = home
        migrated_current_master += 1
        base_direct.append({
            "canonical_tag": tag,
            "home_copyright": home,
            "authority_scope": "DIRECT_CHARACTER",
            "authority_type": mr.get("evidence_type", "") or "CURRENT_MASTER_ROSTER_MIGRATION",
            "evidence_url": "",
            "evidence_claim": "Preserved from the currently validated research master; provenance upgrade recommended",
            "source_provenance": "MAJOR_ROSTER_EXPANSION_V1.csv",
            "validation_state": "PASS",
            "provenance_quality": "CURRENT_MASTER_MIGRATION",
            "production_approved": "false",
        })

    v1_confirmed = sum(r.get("final_state") == "HOME_CONFIRMED" for r in master1_rows)
    if len(direct_home) != v1_confirmed:
        raise SystemExit(f"v1 direct migration mismatch: {len(direct_home)} != {v1_confirmed}")

    family_sources: dict[str, list[dict[str, str]]] = defaultdict(list)

    def add_family(family: str, home: str, kind: str, source: str, url: str = "", claim: str = "") -> None:
        family = (family or "").strip().lower()
        home = (home or "").strip()
        if not family or not home:
            return
        home = canonical_root(home)
        family_sources[family].append({
            "family": family,
            "candidate_home": home,
            "source_kind": kind,
            "source_file": source,
            "evidence_url": url or "",
            "evidence_claim": claim or "",
        })

    first_party_specs = [
        (A / "ROOT_REVIEW_BATCH_A_SECOND_REVIEW_V1.csv", "qualifier", "proposed_root"),
        (A / "BATCH_A_REMAINING_7_SECOND_REVIEW_V2.csv", "qualifier", "proposed_root"),
        (A / "P1_P3_AUTHORITY_SECOND_REVIEW_V1.csv", "qualifier", "candidate_root"),
    ]
    for path, family_field, home_field in first_party_specs:
        for row in read(path):
            passed = row.get("second_review") == "PASS" or row.get("authority_decision") == "SECOND_REVIEW_PASS_RESEARCH_ONLY"
            if not passed or not row.get(home_field) or not row.get("official_source_url"):
                continue
            add_family(
                row.get(family_field, ""), row.get(home_field, ""), "FIRST_PARTY_REVIEWED",
                path.name, row.get("official_source_url", ""), row.get("official_source_claim", ""),
            )

    for row in read(A / "GLOBAL_EXACT_COPYRIGHT_SECOND_REVIEW_V1.csv"):
        if row.get("second_review") == "PASS" and row.get("candidate_root_hint"):
            add_family(
                row.get("family", ""), row.get("candidate_root_hint", ""),
                "EXACT_COPYRIGHT_REVIEWED", "GLOBAL_EXACT_COPYRIGHT_SECOND_REVIEW_V1.csv",
                "", "Final qualifier exactly equals a reviewed Copyright catalog root",
            )

    for row in read(A / "POST_EXACT_REVIEW/IP_ROOT_NORMALIZED_SECOND_REVIEW_V1.csv"):
        if row.get("second_review") == "PASS" and row.get("candidate_root_hint"):
            add_family(
                row.get("family", ""), row.get("candidate_root_hint", ""),
                "NORMALIZED_COPYRIGHT_REVIEWED", "IP_ROOT_NORMALIZED_SECOND_REVIEW_V1.csv",
                "", "Unique normalized Copyright candidate from prior review; requires semantic revalidation",
            )

    precedence = {
        "FIRST_PARTY_REVIEWED": 3,
        "EXACT_COPYRIGHT_REVIEWED": 2,
        "NORMALIZED_COPYRIGHT_REVIEWED": 1,
    }
    resolved_family: dict[str, dict[str, str]] = {}
    family_conflicts: list[str] = []
    for family, records in family_sources.items():
        homes = {r["candidate_home"] for r in records}
        if len(homes) != 1:
            family_conflicts.append(f"{family}:{'|'.join(sorted(homes))}")
            continue
        chosen = max(records, key=lambda r: precedence[r["source_kind"]])
        resolved_family[family] = chosen
    if family_conflicts:
        raise SystemExit("family authority conflicts: " + ", ".join(family_conflicts[:20]))

    old_confirmed_rows = [r for r in read(OLD_GLOBAL) if r.get("home_state") == "HOME_CONFIRMED_RESEARCH"]
    old_counts = Counter((r.get("final_qualifier") or "").strip().lower() for r in old_confirmed_rows)
    if len(old_counts) != 1456:
        raise SystemExit(f"legacy family count drift: {len(old_counts)} != 1456")
    if set(old_counts) != set(resolved_family):
        missing = sorted(set(old_counts) - set(resolved_family))
        extra = sorted(set(resolved_family) - set(old_counts))
        raise SystemExit(f"legacy family provenance mismatch missing={missing[:10]} extra={extra[:10]}")

    norm_index: dict[str, set[str]] = defaultdict(set)
    for row in copyrights:
        values = [row.get("canonical_tag", ""), row.get("display_ja", "")]
        values += (row.get("aliases", "") or "").split("|")
        values += (row.get("search_ja", "") or "").split("|")
        for value in values:
            n = norm(value)
            if n:
                norm_index[n].add(row["canonical_tag"])

    fast_family_home: dict[str, str] = {}
    effective_family: dict[str, dict[str, str]] = {}
    for family, row in resolved_family.items():
        effective = dict(row)
        if family in ROOT_POLICY_NORMALIZATION:
            effective["candidate_home"] = canonical_root(ROOT_POLICY_NORMALIZATION[family])
            effective["source_kind"] = "POLICY_ROOT_NORMALIZATION"
            effective["source_file"] = "docs/issue180/AUTHORITY_POLICY_V1.md"
            effective["evidence_claim"] = "Existing Issue #180 canonical-root product policy"
        elif row["source_kind"] == "EXACT_COPYRIGHT_REVIEWED":
            hinted_root = root_policy_review_hint(family)
            if hinted_root:
                effective["candidate_home"] = canonical_root(hinted_root)
                effective["source_kind"] = "ROOT_POLICY_REVIEW_HINT"
                effective["source_file"] = "Issue #180 previously reviewed canonical franchise-root mappings"
                effective["evidence_claim"] = "Candidate-only canonical-root review hint; not authority until autonomous review"
        effective_family[family] = effective
        if family in NON_HOME_EXACT_FAMILIES:
            continue
        if effective["source_kind"] in {"FIRST_PARTY_REVIEWED", "EXACT_COPYRIGHT_REVIEWED", "POLICY_ROOT_NORMALIZATION"}:
            fast_family_home[family] = effective["candidate_home"]

    predicted_home = dict(direct_home)
    fast_applied = Counter()
    for tag, row in master1.items():
        if tag in predicted_home or row.get("final_state") != "HOME_UNRESOLVED":
            continue
        family = (census[tag].get("final_qualifier") or "").strip().lower()
        if not family or is_attribute_family(family) or nested_final_qualifier(tag, family):
            continue
        home = fast_family_home.get(family, "")
        if home:
            predicted_home[tag] = home
            fast_applied[effective_family[family]["source_kind"]] += 1

    unresolved_tags = [t for t in master1 if t not in predicted_home]
    unresolved_family_counts = Counter()
    unresolved_nested_counts = Counter()
    for tag in unresolved_tags:
        family = (census[tag].get("final_qualifier") or "").strip().lower()
        if not family:
            continue
        if is_attribute_family(family) or nested_final_qualifier(tag, family):
            unresolved_nested_counts[family] += 1
        else:
            unresolved_family_counts[family] += 1

    family_registry: list[dict[str, str]] = []
    for family, count in sorted(unresolved_family_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        existing = effective_family.get(family)
        exact = family if family in copyright_by else ""
        normalized = sorted(norm_index.get(norm(family), set())) if family else []
        candidate = ""
        basis = ""
        source_file = ""
        evidence_url = ""
        if existing:
            candidate = existing["candidate_home"]
            basis = existing["source_kind"]
            source_file = existing["source_file"]
            evidence_url = existing["evidence_url"]
            if family in NON_HOME_EXACT_FAMILIES:
                lane = "HIGHER_REASONING_NON_HOME_SEMANTICS"
            elif basis == "NORMALIZED_COPYRIGHT_REVIEWED":
                lane = "FAST_REVALIDATE_NORMALIZATION"
            elif basis == "ROOT_POLICY_REVIEW_HINT":
                lane = "FAST_ROOT_POLICY_REVIEW"
            else:
                lane = "ALREADY_FASTPATH_SHOULD_NOT_REMAIN"
        elif family in BROAD:
            candidate = exact or (normalized[0] if len(normalized) == 1 else "")
            basis = "BROAD_OR_UMBRELLA"
            lane = "HIGHER_REASONING_BROAD"
        elif exact:
            candidate = exact
            basis = "NEW_EXACT_COPYRIGHT_CANDIDATE"
            lane = "FAST_REVIEW_NEW_EXACT"
        elif len(normalized) == 1:
            candidate = normalized[0]
            basis = "NEW_UNIQUE_NORMALIZED_CANDIDATE"
            lane = "REVIEW_NORMALIZATION"
        elif len(normalized) > 1:
            candidate = "|".join(normalized)
            basis = "AMBIGUOUS_NORMALIZED_CANDIDATE"
            lane = "HIGHER_REASONING_AMBIGUOUS"
        else:
            basis = "NO_CATALOG_ROOT_HINT"
            lane = "DISCOVERY_RESEARCH"
        family_registry.append({
            "family": family,
            "character_rows": str(count),
            "nested_rows_separate": str(unresolved_nested_counts.get(family, 0)),
            "candidate_home": candidate,
            "candidate_basis": basis,
            "source_file": source_file,
            "evidence_url": evidence_url,
            "work_lane": lane,
            "production_approved": "false",
        })

    variant_rows: list[dict[str, str]] = []
    for tag in unresolved_tags:
        family = (census[tag].get("final_qualifier") or "").strip().lower()
        is_nested = nested_final_qualifier(tag, family)
        if not family or (not is_attribute_family(family) and not is_nested):
            continue
        base, state = select_base_character(tag, family, char_by, predicted_home)
        base_home = predicted_home.get(base, "") if base else ""
        prefix, outer = split_final_qualifier(tag)
        _, inner = split_final_qualifier(prefix) if prefix else ("", "")
        variant_qualifier = inner if is_nested and inner else family
        variant_rows.append({
            "canonical_tag": tag,
            "display_ja": char_by[tag].get("display_ja", ""),
            "final_qualifier": family,
            "variant_qualifier": variant_qualifier,
            "outer_ip_qualifier": family if is_nested else "",
            "variant_shape": "NESTED_FINAL_QUALIFIER" if is_nested else "ATTRIBUTE_OR_VARIANT",
            "base_character": base,
            "base_home_candidate": base_home,
            "work_state": state,
            "post_count": str(first_float(char_by[tag].get("post_count", "0"))),
            "production_approved": "false",
        })
    variant_rows.sort(key=lambda r: (-int(r["post_count"]), r["canonical_tag"]))

    unqualified_rows: list[dict[str, str]] = []
    for tag in unresolved_tags:
        family = (census[tag].get("final_qualifier") or "").strip().lower()
        if family:
            continue
        cr = char_by[tag]
        p1 = priority1.get(tag, {})
        related = (
            cr.get("related_copyright", "") or cr.get("RelatedCopyright", "")
            or cr.get("relatedCopyright", "") or cr.get("old_related_copyright", "")
        )
        primary_raw = (related.split("|")[0].strip() if related else "")
        primary_root = ""
        if primary_raw:
            if primary_raw in copyright_by:
                primary_root = primary_raw
            else:
                hits = copyright_alias_index.get(primary_raw.lower(), set())
                if len(hits) == 1:
                    primary_root = next(iter(hits))
        state = "DIRECT_ROSTER_REVIEW" if p1.get("roster_candidate_state") == "UNIQUE_IDENTITY_OVERLAP_CANDIDATE" else "ROSTER_DISCOVERY"
        if tag in PIAPRO_POLICY:
            state = "POLICY_DECISION_REQUIRED_PIAPRO"
        unqualified_rows.append({
            "canonical_tag": tag,
            "display_ja": cr.get("display_ja", ""),
            "post_count": str(first_float(cr.get("post_count", "0"))),
            "search_ja": cr.get("search_ja", ""),
            "aliases": cr.get("aliases", ""),
            "support_only_old_relation_hint": related,
            "discovery_primary_raw": primary_raw,
            "discovery_primary_root_hint": primary_root,
            "roster_identity_overlap": p1.get("roster_candidate_state", ""),
            "work_state": state,
            "production_approved": "false",
        })
    unqualified_rows.sort(key=lambda r: (-int(r["post_count"]), r["canonical_tag"]))

    unqualified_groups: list[dict[str, str]] = []
    grouped_unqualified: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in unqualified_rows:
        key = row["discovery_primary_root_hint"] or row["discovery_primary_raw"] or "__NO_DISCOVERY_HINT__"
        grouped_unqualified[key].append(row)
    for key, rows in sorted(grouped_unqualified.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        top = sorted(rows, key=lambda r: (-int(r["post_count"]), r["canonical_tag"]))[:8]
        unqualified_groups.append({
            "discovery_group": key,
            "character_rows": str(len(rows)),
            "canonical_root_hint": rows[0]["discovery_primary_root_hint"] if key != "__NO_DISCOVERY_HINT__" else "",
            "support_only": "true",
            "top_character_samples": "|".join(r["canonical_tag"] for r in top),
            "top_post_count": top[0]["post_count"] if top else "0",
            "work_lane": "ROSTER_GROUP_RESEARCH" if key != "__NO_DISCOVERY_HINT__" else "UNQUALIFIED_NO_HINT",
            "production_approved": "false",
        })

    variant_groups: list[dict[str, str]] = []
    grouped_variants: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in variant_rows:
        group_key = (
            row["base_home_candidate"] or "__BASE_HOME_PENDING__",
            row["variant_qualifier"],
            row["outer_ip_qualifier"],
            row["work_state"],
        )
        grouped_variants[group_key].append(row)
    for (base_home, variant_qualifier, outer_ip, state), rows in sorted(grouped_variants.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        top = sorted(rows, key=lambda r: (-int(r["post_count"]), r["canonical_tag"]))[:8]
        variant_groups.append({
            "base_home_group": "" if base_home == "__BASE_HOME_PENDING__" else base_home,
            "variant_qualifier": variant_qualifier,
            "outer_ip_qualifier": outer_ip,
            "work_state": state,
            "character_rows": str(len(rows)),
            "top_character_samples": "|".join(r["canonical_tag"] for r in top),
            "work_lane": "VARIANT_PATTERN_REVIEW",
            "production_approved": "false",
        })

    higher: list[dict[str, str]] = []
    for row in family_registry:
        if row["work_lane"].startswith("HIGHER_REASONING"):
            higher.append({
                "scope": "FAMILY",
                "key": row["family"],
                "candidate_home": row["candidate_home"],
                "reason": row["work_lane"],
                "character_rows": row["character_rows"],
            })
    for tag in sorted(PIAPRO_POLICY):
        if tag in char_by and tag not in predicted_home:
            higher.append({
                "scope": "CHARACTER",
                "key": tag,
                "candidate_home": "vocaloid",
                "reason": "POLICY_DECISION_REQUIRED_PIAPRO",
                "character_rows": "1",
            })

    provenance_rows: list[dict[str, str]] = []
    for family in sorted(effective_family):
        r = effective_family[family]
        source_kind = r["source_kind"]
        if family in NON_HOME_EXACT_FAMILIES:
            state = "BLOCKED_NON_HOME_SEMANTICS"
        else:
            state = "PASS_FASTPATH" if source_kind in {"FIRST_PARTY_REVIEWED", "EXACT_COPYRIGHT_REVIEWED", "POLICY_ROOT_NORMALIZATION"} else "NEEDS_FAST_REVALIDATION"
        provenance_rows.append({
            "family": family,
            "candidate_home": r["candidate_home"],
            "legacy_character_rows": str(old_counts[family]),
            "authority_basis": source_kind,
            "source_file": r["source_file"],
            "evidence_url": r["evidence_url"],
            "foundation_state": state,
            "production_approved": "false",
        })

    write_csv(O / "BASE_DIRECT_AUTHORITY_V2.csv", base_direct)
    write_csv(O / "FAMILY_AUTHORITY_PROVENANCE_V2.csv", provenance_rows)
    write_csv(O / "FAMILY_WORK_QUEUE_V2.csv", family_registry)
    write_csv(O / "VARIANT_WORK_QUEUE_V2.csv", variant_rows)
    write_csv(O / "UNQUALIFIED_WORK_QUEUE_V2.csv", unqualified_rows)
    write_csv(O / "UNQUALIFIED_DISCOVERY_GROUPS_V2.csv", unqualified_groups)
    write_csv(O / "VARIANT_PATTERN_GROUPS_V2.csv", variant_groups)
    write_csv(
        O / "NEEDS_HIGHER_REASONING_REVIEW_V2.csv", higher,
        ["scope", "key", "candidate_home", "reason", "character_rows"],
    )

    lane_counts = Counter(r["work_lane"] for r in family_registry)
    variant_state_counts = Counter(r["work_state"] for r in variant_rows)
    unqualified_state_counts = Counter(r["work_state"] for r in unqualified_rows)
    summary = {
        "character_population": EXPECTED,
        "v1_confirmed_preserved": len(direct_home),
        "v1_ledger_rows": len(ledger1_rows),
        "current_master_roster_migrations": migrated_current_master,
        "legacy_family_mappings": len(resolved_family),
        "legacy_first_party_families": sum(r["source_kind"] == "FIRST_PARTY_REVIEWED" for r in resolved_family.values()),
        "legacy_exact_families": sum(r["source_kind"] == "EXACT_COPYRIGHT_REVIEWED" for r in resolved_family.values()),
        "legacy_normalized_families": sum(r["source_kind"] == "NORMALIZED_COPYRIGHT_REVIEWED" for r in resolved_family.values()),
        "policy_root_normalized_families": len(ROOT_POLICY_NORMALIZATION),
        "root_policy_review_hint_families": sum(r["source_kind"] == "ROOT_POLICY_REVIEW_HINT" for r in effective_family.values()),
        "non_home_exact_families_blocked": len(NON_HOME_EXACT_FAMILIES),
        "fastpath_family_rows_applied": sum(fast_applied.values()),
        "fastpath_by_basis": dict(fast_applied),
        "foundation_confirmed_before_autonomous_decisions": len(predicted_home),
        "foundation_unresolved_before_autonomous_decisions": EXPECTED - len(predicted_home),
        "family_work_rows": sum(int(r["character_rows"]) for r in family_registry),
        "family_work_families": len(family_registry),
        "family_work_lanes": dict(lane_counts),
        "variant_work_rows": len(variant_rows),
        "variant_work_states": dict(variant_state_counts),
        "unqualified_work_rows": len(unqualified_rows),
        "unqualified_work_states": dict(unqualified_state_counts),
        "unqualified_discovery_groups": len(unqualified_groups),
        "unqualified_rows_with_discovery_hint": sum(r["discovery_primary_raw"] != "" for r in unqualified_rows),
        "variant_pattern_groups": len(variant_groups),
        "higher_reasoning_queue_rows": len(higher),
        "multi_home_conflicts": 0,
        "missing_copyright_roots": 0,
        "canonical_root_normalizations": dict(root_normalizations),
        "canonical_root_normalization_events": sum(root_normalizations.values()),
        "accepted_source_modified": False,
        "production_modified": False,
    }
    if summary["foundation_confirmed_before_autonomous_decisions"] + summary["family_work_rows"] + summary["variant_work_rows"] + summary["unqualified_work_rows"] != EXPECTED:
        raise SystemExit("foundation partition accounting failure")
    if summary["foundation_confirmed_before_autonomous_decisions"] < 9000:
        raise SystemExit("unexpected loss of safe fast-path coverage")
    (O / "autonomous_foundation_v2_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
