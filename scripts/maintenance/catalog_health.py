"""Compatibility CLI. Canonical catalog and UserData validators are separate scripts."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

def run(script: str, option: str, path: Path) -> dict:
    proc = subprocess.run([sys.executable, "-B", str(Path(__file__).with_name(script)), option, str(path)], capture_output=True, text=True)
    try: payload = json.loads(proc.stdout)
    except json.JSONDecodeError: raise RuntimeError(proc.stderr or proc.stdout or f"{script} failed with {proc.returncode}")
    if proc.returncode: raise RuntimeError(payload.get("error", f"{script} failed"))
    return payload

def main() -> int:
    parser=argparse.ArgumentParser(description="Compatibility facade for separate catalog/UserData health checks")
    parser.add_argument("--catalog", type=Path, required=True); parser.add_argument("--userdb", type=Path)
    args=parser.parse_args()
    try:
        out={"catalog":run("catalog_structural_health.py","--catalog",args.catalog),"read_only":True}
        if args.userdb: out["userdb"]=run("userdata_health.py","--userdb",args.userdb)
        print(json.dumps(out,ensure_ascii=False,sort_keys=True)); return 0
    except Exception as error: print(json.dumps({"ok":False,"error":str(error)},ensure_ascii=False)); return 1
if __name__ == "__main__": sys.exit(main())
