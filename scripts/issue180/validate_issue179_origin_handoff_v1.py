#!/usr/bin/env python3
"""Validate the Issue #179 origin handoff snapshot consumed by Issue #180."""
from __future__ import annotations
import csv
import json
import re
from pathlib import Path

R=Path(__file__).resolve().parents[2]
CSV_PATH=R/"docs/issue180/evidence/ISSUE179_ORIGIN_HANDOFF_V1.csv"
META_PATH=R/"docs/issue180/evidence/ISSUE179_ORIGIN_HANDOFF_V1.meta.json"
EXPECTED_FIELDS={
 "row_id","canonical_tag","origin_class","origin_excluded_terms","origin_review_terms",
 "origin_evidence","origin_note","origin_second_review_required",
}
ALLOWED={
 "OFFICIAL_IDENTITY","OFFICIAL_ALIAS","OFFICIAL_VARIANT",
 "FANWORK_PAIRING","FANWORK_HASHTAG","FANWORK_EVENT","FANWORK_MEME",
 "FANWORK_COMMUNITY","FANWORK_CROSSOVER","FANWORK_DERIVATIVE",
 "NON_IDENTITY_DESCRIPTION","UNKNOWN",
}


def read_csv(path):
 with path.open(encoding="utf-8-sig",newline="") as f:
  reader=csv.DictReader(f)
  fields=set(reader.fieldnames or [])
  if fields!=EXPECTED_FIELDS:
   raise SystemExit(f"origin handoff schema drift missing={sorted(EXPECTED_FIELDS-fields)} extra={sorted(fields-EXPECTED_FIELDS)}")
  return list(reader)


def main():
 rows=read_csv(CSV_PATH)
 meta=json.loads(META_PATH.read_text(encoding="utf-8"))
 if len(rows)!=100:
  raise SystemExit(f"origin handoff row drift: {len(rows)} != 100")
 if meta.get("rows")!=len(rows):
  raise SystemExit("origin handoff meta row count mismatch")
 sha=str(meta.get("source_sha",""))
 if not re.fullmatch(r"[0-9a-f]{40}",sha):
  raise SystemExit("origin handoff source_sha malformed")
 if meta.get("source_branch")!="research/issue179-character-quality-audit":
  raise SystemExit("origin handoff source branch drift")
 if meta.get("source_path")!="docs/issue179/reviews/I179-B001-B002_ORIGIN_REVIEW.csv":
  raise SystemExit("origin handoff source path drift")

 ids=set(); tags=set(); by={}
 for r in rows:
  rid=r["row_id"].strip(); tag=r["canonical_tag"].strip(); cls=r["origin_class"].strip()
  if not rid or rid in ids: raise SystemExit(f"duplicate/blank origin row_id: {rid}")
  if not tag or tag in tags: raise SystemExit(f"duplicate/blank origin canonical_tag: {tag}")
  if cls not in ALLOWED: raise SystemExit(f"invalid origin_class {cls!r} for {tag}")
  if r["origin_second_review_required"].strip() not in {"true","false"}:
   raise SystemExit(f"invalid origin_second_review_required for {tag}")
  ids.add(rid);tags.add(tag);by[tag]=cls

 regressions={
  "harmony_(pokemon)":"UNKNOWN",
  "hatsune_miku":"OFFICIAL_IDENTITY",
  "mudrock_(elite_ii)_(arknights)":"OFFICIAL_VARIANT",
 }
 for tag,expected in regressions.items():
  if by.get(tag)!=expected:
   raise SystemExit(f"origin handoff regression: {tag} expected {expected}, got {by.get(tag)}")

 print(json.dumps({
  "rows":len(rows),
  "source_sha":sha,
  "official_rows":sum(r["origin_class"] in {"OFFICIAL_IDENTITY","OFFICIAL_ALIAS","OFFICIAL_VARIANT"} for r in rows),
  "guarded_rows":sum(r["origin_class"] not in {"OFFICIAL_IDENTITY","OFFICIAL_ALIAS","OFFICIAL_VARIANT"} for r in rows),
  "gate":"PASS",
 },ensure_ascii=False,indent=2))


if __name__=="__main__":main()
