from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "artifacts/issue179-corrections/CORRECTION_LEDGER_V1.csv"
OUT_DIR = ROOT / "artifacts/issue179-runtime"
OUT = OUT_DIR / "ISSUE179_RUNTIME_PROJECTION_V1.csv"
MANIFEST = OUT_DIR / "manifest.json"

ISSUE70_SHA256 = "bf366734b41b2be9e6cb52de919ef55b7312445e1715f96a357db37abda8dad5"

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    by_row: dict[str, dict[str, str]] = {}
    for r in rows:
        if r["final_status"] != "ACCEPTED_AUDIT_OVERLAY":
            continue
        target = by_row.setdefault(r["row_id"], {"row_id": r["row_id"], "display_ja": "", "search_ja": ""})
        field = r["field"]
        if field not in {"display_ja", "search_ja"}:
            raise SystemExit("unexpected correction field: " + field)
        if target[field]:
            raise SystemExit("duplicate runtime field correction: " + r["row_id"] + " " + field)
        target[field] = r["proposed_value"]

    ordered = [by_row[k] for k in sorted(by_row, key=lambda v: int(v[4:]))]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["row_id", "display_ja", "search_ja"], lineterminator="\n")
        w.writeheader()
        w.writerows(ordered)

    raw = OUT.read_bytes()
    manifest = {
        "schema_version": 1,
        "source_issue70_sha256": ISSUE70_SHA256,
        "accepted_field_changes": len(rows),
        "distinct_rows": len(ordered),
        "display_rows": sum(bool(r["display_ja"]) for r in ordered),
        "search_rows": sum(bool(r["search_ja"]) for r in ordered),
        "projection_sha256": hashlib.sha256(raw).hexdigest(),
        "home_authority_modified": False,
        "source_data_mutated": False,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))

if __name__ == "__main__":
    main()
