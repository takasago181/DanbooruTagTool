#!/usr/bin/env python3
import argparse
import csv
import hashlib
from pathlib import Path

SOURCE_COMMIT = "b505f34956dc60e189e8c749fbe0cb187ad5154e"
SOURCE_BLOB = "eb9d627e9b774194ec1ff6319374c983f18fb40f"
EXPECTED_ROWS = 195
FIRST_ID = 2789
LAST_ID = 2983
EXPECTED_CORE = 86
EXPECTED_EXTENDED = 109


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--summary", required=True)
    args = p.parse_args()

    src = Path(args.input)
    out = Path(args.output)
    summary = Path(args.summary)

    with src.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    required = {
        "canonical_tag", "post_count", "aliases", "concept_area", "final_status",
        "final_reason", "nearest_special_identity"
    }
    if not rows or not required.issubset(rows[0]):
        raise SystemExit(f"unexpected source schema: {sorted(rows[0] if rows else [])}")
    if len(rows) != EXPECTED_ROWS:
        raise SystemExit(f"candidate count drift: {len(rows)} != {EXPECTED_ROWS}")
    if any(r["final_status"] != "CANDIDATE" for r in rows):
        raise SystemExit("non-CANDIDATE row in frozen candidate source")
    canonical = [r["canonical_tag"] for r in rows]
    if len(set(canonical)) != EXPECTED_ROWS:
        raise SystemExit("duplicate canonical identity in candidate source")

    output_rows = []
    for offset, row in enumerate(rows):
        post_count = int(row["post_count"])
        layer = "Core" if post_count >= 1000 else "Extended"
        output_rows.append({
            "proposed_special_id": str(FIRST_ID + offset),
            "canonical_tag": row["canonical_tag"],
            "post_count": str(post_count),
            "proposed_layer": layer,
            "canonical_aliases": row["aliases"],
            "concept_area": row["concept_area"],
            "nearest_existing_special": row["nearest_special_identity"],
            "issue94_reason": row["final_reason"],
            "kind_id": "",
            "body_site_ids": "",
            "theme_ids": "",
            "display_ja": "",
            "search_ja": "",
            "browse_status": "PENDING_CLASSIFICATION",
            "duplicate_guard": "PENDING_CURRENT_SPECIAL_CHECK",
            "validation_status": "IDENTITY_LAYER_READY",
            "source_issue94_commit": SOURCE_COMMIT,
            "source_candidate_blob": SOURCE_BLOB,
            "notes": "",
        })

    ids = [int(r["proposed_special_id"]) for r in output_rows]
    if ids != list(range(FIRST_ID, LAST_ID + 1)):
        raise SystemExit("proposed ID sequence drift")
    core = sum(r["proposed_layer"] == "Core" for r in output_rows)
    ext = sum(r["proposed_layer"] == "Extended" for r in output_rows)
    if (core, ext) != (EXPECTED_CORE, EXPECTED_EXTENDED):
        raise SystemExit(f"layer-count drift: Core={core}, Extended={ext}")

    out.parent.mkdir(parents=True, exist_ok=True)
    fields = list(output_rows[0])
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(output_rows)

    source_sha = sha256(src)
    output_sha = sha256(out)
    summary.write_text(
        "# Issue #96 identity/layer proposal summary v1\n\n"
        "Status: **195/195 IDENTITY + LAYER MATERIALIZED / TAXONOMY + JA PENDING / NO PRODUCTION MUTATION**\n\n"
        f"- source Issue #94 commit: `{SOURCE_COMMIT}`\n"
        f"- source candidate Git blob: `{SOURCE_BLOB}`\n"
        f"- downloaded source SHA-256: `{source_sha}`\n"
        f"- input candidates: **{len(rows)}**\n"
        f"- proposed IDs: **{FIRST_ID}..{LAST_ID}**\n"
        f"- proposed Core: **{core}**\n"
        f"- proposed Extended: **{ext}**\n"
        "- proposed Alias candidate identities: **0**\n"
        "- proposed Semantic candidate identities: **0**\n"
        f"- proposal SHA-256: `{output_sha}`\n\n"
        "Layer assignment follows the existing Special rule: canonical post_count >=1000 => Core; canonical 1..999 => Extended.\n\n"
        "Remaining fields are deliberately left pending for the next PREP pass: accepted Issue #76 kind/body/theme classification, Japanese display/search metadata, and current-Special duplicate/alias validation.\n\n"
        "`CONTENT_FILTER_USED=NO`  \n"
        "`PRODUCTION_FILES_CHANGED=NO`  \n"
        "`ISSUE70_MUTATED=NO`\n",
        encoding="utf-8",
    )

    print(f"ISSUE96_IDENTITY_LAYER_PASS rows={len(rows)} core={core} extended={ext} ids={FIRST_ID}-{LAST_ID}")


if __name__ == "__main__":
    main()
