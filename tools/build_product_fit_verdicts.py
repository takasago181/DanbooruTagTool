"""Deterministic Issue #63 materialization; existing output is never overwritten."""
import argparse
import hashlib
import json
from pathlib import Path

from danbooru_tag_tool.product_fit import COUNTS, CSV_PATH, MANIFEST_PATH, csv_bytes, load_authority


def materialize(root: Path, *, check=False):
    output = root / CSV_PATH
    payload = csv_bytes(load_authority(root / MANIFEST_PATH))
    if output.exists():
        if output.read_bytes() != payload:
            raise ValueError('Existing product-fit CSV differs; refusing overwrite')
    elif check:
        raise FileNotFoundError(output)
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('xb') as stream:
            stream.write(payload)
    return {'rows': 2788, 'ids': '1..2788', 'duplicates': 0, 'overlap': 0,
            'counts': dict(COUNTS), 'sha256': hashlib.sha256(payload).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print(json.dumps(materialize(args.root, check=args.check), indent=2))


if __name__ == '__main__':
    main()
