#!/usr/bin/env python3
import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_ROWS = 195
API = "https://danbooru.donmai.us/tags.json"
USER_AGENT = "DanbooruTagTool-Issue96-Audit/1.0"


def fetch_tag(name: str) -> dict | None:
    params = urllib.parse.urlencode({"search[name]": name, "limit": "5"})
    req = urllib.request.Request(f"{API}?{params}", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)
    for row in data:
        if row.get("name") == name:
            return row
    return None


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--summary", required=True)
    a = p.parse_args()

    with Path(a.input).open("r", encoding="utf-8-sig", newline="") as f:
        source = list(csv.DictReader(f))
    if len(source) != EXPECTED_ROWS:
        raise SystemExit(f"input row drift: {len(source)} != {EXPECTED_ROWS}")

    checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    results = []
    failures = []
    for i, row in enumerate(source, 1):
        name = row["canonical_tag"]
        try:
            live = fetch_tag(name)
        except Exception as exc:
            failures.append((name, f"API_ERROR:{type(exc).__name__}:{exc}"))
            continue
        if live is None:
            failures.append((name, "NOT_FOUND_EXACT"))
            continue

        category = int(live.get("category", -1))
        deprecated = bool(live.get("is_deprecated", False))
        live_count = int(live.get("post_count", 0))
        status = "PASS_CURRENT_GENERAL_CANONICAL"
        if category != 0:
            status = f"FAIL_CATEGORY_{category}"
        elif deprecated:
            status = "FAIL_DEPRECATED"
        if not status.startswith("PASS"):
            failures.append((name, status))

        results.append({
            "proposed_special_id": row["proposed_special_id"],
            "canonical_tag": name,
            "frozen_post_count_2026_09_02": row["post_count"],
            "live_post_count": str(live_count),
            "live_category": str(category),
            "live_is_deprecated": str(deprecated).lower(),
            "live_tag_id": str(live.get("id", "")),
            "validation_status": status,
            "checked_at_utc": checked_at,
        })
        if i % 25 == 0:
            print(f"checked {i}/{EXPECTED_ROWS}")
        time.sleep(0.08)

    if failures:
        details = "\n".join(f"- {name}: {why}" for name, why in failures[:100])
        raise SystemExit(f"live canonical validation failed ({len(failures)}):\n{details}")
    if len(results) != EXPECTED_ROWS:
        raise SystemExit(f"result count drift: {len(results)}")

    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = list(results[0])
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader(); w.writerows(results)

    changed_counts = sum(
        int(r["frozen_post_count_2026_09_02"]) != int(r["live_post_count"])
        for r in results
    )
    Path(a.summary).write_text(
        "# Issue #96 live Danbooru canonical validation summary v1\n\n"
        "Status: **195/195 LIVE GENERAL CANONICAL PASS / NO PRODUCTION MUTATION**\n\n"
        f"- checked at UTC: `{checked_at}`\n"
        f"- exact identities checked: **{len(results)}**\n"
        "- current General category (`category=0`): **195**\n"
        "- deprecated: **0**\n"
        "- missing exact canonical: **0**\n"
        f"- post_count changed since frozen 2026-09-02 snapshot: **{changed_counts}** (informational only)\n\n"
        "This is a live identity-validity guard only. The frozen Issue #94 source remains the reproducible audit baseline; live post-count changes do not alter Core/Extended assignment in the frozen proposal.\n\n"
        "`CONTENT_FILTER_USED=NO`  \n"
        "`PRODUCTION_FILES_CHANGED=NO`  \n"
        "`ISSUE70_MUTATED=NO`\n",
        encoding="utf-8",
    )
    print(f"ISSUE96_LIVE_CANONICAL_PASS rows={len(results)} changed_counts={changed_counts}")


if __name__ == "__main__":
    main()
