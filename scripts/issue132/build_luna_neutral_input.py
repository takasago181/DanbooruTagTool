#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path

EXPECTED_ROWS = 31_003
EXPECTED_AUTHORITY_SHA256 = "d2966dbc3c70617af2a985a94f81650785a29c1668b40b582d3c213ef2a68bc0"
SORT_SALT = "issue132-pass-a-v2|"

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def stable_key(identity: str) -> str:
    return hashlib.sha256((SORT_SALT+identity).encode("utf-8")).hexdigest()

def parse_sources(value: str) -> list[str]:
    value=(value or "").strip()
    if not value:
        return []
    for parser in (json.loads, ast.literal_eval):
        try:
            obj=parser(value)
            if isinstance(obj,list):
                return [str(x).strip() for x in obj if str(x).strip()]
        except Exception:
            pass
    if "|" in value:
        return [x.strip() for x in value.split("|") if x.strip()]
    if ";" in value:
        return [x.strip() for x in value.split(";") if x.strip()]
    return [value]

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--authority", default="docs/issue118/production_candidate/sexual_intent_v2.csv")
    ap.add_argument("--out", required=True)
    args=ap.parse_args()

    authority=Path(args.authority)
    out=Path(args.out)
    digest=sha256_file(authority)
    if digest != EXPECTED_AUTHORITY_SHA256:
        raise SystemExit(f"authority sha256 drift: {digest} != {EXPECTED_AUTHORITY_SHA256}")

    with authority.open("r",encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=EXPECTED_ROWS:
        raise SystemExit(f"identity count drift: {len(rows)} != {EXPECTED_ROWS}")

    ids=[r["identity_key"].strip() for r in rows]
    if any(not x for x in ids) or len(set(ids))!=EXPECTED_ROWS:
        raise SystemExit("blank/duplicate identity_key")

    neutral=[]
    for row in rows:
        identity=row["identity_key"].strip()
        sources=sorted(set(parse_sources(row.get("source_identities",""))))
        # identity_key is always included as a semantic lookup surface. source_identities
        # may carry historical/source spellings from the accepted runtime reconciliation.
        surfaces=sorted(set([identity,*sources]))
        neutral.append({
            "identity_key":identity,
            "source_surfaces":json.dumps(surfaces,ensure_ascii=False,separators=(",",":")),
            "_sort":stable_key(identity),
        })

    neutral.sort(key=lambda r:(r["_sort"],r["identity_key"]))
    for i,row in enumerate(neutral,1):
        row["review_seq"]=i

    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["review_seq","identity_key","source_surfaces"],lineterminator="\n")
        w.writeheader()
        for row in neutral:
            w.writerow({k:row[k] for k in w.fieldnames})

    identity_order="".join(r["identity_key"]+"\n" for r in neutral).encode("utf-8")
    manifest={
        "schema_version":"issue132-luna-neutral-v2",
        "authority":"docs/issue118/production_candidate/sexual_intent_v2.csv",
        "authority_sha256":digest,
        "identity_count":len(neutral),
        "sort":"sha256",
        "sort_salt":SORT_SALT,
        "identity_order_sha256":hashlib.sha256(identity_order).hexdigest(),
        "output_sha256":sha256_file(out),
        "included_fields":["review_seq","identity_key","source_surfaces"],
        "intentionally_excluded":[
            "sexual_intent","review_status","general/special membership",
            "current #64/#76 classification","current Unified routes",
            "Japanese overlay/search terms","aliases","usage/post count",
            "machine audit labels","prior proposals"
        ],
        "purpose":"Independent Luna Pass A semantic discovery map; current product/search context is joined only after Pass A freezes."
    }
    manifest_path=out.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
