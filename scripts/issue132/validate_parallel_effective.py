#!/usr/bin/env python3
from __future__ import annotations

import csv
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

from parallel_overlay import apply_corrections, load_checkpoint_union

ROOT = Path(__file__).resolve().parents[2]
LANES = (1, 2, 3)
RAW_ERROR_RE = re.compile(r"^ERROR:\s*([^:]+):\s*(.+)$")


def load_base():
    p = ROOT / "scripts/issue132/validate_luna_pass_a.py"
    s = importlib.util.spec_from_file_location("issue132_parallel_effective_base", p)
    if s is None or s.loader is None:
        raise SystemExit("cannot load base validator")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def run_frozen_validator():
    p = subprocess.run(
        [sys.executable, "scripts/issue132/validate_parallel_checkpoints.py"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )
    print(p.stdout, end="")
    raw_errors: list[tuple[str, str]] = []
    for line in p.stdout.splitlines():
        m = RAW_ERROR_RE.match(line.strip())
        if m:
            raw_errors.append((m.group(1).strip(), m.group(2).strip()))
    if p.returncode and not raw_errors:
        raise SystemExit("frozen checkpoint validator failed without parseable row errors")
    return p.returncode, raw_errors


def main():
    frozen_rc, raw_errors = run_frozen_validator()

    base = load_base()
    neutral_path = ROOT / "artifacts/issue132/luna-neutral/luna_neutral_review_input_v2.csv"
    neutral = read_csv(neutral_path)
    errors: list[str] = []
    total = 0
    summary = {}
    corrected_identities: set[str] = set()
    raw_locations: dict[str, tuple[int, int, int]] = {}

    for lane in LANES:
        assigned = [r for r in neutral if ((int(r["review_seq"]) - 1) % 3) + 1 == lane]
        raw, ranges, load_errors = load_checkpoint_union(ROOT, lane, base.FIELDS)
        errors.extend(load_errors)

        for local_index, row in enumerate(raw, start=1):
            ident = row.get("identity_key", "")
            try:
                seq = int(row.get("review_seq", ""))
            except Exception:
                continue
            if ident:
                raw_locations[ident] = (lane, local_index, seq)

        effective, correction_count, correction_errors = apply_corrections(
            ROOT, lane, raw, ranges, base.FIELDS
        )
        errors.extend(correction_errors)

        for raw_row, effective_row in zip(raw, effective):
            if raw_row != effective_row:
                ident = effective_row.get("identity_key", "")
                if ident:
                    corrected_identities.add(ident)

        for local_index, row in enumerate(effective, start=1):
            ident = row.get("identity_key", "")
            seq = next(
                (int(x["review_seq"]) for x in assigned if x["identity_key"] == ident),
                None,
            )
            if seq is None:
                errors.append(f"lane {lane} local {local_index}: unassigned identity {ident}")
            else:
                row_errors = base.validate_row(row, seq)
                errors.extend(
                    f"lane {lane} local {local_index} review_seq {seq}: {err}"
                    for err in row_errors
                )

        total += len(effective)
        summary[str(lane)] = {
            "reviewed": len(effective),
            "assigned": len(assigned),
            "checkpoints": len(ranges),
            "corrections_applied": correction_count,
        }

    uncovered_raw_errors = []
    for ident, message in raw_errors:
        loc = raw_locations.get(ident)
        if loc:
            lane, local_index, seq = loc
            print(
                f"RAW_DIAGNOSTIC: lane {lane} local {local_index} review_seq {seq} "
                f"identity {ident}: {message}"
            )
        else:
            print(f"RAW_DIAGNOSTIC: identity {ident}: {message}")

        if ident not in corrected_identities:
            uncovered_raw_errors.append((ident, message))

    if frozen_rc and uncovered_raw_errors:
        for ident, message in uncovered_raw_errors:
            loc = raw_locations.get(ident)
            if loc:
                lane, local_index, seq = loc
                errors.append(
                    f"lane {lane} local {local_index} review_seq {seq}: "
                    f"raw checkpoint error is not covered by a valid correction overlay: "
                    f"{ident}: {message}"
                )
            else:
                errors.append(
                    f"raw checkpoint error is not covered by a valid correction overlay: "
                    f"{ident}: {message}"
                )

    result = {
        "schema_version": "issue132-parallel-effective-validation-v2",
        "reviewed_total": total,
        "lanes": summary,
        "raw_validator_returncode": frozen_rc,
        "raw_error_count": len(raw_errors),
        "raw_errors_covered_by_corrections": len(raw_errors) - len(uncovered_raw_errors),
        "error_count": len(errors),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        for e in errors[:100]:
            print("ERROR:", e)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
