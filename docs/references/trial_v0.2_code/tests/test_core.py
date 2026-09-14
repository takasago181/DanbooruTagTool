from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"app"))
from core import Catalog
c=Catalog(ROOT/"data"/"catalog_20260902.json.gz")
assert len(c.tags)==124016, len(c.tags)
assert c.verified_special_counts["total"]==2788
r=c.resolve("school uniform")
assert r["ok"] and r["canonical"]=="school_uniform", r
r2=c.resolve("school_uniform")
assert r2["ok"] and r2["canonical"]=="school_uniform"
s=c.search("school un",20)
assert any(x["canonical"]=="school_uniform" for x in s)
sj=c.search("肛門",20)
assert len(sj)>0
for q, expected in [("ツインテール","twintails"),("制服","school_uniform"),("長髪","long_hair"),("座る","sitting")]:
    rr=c.search(q,20)
    assert rr and rr[0]["canonical"]==expected, (q,rr[:3])
p=c.prompt_for(["school_uniform","long_hair"],[{"name":"TestLora","weight":"0.8","triggers":["test trigger"]}])
assert "school uniform" in p and "long hair" in p and "<lora:TestLora:0.8>" in p
assert p.count("school uniform")==1
print("PASS")
print("tags",len(c.tags))
print("search_entries",len(c.entries))
print("special",c.verified_special_counts)
