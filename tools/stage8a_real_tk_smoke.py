"""Production Tk smoke and screenshot for Stage 8A v2."""
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


CORE = ("anal", "butt_plug")
SCREENSHOT = ROOT / "docs/stage_reports/STAGE8A_V2_REAL_TK_SCREENSHOT.png"
RESULT = ROOT / "benchmarks/stage8a/real_tk_smoke.json"


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


def add_special_via_search(app, special_id):
    term = app.knowledge.special[special_id].term
    app.search_var.set(term)
    app._run_search()
    index = next(index for index, item in enumerate(app.special_rows)
                 if item.special_id == special_id)
    app.special_list.selection_clear(0, "end")
    app.special_list.selection_set(index)
    app.special_list.activate(index)
    app._add_clicked_special()


def visible_bounds(root, widget):
    root.update_idletasks()
    root_x, root_y = root.winfo_rootx(), root.winfo_rooty()
    left, top = widget.winfo_rootx(), widget.winfo_rooty()
    right, bottom = left + widget.winfo_width(), top + widget.winfo_height()
    return {
        "mapped": bool(widget.winfo_ismapped()),
        "viewable": bool(widget.winfo_viewable()),
        "within_root": (
            left >= root_x and top >= root_y
            and right <= root_x + root.winfo_width()
            and bottom <= root_y + root.winfo_height()
        ),
        "bounds": [left, top, right, bottom],
    }


def click_widget(root, widget):
    widget.event_generate("<Enter>")
    widget.event_generate("<ButtonPress-1>", x=max(1, widget.winfo_width() // 2),
                          y=max(1, widget.winfo_height() // 2))
    widget.event_generate("<ButtonRelease-1>", x=max(1, widget.winfo_width() // 2),
                          y=max(1, widget.winfo_height() // 2))
    pump(root, .1)


def geometry_snapshot(root, app, geometry):
    root.state("normal")
    root.geometry(geometry)
    pump(root, .2)
    first_hint = next(
        child for child in app.common_recommendations.winfo_children()
        if child.winfo_class() == "TLabel"
        and "タグ" in str(child.cget("text"))
        and " / " not in str(child.cget("text"))
    )
    snapshot = {
        "root": [root.winfo_width(), root.winfo_height()],
        "recommendation": visible_bounds(root, app.recommendation_box),
        "notebook": visible_bounds(root, app.recommendation_notebook),
        "first_generation_hint": visible_bounds(root, first_hint),
        "prompt": visible_bounds(root, app.prompt_bar),
        "copy": visible_bounds(root, app.copy_button),
    }
    snapshot["recommendation_prompt_do_not_overlap"] = (
        snapshot["recommendation"]["bounds"][3] <= snapshot["prompt"]["bounds"][1]
    )
    return snapshot


def main():
    root = create_window(ROOT)
    app = next(child for child in root.winfo_children() if isinstance(child, Stage7AApp))
    try:
        special_ids = tuple(
            next(sid for sid, special in app.knowledge.special.items()
                 if special.chosen_canonical == canonical and special.term.replace(" ", "_") == canonical)
            for canonical in CORE
        )
        started = time.monotonic()
        for special_id in special_ids:
            add_special_via_search(app, special_id)
        schedule_return_ms = (time.monotonic() - started) * 1000
        if not pump_until(root, lambda: app.recommendation_result.status == "ready"):
            raise TimeoutError("Stage 8A recommendation did not finish")

        common_texts = [str(child.cget("text"))
                        for child in app.common_recommendations.winfo_children()
                        if child.winfo_class() == "TLabel"]
        app.recommendation_notebook.select(app.rare_recommendation_tab)
        pump(root, .1)
        rare_texts = [str(child.cget("text"))
                      for child in app.rare_recommendations.winfo_children()
                      if child.winfo_class() == "TLabel"]
        app.recommendation_notebook.select(app.common_recommendation_tab)
        pump(root, .1)

        add_button = next(
            child for child in app.common_recommendations.winfo_children()
            if child.winfo_class() == "TButton" and child.cget("text") == "＋追加"
        )
        added_canonical = app.recommendation_result.common[0].canonical
        click_widget(root, add_button)
        added = added_canonical in app.session.manual_auxiliary_canonicals
        added_state = any(
            child.cget("text") == "追加済み"
            for child in app.common_recommendations.winfo_children()
            if child.winfo_class() == "TButton"
        )

        minimum = geometry_snapshot(root, app, "900x540")
        normal = geometry_snapshot(root, app, "1120x760")
        root.state("zoomed")
        pump(root, .3)
        maximized = geometry_snapshot(root, app, f"{root.winfo_width()}x{root.winfo_height()}")
        root.state("zoomed")
        pump(root, .2)

        click_widget(root, app.copy_button)
        clipboard_matches = root.clipboard_get() == app.session.clipboard_text
        SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
        width, height, capture_method = capture_window_png(root, SCREENSHOT)
        role_badges = sorted({
            text.split("]", 1)[0] + "]" for text in common_texts
            if text.startswith("[") and "]" in text
        })
        payload = {
            "python_executable": sys.executable,
            "tk_patchlevel": root.tk.call("info", "patchlevel"),
            "selected_special_ids": list(special_ids),
            "selected_core_canonicals": list(CORE),
            "recommendation_status": app.recommendation_result.status,
            "base_count": app.recommendation_result.base_count,
            "common_candidate_count": len(app.recommendation_result.common),
            "rare_candidate_count": len(app.recommendation_result.rare),
            "semantic_role_badges_in_common": role_badges,
            "generation_hint_visible": any(
                phrase in text for text in common_texts for phrase in (
                    "基礎タグ", "明示しやすいタグ", "行為補強タグ", "直接補強するとは限りません"
                )
            ),
            "rare_low_support_hint_present": any(
                "件数が少ないため偶然の可能性もあります" in text for text in rare_texts
            ),
            "rare_evidence_note_visible": any(
                text.startswith("補足: ")
                and ("発見に向く候補" in text or "偶然の可能性もあります" in text)
                for text in rare_texts
            ),
            "schedule_return_ms": schedule_return_ms,
            "ui_thread_nonblocking": schedule_return_ms < 100,
            "manual_auxiliary_added": added,
            "added_canonical": added_canonical,
            "added_state_visible": added_state,
            "prompt_preview": app.session.prompt_preview,
            "clipboard_matches_export": clipboard_matches,
            "minimum_geometry": minimum,
            "normal_geometry": normal,
            "maximized_geometry": maximized,
            "screenshot": str(SCREENSHOT.relative_to(ROOT)).replace("\\", "/"),
            "screenshot_size": [width, height],
            "screenshot_capture_method": capture_method,
            "screenshot_sha256": hashlib.sha256(SCREENSHOT.read_bytes()).hexdigest(),
        }
        RESULT.parent.mkdir(parents=True, exist_ok=True)
        RESULT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        geometry_ok = all(
            snapshot[name]["viewable"] and snapshot[name]["within_root"]
            for snapshot in (minimum, normal, maximized)
            for name in ("recommendation", "notebook", "first_generation_hint", "prompt", "copy")
        ) and all(
            snapshot["recommendation_prompt_do_not_overlap"]
            for snapshot in (minimum, normal, maximized)
        )
        required = (
            payload["recommendation_status"] == "ready",
            payload["generation_hint_visible"], payload["rare_evidence_note_visible"],
            added, added_state, clipboard_matches, geometry_ok,
        )
        return 0 if all(required) else 1
    finally:
        app.close()
        root.destroy()


if __name__ == "__main__":
    raise SystemExit(main())
