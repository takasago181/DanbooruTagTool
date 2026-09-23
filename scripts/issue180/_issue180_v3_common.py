"""Shared deterministic helpers for the research-only Issue #180 v3 pipeline."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts/issue180-v3"
DOCS_OUT = ROOT / "docs/issue180/v3/reports"
CATALOG = ROOT / "docs/issue70/data/runtime/issue70_catalog_overlay.csv"
ORIGIN = ROOT / "docs/issue180/evidence/ISSUE179_ORIGIN_HANDOFF_V1.csv"
ORIGIN_META = ROOT / "docs/issue180/evidence/ISSUE179_ORIGIN_HANDOFF_V1.meta.json"
EVIDENCE_DIR = ROOT / "docs/issue180/evidence"
DECISION_DIR = ROOT / "docs/issue180/autonomous/decisions"
V3_SEED = ROOT / "docs/issue180/v3/migrated_evidence_seed_v3.csv"
V3_BASELINE = ROOT / "docs/issue180/v3/v2_confirmed_baseline_v3.csv"
V3_MIGRATION_MANIFEST = ROOT / "docs/issue180/v3/MIGRATION_PROVENANCE_V3.json"
V3_PRE_REPAIR_GAP = ROOT / "docs/issue180/v3/MIGRATION_GAP_BEFORE_REPAIR_V3.csv"
CHARACTER_CATEGORY = "4"
COPYRIGHT_CATEGORY = "3"
FINAL_STATES = {"HOME_CONFIRMED", "HOME_UNRESOLVED", "NOT_OFFICIAL_CHARACTER"}
STRUCTURAL_FAMILY_BLOCKS = {"collab", "collaboration", "crossover", "cross_over", "company", "platform", "event", "costume", "attribute", "hololive"}
DECISION_FILES = (
    "direct_and_exceptions_v2.csv",
    "discovery_roster_reviews_v2.csv",
    "family_terminal_reviews_v2.csv",
    "roster_verified_v4.csv",
    "variant_pattern_reviews_v2.csv",
    "variants_verified_v4.csv",
)

def read_csv(path: Path) -> list[dict[str, str]]:
    csv.field_size_limit(16 * 1024 * 1024)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]

def write_csv(path: Path, rows: Iterable[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def relpath(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()

def load_catalog() -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, dict[str, str]]]:
    rows = read_csv(CATALOG)
    characters = [r for r in rows if r.get("category") == CHARACTER_CATEGORY]
    copyrights = [r for r in rows if r.get("category") == COPYRIGHT_CATEGORY]
    by_tag = {r["canonical_tag"]: r for r in characters}
    if len(by_tag) != len(characters):
        raise ValueError("Issue #70 Character source has duplicate canonical tags")
    if len({r["canonical_tag"] for r in copyrights}) != len(copyrights):
        raise ValueError("Issue #70 Copyright source has duplicate canonical tags")
    return characters, copyrights, by_tag

def load_decisions() -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for name in DECISION_FILES:
        path = DECISION_DIR / name
        if not path.exists():
            continue
        for line, row in enumerate(read_csv(path), start=2):
            row["_source_file"] = relpath(path)
            row["_source_line"] = str(line)
            out.append(row)
    return out

def canonical_family_candidates(characters: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return *candidate-only* family memberships from the terminal tag qualifier."""
    rows: list[dict[str, str]] = []
    for character in characters:
        tag = character["canonical_tag"]
        if not tag.endswith(")") or "_(" not in tag:
            continue
        family = tag.rsplit("_(", 1)[1][:-1]
        if family:
            rows.append({
                "subject_type": "Character", "subject_key": tag,
                "relation_type": "MEMBER_OF", "object_type": "Family", "object_key": family,
                "review_state": "CANDIDATE", "evidence_id": "",
                "derivation": "terminal qualifier parse; candidate only, not authority",
            })
    return rows

