#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "docs/issue70/audit"
AUTO = ROOT / "docs/issue70/automation"
CYCLES = AUTO / "cycles"
CURRENT = AUTO / "CURRENT_MANIFEST.json"
REVIEWED = AUTO / "REVIEWED_UNRESOLVED.csv"
TMP = ROOT / "artifacts/issue70-parallel-manifest"

FINAL = {"KEEP", "FIX_DISPLAY", "FIX_SEARCH", "FIX_BOTH"}
LANE_COUNT = 5
CANDIDATES_PER_LANE = 60
BASE_TARGET = 40
PREFERENCES = {
    1: ["Copyright", "Character", "Artist"],
    2: ["Copyright", "Character", "Artist"],
    3: ["Character", "Copyright", "Artist"],
    4: ["Character", "Artist", "Copyright"],
    5: ["Artist", "Character", "Copyright"],
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def census_rows() -> list[dict[str, str]]:
    if TMP.exists():
        shutil.rmtree(TMP)
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/issue70/audit_semantic_risk_v3.py"),
            "--out",
            str(TMP),
            "--sample-per-category",
            "300",
        ],
        cwd=ROOT,
        check=True,
    )
    return read_csv(TMP / "audit_ledger_template.csv")


def effective_unresolved() -> tuple[list[dict[str, object]], dict[str, object]]:
    progress_path = AUDIT / "EXTERNAL_PROGRESS_LIVE.json"
    progress_bytes = progress_path.read_bytes()
    progress = json.loads(progress_bytes.decode("utf-8"))

    assert progress["production_modified"] is False
    assert progress["conflicted_external_rows"] == 0

    ledger = census_rows()
    by_id = {r["row_id"]: r for r in ledger}

    external: dict[str, dict[str, object]] = {}
    for path in sorted(AUDIT.glob("*.csv")):
        if path.name.startswith("external_resolution_") or "diagnostic" in path.name:
            continue
        try:
            rows = read_csv(path)
        except Exception:
            continue
        for row in rows:
            rid = (row.get("row_id") or "").strip()
            verdict = (row.get("audit_verdict") or "").strip()
            if rid not in by_id or verdict != "NEEDS_EXTERNAL_CHECK":
                continue
            l = by_id[rid]
            external[rid] = {
                "row_id": rid,
                "category": (l.get("category_name") or "").strip(),
                "canonical_tag": (l.get("canonical_tag") or row.get("canonical_tag") or "").strip(),
                "post_count": int(l.get("post_count") or row.get("post_count") or 0),
                "display_ja": (l.get("display_ja") or row.get("display_ja") or "").strip(),
                "search_ja": (l.get("search_ja") or row.get("search_ja") or "").strip(),
                "translation_note": (l.get("translation_note") or row.get("translation_note") or "").strip(),
                "primary_source_file": path.name,
            }

    observations: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for path in sorted(AUDIT.glob("external_resolution_*.csv")):
        try:
            rows = read_csv(path)
        except Exception:
            continue
        for row in rows:
            rid = (row.get("row_id") or "").strip()
            verdict = (row.get("audit_verdict") or "").strip()
            if rid not in external or verdict not in FINAL:
                continue
            observations[rid].append(
                (
                    verdict,
                    (row.get("proposed_display_ja") or "").strip(),
                    (row.get("proposed_search_ja") or "").strip(),
                )
            )

    resolved: set[str] = set()
    conflicts: dict[str, list[tuple[str, str, str]]] = {}
    for rid, entries in observations.items():
        unique = set(entries)
        if len(unique) == 1:
            resolved.add(rid)
        elif len(unique) > 1:
            conflicts[rid] = sorted(unique)

    assert not conflicts, f"external resolution conflicts: {conflicts}"

    unresolved = [row for rid, row in external.items() if rid not in resolved]
    unresolved.sort(key=lambda r: (-int(r["post_count"]), str(r["row_id"])))

    assert len(external) == progress["initial_external_rows"], (len(external), progress["initial_external_rows"])
    assert len(resolved) == progress["resolved_external_rows"], (len(resolved), progress["resolved_external_rows"])
    assert len(unresolved) == progress["remaining_external_rows"], (len(unresolved), progress["remaining_external_rows"])

    by_cat: dict[str, int] = defaultdict(int)
    for row in unresolved:
        by_cat[str(row["category"])] += 1
    assert dict(sorted(by_cat.items())) == progress["remaining_by_category"], (
        dict(sorted(by_cat.items())),
        progress["remaining_by_category"],
    )

    return unresolved, {
        "progress": progress,
        "progress_sha256": sha256_bytes(progress_bytes),
    }


