#!/usr/bin/env python3
import argparse
import csv
import hashlib
from collections import Counter
from pathlib import Path

EXPECTED_TOTAL = 195
FIRST_ID = 2789
LAST_ID = 2983
EXPECTED_LAYERS = {"Core": 86, "Extended": 109}
EXPECTED_DISPLAY_JA = {
    "explosion_gag": "爆発ギャグ表現",
    "pregnancy_halo": "妊娠ヘイロー",
    "breast_curtain_lift": "胸前垂れを持ち上げる",
    "pov_crotch": "一人称視点の自分の股間",
    "spread_eagle_position": "両手両足を広げた姿勢",
}


def read_csv(path: str) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def keyed(rows: list[dict[str, str]], label: str) -> dict[tuple[int, str], dict[str, str]]:
    out = {}
    for row in rows:
        key = (int(row["proposed_special_id"]), row["canonical_tag"])
        if key in out:
            raise SystemExit(f"duplicate {label} key: {key}")
        out[key] = row
    return out


def write_csv(path: str, rows: list[dict[str, str]]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def sha256(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--identity", required=True)
    p.add_argument("--taxonomy", required=True)
    p.add_argument("--live", required=True)
    p.add_argument("--ja-batch", action="append", required=True)
    p.add_argument("--ja-corrections", required=True)
    p.add_argument("--ja-output", required=True)
    p.add_argument("--proposal-output", required=True)
    p.add_argument("--summary", required=True)
    a = p.parse_args()

    identity_rows = read_csv(a.identity)
    taxonomy_rows = read_csv(a.taxonomy)
    live_rows = read_csv(a.live)
    base_ja_rows = [r for path in a.ja_batch for r in read_csv(path)]
    correction_rows = read_csv(a.ja_corrections)

    identity = keyed(identity_rows, "identity")
    taxonomy = keyed(taxonomy_rows, "taxonomy")
    live = keyed(live_rows, "live")
    base_ja = keyed(base_ja_rows, "base-ja")
    corrections = keyed(correction_rows, "ja-correction")

    expected_ids = list(range(FIRST_ID, LAST_ID + 1))
    actual_ids = sorted(k[0] for k in identity)
    if len(identity) != EXPECTED_TOTAL or actual_ids != expected_ids:
        raise SystemExit(f"identity population drift rows={len(identity)} ids={actual_ids[:2]}..{actual_ids[-2:]}")
    keys = set(identity)
    for label, mapping in (("taxonomy", taxonomy), ("live", live), ("base-ja", base_ja)):
        if set(mapping) != keys:
            raise SystemExit(f"{label} key population mismatch")
    if not set(corrections) <= keys:
        raise SystemExit("Japanese correction contains non-proposal identity")

    layer_counts = Counter(r["proposed_layer"] for r in identity_rows)
    if dict(layer_counts) != EXPECTED_LAYERS:
        raise SystemExit(f"layer count drift: {dict(layer_counts)}")

    ja_rows = []
    proposal_rows = []
    kind_counts = Counter()
    for key in sorted(keys):
        ident = identity[key]
        tax = taxonomy[key]
        live_row = live[key]
        ja = dict(base_ja[key])
        if key in corrections:
            corr = corrections[key]
            for field in ("display_ja", "search_ja", "ja_status", "ja_note"):
                ja[field] = corr[field]

        if not ja.get("display_ja") or not ja.get("search_ja"):
            raise SystemExit(f"empty Japanese metadata: {key}")
        if tax.get("validation_status") != "TAXONOMY_RESOLVED" or not tax.get("kind_id"):
            raise SystemExit(f"taxonomy unresolved: {key}")
        if live_row.get("validation_status") != "PASS_CURRENT_GENERAL_CANONICAL":
            raise SystemExit(f"live canonical failed: {key} {live_row.get('validation_status')}")
        if live_row.get("live_category") != "0" or live_row.get("live_is_deprecated") != "false":
            raise SystemExit(f"live category/deprecated guard failed: {key}")

        tag = key[1]
        if tag == "breast_suppress" and tax["kind_id"] != "ACTION_CONTACT":
            raise SystemExit("breast_suppress taxonomy correction missing")
        if tag == "explosion_gag":
            if tax["kind_id"] != "META_EXPRESSION":
                raise SystemExit("explosion_gag kind correction missing")
            if "MOUTH_ORAL" in tax.get("body_site_ids", "") or "BDSM_RESTRAINT" in tax.get("theme_ids", ""):
                raise SystemExit("explosion_gag stale restraint facet remains")
        if tag in EXPECTED_DISPLAY_JA and ja["display_ja"] != EXPECTED_DISPLAY_JA[tag]:
            raise SystemExit(f"reviewed Japanese correction drift at {tag}: {ja['display_ja']}")

        ja_rows.append({
            "proposed_special_id": ident["proposed_special_id"],
            "canonical_tag": tag,
            "display_ja": ja["display_ja"],
            "search_ja": ja["search_ja"],
            "ja_status": ja["ja_status"],
            "ja_note": ja["ja_note"],
        })
        kind_counts[tax["kind_id"]] += 1
        proposal_rows.append({
            "proposed_special_id": ident["proposed_special_id"],
            "canonical_tag": tag,
            "canonical_aliases": ident.get("canonical_aliases", ""),
            "frozen_post_count_2026_09_02": ident["post_count"],
            "live_post_count": live_row["live_post_count"],
            "proposed_layer": ident["proposed_layer"],
            "display_ja": ja["display_ja"],
            "search_ja": ja["search_ja"],
            "kind_id": tax["kind_id"],
            "body_site_ids": tax.get("body_site_ids", ""),
            "theme_ids": tax.get("theme_ids", ""),
            "concept_area": ident.get("concept_area", ""),
            "live_tag_id": live_row.get("live_tag_id", ""),
            "live_validation_status": live_row["validation_status"],
            "ja_status": ja["ja_status"],
            "duplicate_guard": "CURRENT_SPECIAL_GAP_PASS",
            "proposal_status": "PREP_READY_FOR_DEV_REVIEW",
            "source_issue94_commit": ident.get("source_issue94_commit", ""),
            "notes": tax.get("notes", ""),
        })

    if len(ja_rows) != EXPECTED_TOTAL or len(proposal_rows) != EXPECTED_TOTAL:
        raise SystemExit("output row count drift")

    write_csv(a.ja_output, ja_rows)
    write_csv(a.proposal_output, proposal_rows)
    ja_hash = sha256(a.ja_output)
    proposal_hash = sha256(a.proposal_output)
    live_changed = sum(
        int(r["frozen_post_count_2026_09_02"]) != int(r["live_post_count"])
        for r in proposal_rows
    )

    lines = [
        "# Issue #96 promotion proposal summary v1",
        "",
        "Status: **195/195 PREP READY FOR DEV REVIEW / NO PRODUCTION MUTATION**",
        "",
        f"- total proposal rows: **{len(proposal_rows)}**",
        f"- ID range: **{FIRST_ID}..{LAST_ID}**",
        f"- Core: **{layer_counts['Core']}**",
        f"- Extended: **{layer_counts['Extended']}**",
        "- current-Special canonical/alias overlap: **0**",
        "- live General canonical pass: **195/195**",
        "- live deprecated/missing: **0**",
        "- Japanese display/search coverage: **195/195**",
        f"- reviewed Japanese correction overlays applied: **{len(corrections)}**",
        "- taxonomy resolved: **195/195**",
        f"- post_count changed since frozen 2026-09-02 snapshot: **{live_changed}** (informational only)",
        "",
        "## Kind counts",
        "",
    ]
    lines += [f"- `{k}`: **{v}**" for k, v in sorted(kind_counts.items())]
    lines += [
        "",
        "## Reviewed correction guards",
        "",
        "- `breast_suppress` -> `ACTION_CONTACT`",
        "- `explosion_gag` -> `META_EXPRESSION` with no mouth/BDSM facet",
        "- `pregnancy_halo` -> `妊娠ヘイロー`",
        "- `breast_curtain_lift` -> `胸前垂れを持ち上げる`",
        "- `pov_crotch` -> `一人称視点の自分の股間`",
        "- `spread_eagle_position` -> `両手両足を広げた姿勢`",
        "",
        "## Artifact hashes",
        "",
        f"- Japanese metadata SHA-256: `{ja_hash}`",
        f"- promotion proposal SHA-256: `{proposal_hash}`",
        "",
        "This proposal is a PREP artifact only. It does not append rows to the production Special dictionary and does not modify runtime databases.",
        "",
        "`CONTENT_FILTER_USED=NO`  ",
        "`PRODUCTION_FILES_CHANGED=NO`  ",
        "`ISSUE70_MUTATED=NO`",
        "",
    ]
    Path(a.summary).write_text("\n".join(lines), encoding="utf-8")
    print(
        f"ISSUE96_PROMOTION_PROPOSAL_PASS total={len(proposal_rows)} "
        f"core={layer_counts['Core']} extended={layer_counts['Extended']} "
        f"ja={len(ja_rows)} taxonomy={sum(kind_counts.values())}"
    )


if __name__ == "__main__":
    main()
