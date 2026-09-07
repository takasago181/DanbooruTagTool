from __future__ import annotations

import hashlib
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

FILES = [
    {
        "name": "available_tags.csv",
        "url": "https://huggingface.co/spaces/u-haru/danbooru_tagsearch/raw/main/available_tags.csv",
        "sha256": None,
        "size": None,
    },
    {
        "name": "cooccurrence_all_normalized.npz",
        "url": "https://huggingface.co/spaces/u-haru/danbooru_tagsearch/resolve/main/cooccurrence_all_normalized.npz?download=true",
        "sha256": "dc1749f1d00f8b7063015176b81b603b49552c341074993c50c4390d8c8b6ca6",
        "size": 455_719_557,
    },
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(4 * 1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path):
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "DanbooruCooccurrencePrototype/0.1"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp, tmp.open("wb") as f:
        total = resp.headers.get("Content-Length")
        total = int(total) if total and total.isdigit() else 0
        done = 0
        started = time.time()
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
            done += len(chunk)
            elapsed = max(time.time() - started, 0.1)
            speed = done / elapsed / (1024 * 1024)
            if total:
                pct = done * 100 / total
                print(f"\r{dest.name}: {pct:6.2f}%  {done/1024/1024:8.1f}/{total/1024/1024:.1f} MiB  {speed:5.1f} MiB/s", end="")
            else:
                print(f"\r{dest.name}: {done/1024/1024:8.1f} MiB  {speed:5.1f} MiB/s", end="")
    print()
    tmp.replace(dest)


def main():
    for item in FILES:
        dest = DATA / item["name"]
        expected_sha = item["sha256"]
        expected_size = item["size"]

        if dest.exists():
            ok = True
            if expected_size is not None and dest.stat().st_size != expected_size:
                ok = False
            if expected_sha is not None and sha256_file(dest) != expected_sha:
                ok = False
            if ok:
                print(f"[OK] {dest.name} は取得済みです。")
                continue
            print(f"[WARN] {dest.name} の検証に失敗したため再取得します。")
            dest.unlink()

        print(f"[DOWNLOAD] {dest.name}")
        download(item["url"], dest)

        if expected_size is not None and dest.stat().st_size != expected_size:
            raise RuntimeError(
                f"{dest.name}: size mismatch: {dest.stat().st_size} != {expected_size}"
            )
        if expected_sha is not None:
            actual = sha256_file(dest)
            if actual != expected_sha:
                raise RuntimeError(
                    f"{dest.name}: SHA-256 mismatch:\n{actual}\n!=\n{expected_sha}"
                )

        if dest.name == "available_tags.csv":
            first = dest.open("r", encoding="utf-8-sig").readline().strip()
            if first != "tag,count,category,available":
                raise RuntimeError(f"available_tags.csv header mismatch: {first}")

        print(f"[VERIFIED] {dest.name}")

    print("\n共起データの準備が完了しました。")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        input("Enterで終了...")
        raise
