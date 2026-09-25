#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from codex_qa_packet import build_packet
from codex_runtime import load_runtime

ROOT = Path(__file__).resolve().parents[2]


def snapshot() -> dict:
    result = subprocess.run(
        [sys.executable, "scripts/issue132/validate_flat_pass_a.py"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise SystemExit("flat validator failed:\n" + result.stdout[-12000:])
    marker = "FLAT_SNAPSHOT_JSON="
    for line in result.stdout.splitlines():
        if line.startswith(marker):
            return json.loads(line[len(marker):])
    raise SystemExit("flat validator did not emit snapshot")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", type=int, required=True, choices=(1, 2, 3))
    ap.add_argument("--through", type=int, required=True)
    args = ap.parse_args()

    authority, _, qa, runtime_errors = load_runtime(ROOT)
    if runtime_errors:
        raise SystemExit("runtime errors: " + "; ".join(runtime_errors))

    packet = build_packet(args.lane)
    if packet.get("status") != "READY":
        raise SystemExit(
            f"no QA epoch ready for lane {args.lane}: {packet.get('status')}"
        )
    expected_end = int(packet["lane_local_end"])
    if args.through != expected_end:
        raise SystemExit(
            f"--through {args.through} must equal audited packet end {expected_end}"
        )

    # An epoch cannot be marked clean while it still contains unresolved HOLDs.
    holds = [
        row["lane_local_index"]
        for row in packet["rows"]
        if row.get("current_kind") == "hold"
    ]
    if holds:
        raise SystemExit(
            "QA epoch still contains HOLDs; repair before advancing: "
            + ",".join(map(str, holds[:50]))
        )

    state_path = ROOT / authority["qa"]["state_path"]
    state = json.loads(state_path.read_text(encoding="utf-8"))
    lane_key = str(args.lane)
    old = int(state["last_codex_qa_by_lane"][lane_key])
    expected_start = old + 1
    if int(packet["lane_local_start"]) != expected_start:
        raise SystemExit("QA cursor/packet start mismatch")

    state["last_codex_qa_by_lane"][lane_key] = expected_end
    state.setdefault("completed_epochs", []).append({
        "lane": args.lane,
        "lane_local_start": expected_start,
        "lane_local_end": expected_end,
        "selected_count": int(packet["selected_count"]),
        "packet_sha256": packet["packet_sha256"],
    })

    lane_lengths = authority["fixed"]["lane_lengths"]
    caught_up = all(
        int(state["last_codex_qa_by_lane"][str(lane)])
        >= int(lane_lengths[str(lane)])
        for lane in (1, 2, 3)
    )

    current = snapshot()
    clean_data = (
        current.get("processed_slot_total") == 31003
        and current.get("baseline_hold_count") == 0
        and current.get("baseline_semantic_lint_count") == 0
        and current.get("forward_hold_count") == 0
        and current.get("invalid_window_count") == 0
        and current.get("duplicate_coverage_count") == 0
        and current.get("fatal_contract_error_count") == 0
    )
    if caught_up and clean_data:
        state["final_internal_qa_passed"] = True

    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "lane": args.lane,
        "old_qa_cursor": old,
        "new_qa_cursor": expected_end,
        "final_internal_qa_passed": state["final_internal_qa_passed"],
        "state_path": str(state_path.relative_to(ROOT)),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