def reviewed_unresolved() -> tuple[dict[str, dict[str, str]], str]:
    if not REVIEWED.exists():
        return {}, hashlib.sha256(b"").hexdigest()
    raw = REVIEWED.read_bytes()
    try:
        rows = read_csv(REVIEWED)
    except Exception:
        rows = []
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        rid = (row.get("row_id") or "").strip()
        if rid:
            out[rid] = row
    return out, sha256_bytes(raw)


def seed_shortlists(unresolved_by_tag: dict[str, dict[str, object]]) -> dict[str, dict[str, str]]:
    seeds: dict[str, dict[str, str]] = {}
    for path in sorted(AUDIT.glob("BATCH*_VERIFIED_SHORTLIST_*.csv")):
        try:
            rows = read_csv(path)
        except Exception:
            continue
        for row in rows:
            tag = (row.get("canonical_tag") or "").strip()
            if tag not in unresolved_by_tag:
                continue
            if (row.get("status") or "").strip() != "VERIFIED_SHORTLIST":
                continue
            seeds[tag] = {
                "source": path.name,
                "provisional_verdict": (row.get("provisional_verdict") or "").strip(),
                "proposed_display_ja": (row.get("proposed_display_ja") or "").strip(),
                "proposed_search_ja": (row.get("proposed_search_ja") or "").strip(),
                "evidence_ref": (row.get("evidence_ref") or "").strip(),
                "audit_note": (row.get("audit_note") or "").strip(),
            }
    return seeds


def next_cycle_id() -> str:
    CYCLES.mkdir(parents=True, exist_ok=True)
    nums = []
    for p in CYCLES.glob("cycle-*"):
        if not p.is_dir():
            continue
        try:
            nums.append(int(p.name.split("-", 1)[1]))
        except Exception:
            pass
    n = max(nums, default=0) + 1
    return f"cycle-{n:04d}"


