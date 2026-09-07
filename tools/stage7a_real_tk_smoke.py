"""Run the Stage 7A production Tk window and record a real Windows smoke test."""
from __future__ import annotations

import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import sys
import time
import zlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danbooru_tag_tool.ui import Stage7AApp, create_window


SCREENSHOT = ROOT / "docs" / "stage_reports" / "STAGE7A_REAL_TK_SCREENSHOT.png"
RESULT = ROOT / "benchmarks" / "stage7a" / "real_tk_smoke.json"


class BitmapInfoHeader(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


class BitmapInfo(ctypes.Structure):
    _fields_ = [("bmiHeader", BitmapInfoHeader), ("bmiColors", wintypes.DWORD * 3)]


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))


def capture_window_png(root, destination: Path) -> tuple[int, int, str]:
    """Capture only the real Tk top-level window using standard Win32 GDI."""
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    hwnd = user32.GetAncestor(root.winfo_id(), 2)  # GA_ROOT
    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        raise ctypes.WinError()
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    screen_dc = user32.GetDC(0)
    memory_dc = gdi32.CreateCompatibleDC(screen_dc)
    bitmap = gdi32.CreateCompatibleBitmap(screen_dc, width, height)
    previous = gdi32.SelectObject(memory_dc, bitmap)
    try:
        method = "PrintWindow"
        if not user32.PrintWindow(hwnd, memory_dc, 2):  # PW_RENDERFULLCONTENT
            method = "BitBlt"
            if not gdi32.BitBlt(memory_dc, 0, 0, width, height, screen_dc, rect.left, rect.top, 0x00CC0020):
                raise ctypes.WinError()
        info = BitmapInfo()
        info.bmiHeader.biSize = ctypes.sizeof(BitmapInfoHeader)
        info.bmiHeader.biWidth = width
        info.bmiHeader.biHeight = -height
        info.bmiHeader.biPlanes = 1
        info.bmiHeader.biBitCount = 32
        info.bmiHeader.biCompression = 0
        pixels = ctypes.create_string_buffer(width * height * 4)
        if gdi32.GetDIBits(memory_dc, bitmap, 0, height, pixels, ctypes.byref(info), 0) != height:
            raise ctypes.WinError()
        raw = pixels.raw
        rows = []
        stride = width * 4
        for y in range(height):
            bgra = raw[y * stride : (y + 1) * stride]
            rgb = bytearray(width * 3)
            for x in range(width):
                source = x * 4
                target = x * 3
                rgb[target : target + 3] = bgra[source + 2], bgra[source + 1], bgra[source]
            rows.append(b"\x00" + bytes(rgb))
        png = b"\x89PNG\r\n\x1a\n"
        png += png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        png += png_chunk(b"IDAT", zlib.compress(b"".join(rows), level=9))
        png += png_chunk(b"IEND", b"")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(png)
        return width, height, method
    finally:
        gdi32.SelectObject(memory_dc, previous)
        gdi32.DeleteObject(bitmap)
        gdi32.DeleteDC(memory_dc)
        user32.ReleaseDC(0, screen_dc)


def visible_widget_bounds(root, widget, label: str) -> dict[str, object]:
    root.update_idletasks()
    root_left = root.winfo_rootx()
    root_top = root.winfo_rooty()
    root_right = root_left + root.winfo_width()
    root_bottom = root_top + root.winfo_height()
    left = widget.winfo_rootx()
    top = widget.winfo_rooty()
    right = left + widget.winfo_width()
    bottom = top + widget.winfo_height()
    mapped = bool(widget.winfo_ismapped())
    viewable = bool(widget.winfo_viewable())
    within_root = (
        root_left <= left < right <= root_right
        and root_top <= top < bottom <= root_bottom
    )
    if not (mapped and viewable and within_root):
        raise AssertionError(
            f"{label} is not visibly inside the root: "
            f"mapped={mapped}, viewable={viewable}, widget={(left, top, right, bottom)}, "
            f"root={(root_left, root_top, root_right, root_bottom)}"
        )
    return {
        "mapped": mapped,
        "viewable": viewable,
        "within_root": within_root,
        "bounds": [left, top, right, bottom],
    }


def geometry_visibility(root, app) -> dict[str, object]:
    root.update()
    return {
        "root_size": [root.winfo_width(), root.winfo_height()],
        "prompt_bar": visible_widget_bounds(root, app.prompt_bar, "Prompt bar"),
        "prompt_text": visible_widget_bounds(root, app.prompt_text, "Prompt preview"),
        "copy_button": visible_widget_bounds(root, app.copy_button, "Prompt copy button"),
    }


