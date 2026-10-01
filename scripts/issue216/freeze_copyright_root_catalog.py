#!/usr/bin/env python3
"""Freeze the complete canonical Copyright inventory used by Issue #180."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "docs/issue70/data/runtime/issue70_catalog_overlay.csv"
CATALOG_SHA256 = "1d346ad75655ea6091f9bce9a4cf58b1cf6f8fac18c7eb441f8edd009ee81433"
CATALOG_ROWS = 92_739
COPYRIGHT_ROWS = 8_536
FIELDS = ["copyright_canonical", "provenance"]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build(catalog_path: Path) -> tuple[list[dict[str, str]], dict[str, object]]:
    catalog_hash = digest(catalog_path)
    if catalog_hash != CATALOG_SHA256:
        raise SystemExit(f"Issue #70 catalog SHA mismatch: {catalog_hash}")
    with catalog_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != CATALOG_ROWS:
        raise SystemExit(f"Issue #70 catalog population mismatch: {len(rows)}")
    copyrights = [row for row in rows if row.get("category") == "3"]
    roots = sorted(row["canonical_tag"] for row in copyrights)
    if len(copyrights) != COPYRIGHT_ROWS or len(set(roots)) != len(roots) or any(not root for root in roots):
        raise SystemExit("Issue #70 catalog Copyright inventory failed count/uniqueness checks")
    output = [{"copyright_canonical": root,
               "provenance": f"Canonical Copyright category 3 row in Issue #70 catalog {CATALOG_SHA256}."}
              for root in roots]
    manifest = {"schema_version": "issue216-copyright-root-catalog-v2", "catalog_issue": 70,
                "catalog_path": "docs/issue70/data/runtime/issue70_catalog_overlay.csv",
                "catalog_sha256": catalog_hash, "catalog_row_count": len(rows),
                "copyright_category": "3", "copyright_root_count": len(roots),
                "root_catalog_sha256": hashlib.sha256(
                    ("\n".join(roots) + "\n").encode("utf-8")).hexdigest()}
    return output, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--roots", type=Path, default=ROOT / "docs/issue216/COPYRIGHT_ROOTS_V1.csv")
    parser.add_argument("--manifest", type=Path, default=ROOT / "docs/issue216/COPYRIGHT_ROOTS_V1.json")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--upgrade-home-root-v1", action="store_true",
                        help="replace the earlier confirmed-HOME-only set after validating its known v1 manifest")
    args = parser.parse_args()
    output, manifest = build(args.catalog)
    if args.check:
        with args.roots.open(encoding="utf-8-sig", newline="") as stream:
            actual = list(csv.DictReader(stream))
        if actual != output or json.loads(args.manifest.read_text(encoding="utf-8")) != manifest:
            raise SystemExit("frozen Copyright root catalog differs from deterministic reconstruction")
        print(f"complete Copyright root catalog reproducibility: PASS ({len(output)} roots)")
        return
    if args.roots.exists() or args.manifest.exists():
        if not args.upgrade_home_root_v1 or not (args.roots.exists() and args.manifest.exists()):
            raise SystemExit("refusing to overwrite frozen Copyright root catalog")
        previous = json.loads(args.manifest.read_text(encoding="utf-8"))
        if (previous.get("schema_version") != "issue216-copyright-root-catalog-v1"
                or previous.get("root_count") != 1672
                or previous.get("root_catalog_sha256") != "4b5f756a1b82992bdad01fc4c1c39a4977eadc2f08ba1a472e95d5d10806337d"):
            raise SystemExit("existing roots are not the exact known v1 HOME-only catalog; refusing upgrade")
    args.roots.parent.mkdir(parents=True, exist_ok=True)
    with args.roots.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"frozen complete Copyright root catalog: {len(output)}")


if __name__ == "__main__":
    main()
