#!/usr/bin/env python3
"""Shard the complete unresolved family backlog for high-throughput semantic/authority review. No auto approval."""
import csv,json,hashlib
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parents[2];A=R/"artifacts/issue180-full-preflight";IN=A/"GLOBAL_UNRESOLVED_FAMILIES_V1.csv";OUT=A/"GLOBAL_UNRESOLVED_FAMILY_SHARDS_V1.csv";SUM=A/"global_unresolved_family_shards_v1_summary.json"
SHARDS=96
ATTR={"1st_costume","2nd_costume","3rd_costume","4th_costume","5th_costume","new_year","casual","stand","timeskip","female","male","summer","school_uniform","young","human","character","racehorse","cat"}
def main():
 rows=list(csv.DictReader(IN.open(encoding="utf-8-sig",newline="")));out=[];dist=Counter();lanes=Counter()
 for r in rows:
  fam=r["family"]; lane="UNQUALIFIED_ROSTER" if fam=="__UNQUALIFIED__" else ("ATTRIBUTE_VARIANT_REVIEW" if fam in ATTR else "IP_OR_VARIANT_AUTHORITY_REVIEW")
  shard=int(hashlib.sha256(fam.encode()).hexdigest()[:8],16)%SHARDS+1;sid=f"GF-{shard:02d}"
  out.append({**r,"review_lane":lane,"review_shard":sid,"authority_decision":"PENDING","auto_approved":"false"});dist[sid]+=1;lanes[lane]+=int(r["character_rows"])
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"families":len(out),"shards":SHARDS,"family_distribution":dict(sorted(dist.items())),"character_rows_by_lane":dict(lanes),
 "auto_approved":0,"accepted_source_modified":False,"production_modified":False}
 SUM.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
 if len(out)!=3849 or any(r["authority_decision"]!="PENDING" for r in out):raise SystemExit(1)
if __name__=="__main__":main()