def click_visible_copy_button(root, app) -> list[int]:
    visible_widget_bounds(root, app.copy_button, "Prompt copy button")
    app.clipboard_clear()
    app.clipboard_append("stage7a-copy-not-yet-triggered")
    root.update()
    x = max(2, app.copy_button.winfo_width() // 2)
    y = max(2, app.copy_button.winfo_height() // 2)
    app.copy_button.event_generate("<Enter>", x=x, y=y)
    app.copy_button.event_generate("<ButtonPress-1>", x=x, y=y)
    root.update()
    app.copy_button.event_generate("<ButtonRelease-1>", x=x, y=y)
    root.update()
    if root.clipboard_get() != app.session.clipboard_text:
        raise AssertionError("Visible Prompt copy button did not copy PromptSession export")
    if app.copy_feedback.cget("text") != "コピーしました":
        raise AssertionError("Visible Prompt copy button did not run its production command")
    return [app.copy_button.winfo_rootx() + x, app.copy_button.winfo_rooty() + y]


def main() -> int:
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except (AttributeError, OSError):
        ctypes.windll.user32.SetProcessDPIAware()
    root = create_window(ROOT)
    app = next(child for child in root.winfo_children() if isinstance(child, Stage7AApp))
    normal_exit = False
    try:
        root.update()
        root.lift()
        root.attributes("-topmost", True)
        root.update()
        root.attributes("-topmost", False)

        app.search_entry.focus_force()
        app.search_var.set("青い空")
        app._run_search()
        root.update()
        if not app.general_rows or not app.general_box.winfo_ismapped():
            raise AssertionError("General result frame did not return for a General search result")
        general_positive_case_visible = True

        app.search_var.set("拘束")
        app.search_entry.event_generate("<KeyRelease>")
        time.sleep(0.30)
        root.update()
        special_count = app.special_list.size()
        if special_count < 2:
            raise AssertionError(f"Expected multiple Special results, got {special_count}")

        before_scroll = tuple(app.special_list.yview())
        scrollbar_command = app.special_scrollbar.cget("command")
        app.special_scrollbar.tk.call(scrollbar_command, "moveto", "1.0")
        root.update()
        after_scroll = tuple(app.special_list.yview())
        if before_scroll == after_scroll or after_scroll[1] < 0.99:
            raise AssertionError(f"Scrollbar did not move the Listbox: {before_scroll} -> {after_scroll}")
        app.special_scrollbar.tk.call(scrollbar_command, "moveto", "0.0")
        root.update()

        app.special_list.event_generate("<ButtonPress-1>", x=12, y=10)
        app.special_list.event_generate("<ButtonRelease-1>", x=12, y=10)
        root.update()
        if len(app.session.selected_special_ids) != 1:
            raise AssertionError("One-click Special selection was not reflected")
        selected_id = app.session.selected_special_ids[0]
        selected_term = app.knowledge.special[selected_id].term
        preview = app.prompt_text.get("1.0", "end-1c")
        if selected_term.replace("_", " ") not in preview:
            raise AssertionError("Prompt preview did not include the selected Special")
        if app.general_rows or app.general_box.winfo_ismapped():
            raise AssertionError("Empty General result frame remained visible")

        normal_geometry = geometry_visibility(root, app)

        root.state("normal")
        root.geometry("900x540")
        root.update()
        minimum_geometry = geometry_visibility(root, app)
        minimum_copy_click = click_visible_copy_button(root, app)

        root.state("zoomed")
        root.update()
        maximized_geometry = geometry_visibility(root, app)
        maximized_copy_click = click_visible_copy_button(root, app)
        clipboard = root.clipboard_get()

        root.update_idletasks()
        root.update()
        time.sleep(0.25)
        root.update()
        width, height, capture_method = capture_window_png(root, SCREENSHOT)
        payload = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "python_version": sys.version.split()[0],
            "python_executable": sys.executable,
            "tk_patchlevel": root.tk.call("info", "patchlevel"),
            "query": "拘束",
            "special_result_count": special_count,
            "scroll_before": before_scroll,
            "scroll_after": after_scroll,
            "scrollbar_moved": before_scroll != after_scroll,
            "selected_special_id": selected_id,
            "selected_original_term": selected_term,
            "prompt_preview": preview,
            "clipboard_matches_export": clipboard == app.session.clipboard_text,
            "general_result_count": len(app.general_rows),
            "general_frame_hidden": not bool(app.general_box.winfo_ismapped()),
            "general_positive_case_visible": general_positive_case_visible,
            "normal_geometry": normal_geometry,
            "minimum_supported_geometry": minimum_geometry,
            "minimum_copy_click_screen_coordinates": minimum_copy_click,
            "maximized_geometry": maximized_geometry,
            "maximized_copy_click_screen_coordinates": maximized_copy_click,
            "visible_copy_button_click": True,
            "copy_feedback": app.copy_feedback.cget("text"),
            "screenshot": str(SCREENSHOT.relative_to(ROOT)).replace("\\", "/"),
            "screenshot_size": [width, height],
            "screenshot_capture_method": capture_method,
            "screenshot_sha256": hashlib.sha256(SCREENSHOT.read_bytes()).hexdigest(),
            "normal_exit": True,
        }
        RESULT.parent.mkdir(parents=True, exist_ok=True)
        RESULT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        normal_exit = True
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    finally:
        root.destroy()
        if not normal_exit:
            print("Stage 7A real Tk smoke failed before normal shutdown", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
