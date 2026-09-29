#!/usr/bin/env python3
"""Append exact-fingerprint terminal reviews for the deterministic Phase B sweep.

This only records existing unresolved outcomes. It does not create or alter HOME
evidence and requires the current lane audit to cover every OPEN Research Unit.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts/issue180-v3"
UNITS = OUT / "research_units_v3.csv"
CLOSURE = ROOT / "docs/issue180/v3/reports/RESEARCH_UNIT_CLOSURE_SWEEP_V3.csv"
LANES = ROOT / "docs/issue180/v3/PHASE_B_LANE_AUDIT_V2.csv"
MEMBER_LANES = ROOT / "docs/issue180/v3/PHASE_B_MEMBER_LANE_AUDIT_V2.csv"
REVIEWS = ROOT / "docs/issue180/v3/research_unit_terminal_reviews_v3.csv"
SWEEP_AUDIT = ROOT / "docs/issue180/v3/reports/PHASE_B_TERMINAL_SWEEP_V2.csv"
FIELDS = ["unit_id", "member_ids_sha256", "terminal_status", "authority_source", "source_claim", "review_provenance"]

# These five exact migration/conflict residuals were independently examined in
# the Phase B high-yield pass. They remain unresolved for the stated reason.
EXHAUSTED_HIGH_YIELD = {
    "ru3-5a64e861ef4dcfd2c9cb": (
        "PARTIALLY_RESOLVED",
        "fu_hua_(phoenix) has two validated paths to distinct roots, honkai_(series) and honkai_impact_3rd; neither can be selected by voting or candidate score.",
    ),
    "ru3-5a7d65cbb3bb62d11093": (
        "PARTIALLY_RESOLVED",
        "gueira_(made_in_abyss) has an exact base Character whose validated HOME is promare, while the qualifier is only candidate evidence for made_in_abyss; no validated variant path establishes one HOME.",
    ),
    "ru3-674fb4829ec5a74bb8a3": (
        "PARTIALLY_RESOLVED",
        "theresa_apocalypse_(honkai_gakuen) has a validated exact base HOME honkai_(series), while honkai_gakuen remains qualifier-only; reviewed official routes did not establish a variant relation.",
    ),
    "ru3-b5955ec185bea7e55cfc": (
        "PARTIALLY_RESOLVED",
        "seong_mi-na_(bural_chingu) has an exact base HOME soulcalibur, while bural_chingu is not a validated variant HOME; current exact-source evidence does not resolve that identity path.",
    ),
    "ru3-eaace9542f0bc17d2fc5": (
        "PARTIALLY_RESOLVED",
        "zatanna_zatara_(absolute_dc) has a validated base HOME dc_comics, but the reviewed Absolute Wonder Woman appearance does not establish a distinct Absolute variant or HOME.",
    ),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def member_hash(tags: list[str]) -> str:
    return hashlib.sha256("\n".join(sorted(tags)).encode("utf-8")).hexdigest()


def build_reviews() -> list[dict[str, str]]:
    units = {r["unit_id"]: r for r in read(UNITS) if r["status"] == "OPEN"}
    closures = {r["unit_id"]: r for r in read(CLOSURE)}
    lanes = {r["unit_id"]: r for r in read(LANES)}
    member_lanes = read(MEMBER_LANES)
    if len(units) != len([r for r in read(UNITS) if r["status"] == "OPEN"]):
        raise ValueError("duplicate OPEN Research Unit ID")
    if set(units) != set(closures) or set(units) != set(lanes):
        raise ValueError("terminal sweep inputs do not exactly cover current OPEN units")
    if not units:
        if member_lanes:
            raise ValueError("member lane audit is nonempty while current OPEN unit set is empty")
        return []
    if set(EXHAUSTED_HIGH_YIELD) != {uid for uid, lane in lanes.items() if lane["lane"] == "HIGH_YIELD_RESEARCH"}:
        raise ValueError("exhausted high-yield set differs from the current deterministic audit")
    if len(member_lanes) != sum(int(unit["member_count"]) for unit in units.values()):
        raise ValueError("member audit does not exactly cover current OPEN members")

    rows: list[dict[str, str]] = []
    for uid in sorted(units):
        unit, closure, lane = units[uid], closures[uid], lanes[uid]
        tags = json.loads(unit["member_ids/tags"])
        fingerprint = member_hash(tags)
        if lane["member_ids_sha256"] != fingerprint:
            raise ValueError(f"lane audit fingerprint mismatch: {uid}")
        if lane["lane"] == "HIGH_YIELD_RESEARCH":
            status, claim = EXHAUSTED_HIGH_YIELD[uid]
            rationale = "Phase B bounded official-source review completed; this exact migration/conflict residual remains unresolved under existing evidence policy."
            sources = "docs/issue180/v3/PHASE_B_LANE_AUDIT_V2.csv; docs/issue180/v3/PHASE_B_MEMBER_LANE_AUDIT_V2.csv; docs/issue180/v3/reports/MIGRATION_COMPARISON_V3.csv; docs/issue180/v3/reports/RESEARCH_UNIT_CLOSURE_SWEEP_V3.csv"
        else:
            classification = closure["classification"]
            if classification == "POLICY_BLOCKED":
                status = "POLICY_BLOCKED"
                claim = "The current exact member set is blocked from HOME inference by the frozen Issue #180 policy; candidate roots and labels do not provide a valid HOME authority."
                sources = "docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json; docs/issue180/v3/reports/RESEARCH_UNIT_CLOSURE_SWEEP_V3.csv"
            elif classification == "CONFLICT_REVIEW":
                status = "PARTIALLY_RESOLVED"
                claim = "The current exact member set has competing validated HOME paths; preserving HOME_UNRESOLVED avoids selecting one root without an existing policy for the conflict."
                sources = "docs/issue180/v3/reports/RESEARCH_UNIT_CLOSURE_SWEEP_V3.csv; docs/issue180/v3/reports/MIGRATION_COMPARISON_V3.csv"
            elif classification == "IDENTITY_BLOCKED":
                raise ValueError(f"identity-blocked members must already carry exact #179 row IDs before terminalization: {uid}")
            else:
                if lane["lane"] != "FINAL_UNRESOLVED":
                    raise ValueError(f"unexpected lane for deterministic terminal status: {uid} {lane['lane']}")
                status = "NO_SAFE_EVIDENCE"
                claim = "The current exact member set has no validated direct HOME, family HOME plus membership path, or safe exact base/variant path; remaining candidate roots are non-authoritative and the Phase B audit found no approved reusable source, fresh official hint, or migration/conflict trigger."
                sources = "docs/issue180/v3/reports/RESEARCH_UNIT_CLOSURE_SWEEP_V3.csv; docs/issue180/v3/PHASE_B_LANE_AUDIT_V2.csv; docs/issue180/v3/PHASE_B_MEMBER_LANE_AUDIT_V2.csv; docs/issue180/parallel/QA_REVIEW_LEDGER_V2.csv; docs/issue180/parallel/SOURCE_REVIEW_LEDGER_V2.csv"
            rationale = f"Deterministic Phase B final-lane audit: {lane['rejection_reason']}; {lane['route_basis']}. Existing exact candidate structure was inspected; no HOME was inferred."
        rows.append({
            "unit_id": uid,
            "member_ids_sha256": fingerprint,
            "terminal_status": status,
            "authority_source": sources,
            "source_claim": claim,
            "review_provenance": f"Phase B terminal sweep; lane={lane['lane']}; classification={closure['classification']}; exact_member_count={len(tags)}; member_ids_sha256={fingerprint}. {rationale}",
        })
    return rows


def main() -> None:
    generated = build_reviews()
    existing = read(REVIEWS)
    by_id = {r["unit_id"]: r for r in existing}
    if len(by_id) != len(existing):
        raise SystemExit("duplicate terminal review IDs already exist")
    for row in generated:
        prior = by_id.get(row["unit_id"])
        if prior and prior != row:
            raise SystemExit(f"existing terminal review differs; refusing overwrite: {row['unit_id']}")
    additions = [row for row in generated if row["unit_id"] not in by_id]
    if any(set(row) != set(FIELDS) for row in additions):
        raise SystemExit("generated terminal review schema mismatch")
    with REVIEWS.open("a", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writerows(additions)
    persisted = {row["unit_id"]: row for row in read(REVIEWS)}
    for row in generated:
        if persisted.get(row["unit_id"]) != row:
            raise SystemExit(f"persisted terminal review mismatch: {row['unit_id']}")
    sweep_rows = [row for row in read(REVIEWS) if row["review_provenance"].startswith("Phase B terminal sweep;")]
    with SWEEP_AUDIT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(sweep_rows)
    counts: dict[str, int] = {}
    for row in sweep_rows:
        counts[row["terminal_status"]] = counts.get(row["terminal_status"], 0) + 1
    print(json.dumps({"current_open_units": len(generated), "appended": len(additions), "persisted_terminal_sweep_units": len(sweep_rows), "terminal_status_counts": counts}, indent=2))


if __name__ == "__main__":
    main()
