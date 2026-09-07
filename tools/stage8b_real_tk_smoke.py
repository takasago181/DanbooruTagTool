"""Production Tk smoke and screenshots for Stage 8B Pilot."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danbooru_tag_tool.ui import Stage7AApp, create_window
from tools.stage7a_real_tk_smoke import capture_window_png


OUT = ROOT / "benchmarks/stage8b/real_tk_smoke.json"
CASES = (
    ("semantic", ("161",), "900x540", "STAGE8B_REAL_TK_ANAL_TRAINING.png", "anus", 1),
    ("statistical", ("312",), "1120x760", "STAGE8B_REAL_TK_SEX_MACHINE.png", "machine", 1),
    ("control", ("88",), "maximized", "STAGE8B_REAL_TK_MASTURBATION_CONTROL.png", "solo", 1),
    ("multi_relation", ("88", "122"), "1120x760",
     "STAGE8B_REAL_TK_MULTI_RELATION.png", "on_back", 2),
)


def pump(root, seconds=.2):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        root.update_idletasks()
        root.update()
        time.sleep(.02)


def pump_until(root, predicate, seconds=20):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        pump(root, .05)
        if predicate():
            return True
    return False


def add_special(app, special_id):
    term = app.knowledge.special[special_id].term
    app.search_var.set(term)
    app._run_search()
    index = next(index for index, item in enumerate(app.special_rows)
                 if item.special_id == special_id)
    app.special_list.selection_set(index)
    app.special_list.activate(index)
    app._add_clicked_special()


def click(root, widget):
    widget.event_generate("<Enter>")
    widget.event_generate("<ButtonPress-1>", x=max(1, widget.winfo_width() // 2),
                          y=max(1, widget.winfo_height() // 2))
    widget.event_generate("<ButtonRelease-1>", x=max(1, widget.winfo_width() // 2),
                          y=max(1, widget.winfo_height() // 2))
    pump(root, .1)


def bounds(root, widget):
    root.update_idletasks()
    rx, ry = root.winfo_rootx(), root.winfo_rooty()
    left, top = widget.winfo_rootx(), widget.winfo_rooty()
    right, bottom = left + widget.winfo_width(), top + widget.winfo_height()
    return {
        "viewable": bool(widget.winfo_viewable()),
        "within_root": (
            left >= rx and top >= ry
            and right <= rx + root.winfo_width()
            and bottom <= ry + root.winfo_height()
        ),
        "bounds": [left, top, right, bottom],
    }


def run_case(kind, special_ids, geometry, screenshot_name, target_canonical,
             expected_relation_count):
    root = create_window(ROOT)
    app = next(child for child in root.winfo_children() if isinstance(child, Stage7AApp))
    try:
        if geometry == "maximized":
            root.state("zoomed")
        else:
            root.geometry(geometry)
        pump(root, .2)
        started = time.monotonic()
        for special_id in special_ids:
            add_special(app, special_id)
        schedule_return_ms = (time.monotonic() - started) * 1000
        assert pump_until(root, lambda: app.recommendation_result.status != "empty")
        app.recommendation_notebook.select(app.semantic_support_tab)
        pump(root, .2)
        support_texts = [str(child.cget("text"))
                         for child in app.semantic_support_frame.winfo_children()
                         if child.winfo_class() == "TLabel"]
        buttons = [child for child in app.semantic_support_frame.winfo_children()
                   if child.winfo_class() == "TButton"]
        target_index = next(
            index for index, candidate in enumerate(app.semantic_support_candidates)
            if candidate.canonical == target_canonical
        )
        add_button = buttons[target_index]
        add_button_bounds = bounds(root, add_button)
        target_candidate = app.semantic_support_candidates[target_index]
        added_canonical = target_candidate.canonical
        click(root, add_button)
        added = added_canonical in app.session.manual_auxiliary_canonicals
        added_state = any(
            child.cget("text") == "追加済み"
            for child in app.semantic_support_frame.winfo_children()
            if child.winfo_class() == "TButton"
        )
        click(root, app.copy_button)
        clipboard_matches = root.clipboard_get() == app.session.clipboard_text
        screenshot = ROOT / "docs/stage_reports" / screenshot_name
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        width, height, method = capture_window_png(root, screenshot)
        payload = {
            "kind": kind,
            "special_ids": list(special_ids),
            "special_terms": [app.knowledge.special[special_id].term
                              for special_id in special_ids],
            "geometry": geometry,
            "root_size": [root.winfo_width(), root.winfo_height()],
            "stage7b_status": app.recommendation_result.status,
            "stage7b_base_count": app.recommendation_result.base_count,
            "support_candidate_count": len(app.semantic_support_candidates),
            "target_relation_count": len(target_candidate.relations),
            "target_relation_owner_special_ids": [
                relation.owner_special_id for relation in target_candidate.relations
            ],
            "support_tab_text": app.recommendation_notebook.tab(app.semantic_support_tab, "text"),
            "support_intro_visible": any("投稿統計ではなく" in text for text in support_texts),
            "support_slot_visible": any(text.startswith("[") for text in support_texts),
            "support_reason_visible": any("候補" in text and not text.startswith("[")
                                          for text in support_texts),
            "fake_statistics_in_support": any(
                token in text for text in support_texts for token in ("枚", "%", "Lift")
            ),
            "add_button_before_click": add_button_bounds,
            "manual_auxiliary_added": added,
            "added_canonical": added_canonical,
            "added_state_visible": added_state,
            "selected_special_ids": list(app.session.selected_special_ids),
            "prompt_preview": app.session.prompt_preview,
            "clipboard_matches_export": clipboard_matches,
            "ui_thread_nonblocking": schedule_return_ms < 100,
            "schedule_return_ms": schedule_return_ms,
            "recommendation_bounds": bounds(root, app.recommendation_box),
            "support_tab_bounds": bounds(root, app.semantic_support_tab),
            "prompt_bounds": bounds(root, app.prompt_bar),
            "copy_bounds": bounds(root, app.copy_button),
            "screenshot": str(screenshot.relative_to(ROOT)).replace("\\", "/"),
            "screenshot_size": [width, height],
            "screenshot_capture_method": method,
            "screenshot_sha256": hashlib.sha256(screenshot.read_bytes()).hexdigest(),
        }
        required = (
            payload["support_candidate_count"] > 0,
            payload["target_relation_count"] == expected_relation_count,
            set(payload["target_relation_owner_special_ids"])
            == ({*special_ids} if expected_relation_count > 1 else {special_ids[0]}),
            payload["support_tab_text"] == "意味から補助",
            payload["support_intro_visible"], payload["support_slot_visible"],
            payload["support_reason_visible"], not payload["fake_statistics_in_support"],
            add_button_bounds["viewable"], add_button_bounds["within_root"],
            added, added_state, clipboard_matches, payload["ui_thread_nonblocking"],
            all(payload[name]["viewable"] and payload[name]["within_root"] for name in (
                "recommendation_bounds", "support_tab_bounds", "prompt_bounds", "copy_bounds"
            )),
        )
        payload["pass"] = all(required)
        return payload
    finally:
        app.close()
        root.destroy()


def main():
    cases = [run_case(*case) for case in CASES]
    payload = {
        "python_executable": sys.executable,
        "cases": cases,
        "all_pass": all(case["pass"] for case in cases),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
