from __future__ import annotations
import hashlib, sys, time, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DATA=ROOT/"data"/"reference_cooccurrence"
DATA.mkdir(parents=True,exist_ok=True)
FILES=[
 {"name":"available_tags.csv","url":"https://huggingface.co/spaces/u-haru/danbooru_tagsearch/raw/main/available_tags.csv","size":None,"sha256":None},
 {"name":"cooccurrence_all_normalized.npz","url":"https://huggingface.co/spaces/u-haru/danbooru_tagsearch/resolve/main/cooccurrence_all_normalized.npz?download=true","size":455_719_557,"sha256":"dc1749f1d00f8b7063015176b81b603b49552c341074993c50c4390d8c8b6ca6"}
]
def sha(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for b in iter(lambda:f.read(4*1024*1024),b""): h.update(b)
 return h.hexdigest()
def dl(url,dest):
 tmp=dest.with_suffix(dest.suffix+".part")
 req=urllib.request.Request(url,headers={"User-Agent":"DanbooruTagExplorerTrial/0.2"})
 with urllib.request.urlopen(req,timeout=60) as r,tmp.open("wb") as f:
  total=int(r.headers.get("Content-Length") or 0); done=0; st=time.time()
  while True:
   b=r.read(1024*1024)
   if not b: break
   f.write(b); done+=len(b)
   speed=done/max(time.time()-st,.1)/1024/1024
   if total: print(f"\r{dest.name}: {done*100/total:5.1f}% {done/1024/1024:.0f}/{total/1024/1024:.0f} MiB {speed:.1f} MiB/s",end="")
   else: print(f"\r{dest.name}: {done/1024/1024:.0f} MiB {speed:.1f} MiB/s",end="")
 print(); tmp.replace(dest)
for x in FILES:
 p=DATA/x["name"]
 ok=p.exists()
 if ok and x["size"] is not None: ok=p.stat().st_size==x["size"]
 if ok and x["sha256"]: ok=sha(p)==x["sha256"]
 if not ok:
  if p.exists(): p.unlink()
  print("[DOWNLOAD]",p.name); dl(x["url"],p)
 if x["size"] is not None and p.stat().st_size!=x["size"]: raise RuntimeError("size mismatch: "+p.name)
 if x["sha256"] and sha(p)!=x["sha256"]: raise RuntimeError("SHA-256 mismatch: "+p.name)
 print("[OK]",p.name)
print("\n参考共起データの準備が完了しました。")
