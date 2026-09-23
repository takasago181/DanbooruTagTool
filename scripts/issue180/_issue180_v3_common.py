"""Shared deterministic helpers for the research-only Issue #180 v3 pipeline."""
from __future__ import annotations

import csv
import hashlib
import json
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