def main() -> None:
    unresolved, state = effective_unresolved()
    progress = state["progress"]
    progress_hash = str(state["progress_sha256"])
    reviewed, reviewed_hash = reviewed_unresolved()
    assignment_state_hash = hashlib.sha256(f"{progress_hash}:{reviewed_hash}".encode("utf-8")).hexdigest()

    if CURRENT.exists():
        try:
            current = json.loads(CURRENT.read_text(encoding="utf-8"))
        except Exception:
            current = {}
        current_assignment_hash = current.get("assignment_state_sha256")
        if current_assignment_hash == assignment_state_hash:
            print(json.dumps({
                "created": False,
                "reason": "manifest already exists for current assignment state",
                "cycle_id": current.get("cycle_id"),
                "remaining": progress["remaining_external_rows"],
            }, ensure_ascii=False))
            return
        if current_assignment_hash is None and current.get("progress_sha256") == progress_hash:
            print(json.dumps({
                "created": False,
                "reason": "legacy current manifest still owns unchanged external progress",
                "cycle_id": current.get("cycle_id"),
                "remaining": progress["remaining_external_rows"],
            }, ensure_ascii=False))
            return

    unresolved_by_tag = {str(r["canonical_tag"]): r for r in unresolved}
    seeds = seed_shortlists(unresolved_by_tag)
    for row in unresolved:
        row["seed"] = seeds.get(str(row["canonical_tag"]))
        row["reviewed_unresolved"] = reviewed.get(str(row["row_id"]))

    by_category: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in unresolved:
        by_category[str(row["category"])].append(row)

    for category in by_category:
        by_category[category].sort(
            key=lambda r: (
                0 if r.get("seed") else 1,
                1 if r.get("reviewed_unresolved") else 0,
                int((r.get("reviewed_unresolved") or {}).get("review_count") or 0),
                -int(r["post_count"]),
                str(r["row_id"]),
            )
        )

    used: set[str] = set()
    lane_payloads: dict[str, dict[str, object]] = {}

    for lane in range(1, LANE_COUNT + 1):
        chosen: list[dict[str, object]] = []
        for category in PREFERENCES[lane]:
            for row in by_category.get(category, []):
                rid = str(row["row_id"])
                if rid in used:
                    continue
                chosen.append(row)
                used.add(rid)
                if len(chosen) >= CANDIDATES_PER_LANE:
                    break
            if len(chosen) >= CANDIDATES_PER_LANE:
                break

        seeded_count = sum(1 for row in chosen if row.get("seed"))
        reviewed_count = sum(1 for row in chosen if row.get("reviewed_unresolved"))
        target = min(len(chosen), max(BASE_TARGET, seeded_count)) if chosen else 0
        lane_payloads[str(lane)] = {
            "lane": lane,
            "candidate_count": len(chosen),
            "target_resolutions": target,
            "seeded_count": seeded_count,
            "reviewed_unresolved_count": reviewed_count,
            "category_preference": PREFERENCES[lane],
            "candidates": chosen,
        }

    cycle_id = next_cycle_id()
    authority_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    manifest = {
        "format_version": 2,
        "issue": 70,
        "cycle_id": cycle_id,
        "authority_base_sha": authority_sha,
        "progress_sha256": progress_hash,
        "reviewed_unresolved_sha256": reviewed_hash,
        "assignment_state_sha256": assignment_state_hash,
        "progress_snapshot": {
            "initial_external_rows": progress["initial_external_rows"],
            "resolved_external_rows": progress["resolved_external_rows"],
            "remaining_external_rows": progress["remaining_external_rows"],
            "remaining_by_category": progress["remaining_by_category"],
            "conflicted_external_rows": progress["conflicted_external_rows"],
            "production_modified": progress["production_modified"],
        },
        "lane_count": LANE_COUNT,
        "candidate_count_per_lane": CANDIDATES_PER_LANE,
        "base_target_resolutions_per_lane": BASE_TARGET,
        "assigned_unique_rows": len(used),
        "reviewed_unresolved_registry_rows": len(reviewed),
        "lanes": lane_payloads,
    }

    cycle_dir = CYCLES / cycle_id
    cycle_dir.mkdir(parents=True, exist_ok=True)
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    (cycle_dir / "MANIFEST.json").write_text(manifest_text, encoding="utf-8")
    AUTO.mkdir(parents=True, exist_ok=True)
    CURRENT.write_text(manifest_text, encoding="utf-8")

    fields = [
        "row_id", "canonical_tag", "category", "post_count", "display_ja", "search_ja",
        "translation_note", "primary_source_file", "seed_shortlist_source",
        "seed_provisional_verdict", "seed_proposed_display_ja", "seed_proposed_search_ja",
        "seed_evidence_ref", "seed_audit_note",
        "reviewed_unresolved", "review_count", "last_review_cycle", "last_review_reason",
    ]

    for lane, payload in lane_payloads.items():
        lane_dir = cycle_dir / f"lane-{lane}"
        lane_dir.mkdir(parents=True, exist_ok=True)
        with (lane_dir / "ASSIGNMENT.csv").open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in payload["candidates"]:
                seed = row.get("seed") or {}
                reviewed_row = row.get("reviewed_unresolved") or {}
                writer.writerow({
                    "row_id": row["row_id"],
                    "canonical_tag": row["canonical_tag"],
                    "category": row["category"],
                    "post_count": row["post_count"],
                    "display_ja": row["display_ja"],
                    "search_ja": row["search_ja"],
                    "translation_note": row["translation_note"],
                    "primary_source_file": row["primary_source_file"],
                    "seed_shortlist_source": seed.get("source", ""),
                    "seed_provisional_verdict": seed.get("provisional_verdict", ""),
                    "seed_proposed_display_ja": seed.get("proposed_display_ja", ""),
                    "seed_proposed_search_ja": seed.get("proposed_search_ja", ""),
                    "seed_evidence_ref": seed.get("evidence_ref", ""),
                    "seed_audit_note": seed.get("audit_note", ""),
                    "reviewed_unresolved": "true" if reviewed_row else "",
                    "review_count": reviewed_row.get("review_count", ""),
                    "last_review_cycle": reviewed_row.get("last_review_cycle", ""),
                    "last_review_reason": reviewed_row.get("review_reason", ""),
                })

    print(json.dumps({
        "created": True,
        "cycle_id": cycle_id,
        "authority_base_sha": authority_sha,
        "progress_sha256": progress_hash,
        "assignment_state_sha256": assignment_state_hash,
        "remaining": progress["remaining_external_rows"],
        "reviewed_unresolved_registry_rows": len(reviewed),
        "assigned_unique_rows": len(used),
        "lanes": {
            k: {
                "candidate_count": v["candidate_count"],
                "target_resolutions": v["target_resolutions"],
                "seeded_count": v["seeded_count"],
                "reviewed_unresolved_count": v["reviewed_unresolved_count"],
            }
            for k, v in lane_payloads.items()
        },
        "production_modified": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
