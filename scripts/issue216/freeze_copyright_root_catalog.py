#!/usr/bin/env python3
"""Freeze the set of already-confirmed #180 HOME roots for missing-root checks."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER_SHA256 = "135463a5225b6501db923322284f8e309f217eb5359538088eb6de6d78b77071"
FIELDS = ["copyright_canonical", "provenance"]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build(master_path: Path) -> tuple[list[dict[str, str]], dict[str, object]]:
    master_hash = digest(master_path)
    if master_hash != MASTER_SHA256:
        raise SystemExit(f"frozen #180 master SHA mismatch: {master_hash}")
    with master_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 35_890:
        raise SystemExit(f"frozen #180 master population mismatch: {len(rows)}")
    if sum(row["final_state"] == "HOME_CONFIRMED" for row in rows) != 21_907:
        raise SystemExit("frozen #180 confirmed count mismatch")
    roots = sorted({row["home_copyright"] for row in rows
                    if row["final_state"] == "HOME_CONFIRMED" and row["home_copyright"]})
    if any(row["final_state"] == "HOME_CONFIRMED" and not row["home_copyright"] for row in rows):
        raise SystemExit("frozen #180 master has confirmed rows without HOME")
    output = [{"copyright_canonical": root,
               "provenance": f"Observed as an existing HOME_CONFIRMED Copyright in Issue #180 master {MASTER_SHA256}."}
              for root in roots]
    manifest = {"schema_version": "issue216-copyright-root-catalog-v1", "baseline_issue": 180,
                "baseline_commit": "9c0db59c0f1dc56402c955e718a37d9de1849d7e",
                "baseline_master_sha256": master_hash, "confirmed_character_count": 21_907,
                "root_count": len(roots), "root_catalog_sha256": hashlib.sha256(
                    ("\n".join(roots) + "\n").encode("utf-8")).hexdigest()}
    return output, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", type=Path, required=True)
    parser.add_argument("--roots", type=Path, default=ROOT / "docs/issue216/COPYRIGHT_ROOTS_V1.csv")
    parser.add_argument("--manifest", type=Path, default=ROOT / "docs/issue216/COPYRIGHT_ROOTS_V1.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output, manifest = build(args.master)
    if args.check:
        with args.roots.open(encoding="utf-8-sig", newline="") as stream:
            actual = list(csv.DictReader(stream))
        if actual != output or json.loads(args.manifest.read_text(encoding="utf-8")) != manifest:
            raise SystemExit("frozen Copyright root catalog differs from deterministic reconstruction")
        print(f"Copyright root catalog reproducibility: PASS ({len(output)} roots)")
        return
    if args.roots.exists() or args.manifest.exists():
        raise SystemExit("refusing to overwrite frozen Copyright root catalog")
    args.roots.parent.mkdir(parents=True, exist_ok=True)
    with args.roots.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"frozen existing Copyright roots: {len(output)}")


if __name__ == "__main__":
    main()