def safe_structural_variant_bases(tag: str, character_keys: set[str],
                                 reviewed_family_homes: dict[str, set[str]], policy: dict,
                                 copyright_alias_roots: dict[str, set[str]] | None = None) -> list[tuple[str, str, str]]:
    """Return conservative (base, variant_qualifier, outer_family) triples.

    This authorizes HOME inheritance, not claims about official costume status. Nested
    variants need an exact catalog/reviewed outer HOME qualifier. A single terminal
    modifier can inherit from an exact accepted-catalog base when that base is unique;
    any exact HOME-like or blocked qualifier must not contradict that base.
    """
    match = re.fullmatch(r"(.+)_\(([^()]*)\)_\(([^()]*)\)", tag)
    single = re.fullmatch(r"(.+)_\(([^()]*)\)", tag)
    is_single_base = bool(single and tag.count("_(") == 1 and single.group(1) in character_keys)
    if not match and not is_single_base:
        return []
    policy_sets = [
        set(str(x).lower() for x in policy.get("attribute_families", [])),
        set(str(x).lower() for x in policy.get("variant_qualifier_families", [])),
        set(str(x).lower() for x in policy.get("non_home_families", [])),
        set(str(x).lower() for x in policy.get("broad_families", [])),
    ]
    blocked = set().union(*policy_sets) | STRUCTURAL_FAMILY_BLOCKS
    root_map = {k.lower(): set(v) for k, v in reviewed_family_homes.items()}
    for k, v in (copyright_alias_roots or {}).items():
        root_map.setdefault(k.lower(), set()).update(v)
    options: set[tuple[str, str, str]] = set()
    if is_single_base:
        stem, modifier = single.groups()
        modifier_key = modifier.lower()
        blocked_single = (STRUCTURAL_FAMILY_BLOCKS
                          | set(str(x).lower() for x in policy.get("broad_families", []))
                          | set(str(x).lower() for x in policy.get("non_home_families", [])))
        roots = root_map.get(modifier_key, set())
        if (modifier_key not in blocked_single
                and (not roots or len(roots) == 1)):
            options.add((stem, modifier, modifier if roots else ""))
        return sorted(options)
    if not match:
        return []
    stem, first, second = match.groups()
    for outer, modifier in ((second, first), (first, second)):
        outer_key, modifier_key = outer.lower(), modifier.lower()
        homes = root_map.get(outer_key, set())
        other_homes = root_map.get(modifier_key, set())
        if (len(homes) != 1 or outer_key in blocked or modifier_key in STRUCTURAL_FAMILY_BLOCKS
                or modifier_key in set(policy_sets[2]) | set(policy_sets[3])):
            continue
        if other_homes and other_homes != homes:
            continue
        base = f"{stem}_({outer})"
        if base in character_keys:
            options.add((base, modifier, outer))
    return sorted(options)

def safe_terminal_family_membership(tag: str, family: str, family_homes: dict[str, set[str]], policy: dict,
                                    copyright_alias_roots: dict[str, set[str]] | None = None) -> bool:
    """Validate an exact terminal work qualifier without overriding collision signals."""
    qualifiers = [x.lower() for x in re.findall(r"_\(([^()]*)\)", tag.lower())]
    family_key = family.lower()
    if not qualifiers or qualifiers[-1] != family_key or len(family_homes.get(family_key, set())) != 1:
        return False
    blocked = STRUCTURAL_FAMILY_BLOCKS
    broad = {str(x).lower() for x in policy.get("broad_families", [])}
    non_home = {str(x).lower() for x in policy.get("non_home_families", [])}
    attributes = {str(x).lower() for x in policy.get("attribute_families", [])}
    variants = {str(x).lower() for x in policy.get("variant_qualifier_families", [])}
    if family_key in blocked | broad | non_home | attributes | variants:
        return False
    outer_home = family_homes[family_key]
    all_homes = {k.lower(): set(v) for k, v in family_homes.items()}
    for key, value in (copyright_alias_roots or {}).items():
        all_homes.setdefault(key.lower(), set()).update(value)
    for qualifier in qualifiers[:-1]:
        if qualifier in blocked | broad | non_home:
            return False
        other = all_homes.get(qualifier, set())
        if other and other != outer_home:
            return False
    return True

def exact_base_home_conflicts(tag: str, family_home: str, character_keys: set[str],
                              direct_home_roots: dict[str, set[str]]) -> bool:
    """Reject family inheritance when an exact existing base has a different direct HOME."""
    if "_(" not in tag:
        return False
    base = tag.rsplit("_(", 1)[0]
    roots = direct_home_roots.get(base, set()) if base in character_keys else set()
    return bool(roots) and roots != {family_home}

def is_valid_citation(url: str, claim: str) -> bool:
    u = (url or "").strip().lower()
    c = (claim or "").strip()
    return (u.startswith("https://") or u.startswith("http://")) and len(c) >= 35

def evidence_id(subject_type: str, subject: str, relation: str, object_key: str,
                authority_type: str, url: str, claim: str) -> str:
    # Provenance file/line is deliberately excluded: identical source facts retain the same ID.
    parts = [subject_type, subject, relation, object_key, authority_type,
             (url or "").strip(), " ".join((claim or "").split())]
    return "ev3-" + sha256_text("\x1f".join(parts))[:24]

def select_home(paths: list[dict[str, object]]) -> tuple[str, list[str], list[dict[str, object]]]:
    """Return unique HOME only when every validated path agrees; never score away conflicts."""
    homes = sorted({str(p["home"]) for p in paths})
    if len(homes) != 1:
        return "", homes, []
    rank = {"DIRECT_HOME": 0, "FAMILY_HOME": 1, "VARIANT_INHERITANCE": 2}
    same = [p for p in paths if p["home"] == homes[0]]
    same.sort(key=lambda p: (rank.get(str(p.get("kind", "")), 99), tuple(p.get("evidence_ids", []))))
    return homes[0], homes, same
