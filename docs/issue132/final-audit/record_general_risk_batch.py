#!/usr/bin/env python3
"""Validate and append hand-reviewed entries against the frozen blind packet."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DIR = ROOT / "docs/issue132/final-audit"
PACKET = DIR / "general_risk_reduced_blind.jsonl"
OUTPUT = DIR / "audit_general_risk_verdicts.jsonl"
CONTRACT = ROOT / "docs/issue132/parallel/pass_a_semantic_contract_v2.json"
FIELDS = {
    "discovery_mode",
    "routes",
    "local_refinement_ids",
    "body_site_ids",
    "theme_ids",
    "route_vocabulary_gap",
    "confidence",
    "short_reason",
    "review_depth",
    "evidence_urls",
}


def canonical_json(value: object) -> bytes:
    # ASCII escaping keeps Windows PowerShell pipe encoding from producing lone surrogates.
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def main() -> None:
    packet_rows = load_jsonl(PACKET)
    packet = {row["identity_key"]: row for row in packet_rows}
    existing_rows = load_jsonl(OUTPUT) if OUTPUT.exists() else []
    existing = {row["identity_key"] for row in existing_rows}
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    route_ids = set(contract["route_ids"])
    local_ids = set(contract["local_refinement_parent"])
    body_ids = set(contract["body_site_ids"])
    theme_ids = set(contract["theme_ids"])
    allowed_modes = set(contract["allowed_discovery_modes"])
    allowed_depths = set(contract["allowed_review_depths"])

    batch = [json.loads(line) for line in sys.stdin.read().splitlines() if line.strip()]
    if not batch:
        raise SystemExit("No audit decisions supplied on stdin")
    seen_batch: set[str] = set()
    normalized: list[dict] = []
    for decision in batch:
        key = decision.get("identity_key")
        if key not in packet:
            raise SystemExit(f"Identity is outside the frozen blind packet: {key}")
        if key in existing or key in seen_batch:
            raise SystemExit(f"Duplicate audit verdict: {key}")
        if set(decision) != {"identity_key", *FIELDS}:
            raise SystemExit(f"Invalid audit fields for {key}: {sorted(set(decision) ^ {'identity_key', *FIELDS})}")
        seen_batch.add(key)
        if decision["discovery_mode"] not in allowed_modes:
            raise SystemExit(f"Invalid discovery mode for {key}")
        if decision["review_depth"] not in allowed_depths:
            raise SystemExit(f"Invalid review depth for {key}")
        if decision["confidence"] not in {"HIGH", "MEDIUM", "LOW"}:
            raise SystemExit(f"Invalid confidence for {key}")
        if not isinstance(decision["route_vocabulary_gap"], bool):
            raise SystemExit(f"route_vocabulary_gap must be Boolean for {key}")
        routes = decision["routes"]
        if not isinstance(routes, list) or len(routes) > 3:
            raise SystemExit(f"Invalid routes list for {key}")
        route_ids_here = [route.get("id") for route in routes]
        if len(set(route_ids_here)) != len(route_ids_here) or any(
            route not in route_ids or strength not in {"CORE", "SUPPORTING"}
            for route, strength in ((route.get("id"), route.get("strength")) for route in routes)
        ):
            raise SystemExit(f"Invalid or duplicate route for {key}")
        if routes and not any(route["strength"] == "CORE" for route in routes):
            raise SystemExit(f"Browse routes require a CORE route for {key}")
        for field, allowed in (("local_refinement_ids", local_ids), ("body_site_ids", body_ids), ("theme_ids", theme_ids)):
            values = decision[field]
            if not isinstance(values, list) or len(values) != len(set(values)) or any(value not in allowed for value in values):
                raise SystemExit(f"Invalid {field} for {key}")
        if decision["review_depth"] == "RESEARCHED" and not decision["evidence_urls"]:
            raise SystemExit(f"RESEARCHED requires evidence for {key}")
        if decision["discovery_mode"] == "SEMANTIC_UNRESOLVED" and (
            decision["review_depth"] != "RESEARCHED" or not decision["evidence_urls"]
        ):
            raise SystemExit(f"SEMANTIC_UNRESOLVED requires RESEARCHED evidence for {key}")
        if decision["discovery_mode"] in {"SEARCH_ORIENTED", "SEMANTIC_UNRESOLVED"} and (
            decision["local_refinement_ids"] or decision["body_site_ids"] or decision["theme_ids"]
        ):
            raise SystemExit(f"Search/unresolved identity cannot carry browse facets for {key}")
        if not isinstance(decision["short_reason"], str) or not decision["short_reason"].strip():
            raise SystemExit(f"Missing independent semantic reason for {key}")

        source = packet[key]
        row = {
            **source,
            **decision,
            "input_packet_sha256": hashlib.sha256(canonical_json(source)).hexdigest(),
        }
        normalized.append(row)

    with OUTPUT.open("a", encoding="utf-8", newline="\n") as stream:
        for row in normalized:
            stream.write(canonical_json(row).decode("utf-8") + "\n")
    print(json.dumps({"appended": len(normalized), "total": len(existing) + len(normalized)}, indent=2))


if __name__ == "__main__":
    main()
