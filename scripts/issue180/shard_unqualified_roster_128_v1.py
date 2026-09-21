#!/usr/bin/env python3
"""Create 128 balanced review shards for every unqualified Character lacking identity-overlap evidence.
This is the official-roster research queue; no inferred HOME is approved here."""
import csv,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];D=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW";IN=D/"UNQUALIFIED_ROSTER_CANDIDATES_V1.csv";OD=D/"UNQUALIFIED_ROSTER_128";OD.mkdir(parents=True,exist_ok=True)
N=128
def main():
 rows=[r for r in csv.DictReader(IN.open(encoding="utf-8-sig",newline="")) if r["roster_candidate_state"]=="NO_IDENTITY_OVERLAP"];b=[[] for _ in range(N)]
 for r in rows:
  key=r.get("canonical_tag") or r.get("character_tag") or "";i=int(hashlib.sha256(key.encode()).hexdigest()[:8],16)%N;b[i].append(r)
 for i,rs in enumerate(b):
  p=OD/f"UQ-{i+1:03d}-of-{N}.csv"
  with p.open("w",encoding="utf-8-sig",newline="") as f:
   w=csv.DictWriter(f,fieldnames=rs[0].keys(),lineterminator="\n");w.writeheader();w.writerows(rs)
 x={"rows":len(rows),"shards":N,"min_rows":min(map(len,b)),"max_rows":max(map(len,b)),"authority_decision":"PENDING_OFFICIAL_ROSTER_RESEARCH","auto_approved":0,"accepted_source_modified":False,"production_modified":False}
 (D/"unqualified_roster_128_summary.json").write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
 if sum(map(len,b))!=len(rows):raise SystemExit("shard loss")
if __name__=="__main__":main()
