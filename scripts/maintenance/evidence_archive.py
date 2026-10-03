"""Recover frozen research into a NEW external directory; never restore over a checkout."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "research/archive/foundation-b.json"

def safe_destination(output: Path, root: Path = ROOT) -> Path:
    output = output.absolute()
    if any(p.is_symlink() or p.is_junction() for p in [output, *output.parents]):
        raise ValueError("Output cannot traverse filesystem links")
    if output.exists() or output.is_relative_to(root.resolve()):
        raise ValueError("Output must be a new directory outside this checkout")
    # A different checkout/runtime must not be an archive destination either.
    for parent in output.parents:
        if (parent / ".git").exists() or parent.name.lower() == "userdata" or (parent / "runtime-manifest.json").exists():
            raise ValueError("Output cannot be inside a checkout, runtime or UserData")
    return output

def verify(directory: Path, manifest: dict) -> int:
    for item in manifest["files"]:
        path = directory / item["path"]
        if path.stat().st_size != item["bytes"] or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Archive hash mismatch: {item['path']}")
    return len(manifest["files"])

def restore(output: Path, manifest: dict) -> int:
    output = safe_destination(output)
    revision = manifest["source_commit"]
    subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", revision + "^{commit}"], check=True)
    # Full frozen source tree keeps historical imports, relative paths and tests reproducible.
    # No network, workflow execution or source authority regeneration occurs here.
    with tempfile.TemporaryDirectory(prefix="DTT-evidence-") as scratch:
        archive = Path(scratch) / "source.zip"
        subprocess.run(["git", "-C", str(ROOT), "archive", "--format=zip", "-o", str(archive), revision], check=True)
        with zipfile.ZipFile(archive) as z:
            for item in z.infolist():
                path = PurePosixPath(item.filename)
                if path.is_absolute() or ".." in path.parts or "\\" in item.filename or ":" in item.filename or (item.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("Unsafe archive member")
            output.mkdir(parents=True, exist_ok=False)
            z.extractall(output)
    return verify(output, manifest)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["restore", "verify"])
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    count = restore(args.directory, manifest) if args.action == "restore" else verify(args.directory, manifest)
    print(f"PASS {args.action}: {count} frozen research/tool/workflow assets")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
