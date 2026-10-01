"""Read-only UserData SQLite health and inventory, intentionally separate from catalog checks."""
from __future__ import annotations
import argparse, hashlib, json, sqlite3, sys
from pathlib import Path
from contextlib import closing

def inspect(path: Path) -> dict:
    if not path.is_file(): raise FileNotFoundError(path)
    hasher=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""): hasher.update(block)
    digest = hasher.hexdigest().upper()
    uri = f"{path.resolve().as_uri()}?mode=ro&immutable=1"
    with closing(sqlite3.connect(uri, uri=True)) as db:
        quick = db.execute("PRAGMA quick_check").fetchall()
        integrity = db.execute("PRAGMA integrity_check").fetchall()
        foreign = db.execute("PRAGMA foreign_key_check").fetchall()
        if quick != [("ok",)] or integrity != [("ok",)] or foreign: raise ValueError("UserData SQLite integrity failure")
        columns = {r[1] for r in db.execute("PRAGMA table_info(user_state)")}
        if not {"id", "version", "payload"}.issubset(columns): raise ValueError("user_state schema missing required columns")
        row = db.execute("SELECT version,payload FROM user_state WHERE id=1").fetchone()
        if row is not None:
            if row[0] != 1: raise ValueError(f"unsupported UserData version {row[0]}")
            json.loads(row[1])
    return {"ok": True, "path": str(path.resolve()), "sha256": digest, "bytes": path.stat().st_size, "state_present": row is not None}

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--userdb",type=Path,required=True); a=p.parse_args()
    try: print(json.dumps(inspect(a.userdb),sort_keys=True)); return 0
    except Exception as e: print(json.dumps({"ok":False,"error":str(e)})); return 1
if __name__ == "__main__": sys.exit(main())
