from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

from engine import CooccurrenceEngine

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Danbooru 共起タグ推薦 Prototype")
        self.geometry("1180x760")
        self.minsize(980, 640)

        self.engine: CooccurrenceEngine | None = None
        self.last_results = []
        self.last_resolved = []

        self._build_ui()
        self.after(200, self._start_loading)

    def _build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Label(
            top,
            text="入力タグ（カンマ / 改行区切り）",
            font=("", 11, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self.input_text = tk.Text(top, height=4, width=90)
        self.input_text.grid(row=1, column=0, columnspan=8, sticky="ew", pady=(4, 8))
        self.input_text.insert("1.0", "twintails, school uniform")

        ttk.Label(top, text="推薦対象").grid(row=2, column=0, sticky="w")
        self.category = ttk.Combobox(
            top,
            values=["general", "character", "copyright", "all"],
            state="readonly",
            width=14,
        )
        self.category.set("general")
        self.category.grid(row=2, column=1, sticky="w", padx=(4, 16))

        ttk.Label(top, text="スコア方式").grid(row=2, column=2, sticky="w")
        self.mode = ttk.Combobox(
            top,
            values=["共通重視", "バランス", "最弱一致", "件数重視"],
            state="readonly",
            width=14,
        )
        self.mode.set("共通重視")
        self.mode.grid(row=2, column=3, sticky="w", padx=(4, 16))

        ttk.Label(top, text="件数").grid(row=2, column=4, sticky="w")
        self.top_n = tk.IntVar(value=100)
        ttk.Spinbox(top, from_=10, to=1000, increment=10, textvariable=self.top_n, width=8).grid(
            row=2, column=5, sticky="w", padx=(4, 16)
        )

        self.ignore_generic = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            top,
            text="1girl / solo等の巨大汎用タグを除外",
            variable=self.ignore_generic,
        ).grid(row=2, column=6, sticky="w")

        self.search_btn = ttk.Button(top, text="推薦を計算", command=self._search, state="disabled")
        self.search_btn.grid(row=2, column=7, sticky="e", padx=(8, 0))
        top.columnconfigure(0, weight=1)

        self.resolution_label = ttk.Label(self, text="入力解決: -", padding=(10, 0))
        self.resolution_label.pack(fill="x")

        columns = (
            "rank", "tag", "ja", "category", "score",
            "weakest", "coverage", "cooc_count", "current_count"
        )
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=22)
        headings = {
            "rank": "#",
            "tag": "Tag",
            "ja": "日本語（2788辞書にある場合）",
            "category": "種別",
            "score": "推薦Score",
            "weakest": "最弱共起",
            "coverage": "入力Coverage",
            "cooc_count": "共起元件数(2026-05)",
            "current_count": "辞書件数(2026-09)",
        }
        widths = {
            "rank": 45, "tag": 210, "ja": 260, "category": 90, "score": 90,
            "weakest": 90, "coverage": 90, "cooc_count": 125, "current_count": 125,
        }
        for c in columns:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c], anchor="w")
        self.tree.column("rank", anchor="e")
        self.tree.column("score", anchor="e")
        self.tree.column("weakest", anchor="e")
        self.tree.column("coverage", anchor="e")
        self.tree.column("cooc_count", anchor="e")
        self.tree.column("current_count", anchor="e")

        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        frame = ttk.Frame(self, padding=(10, 6))
        frame.pack(fill="both", expand=True)
        self.tree.pack(in_=frame, side="left", fill="both", expand=True)
        yscroll.pack(in_=frame, side="right", fill="y")

        self.tree.bind("<Double-1>", self._add_selected)

        bottom = ttk.Frame(self, padding=10)
        bottom.pack(fill="x")
        ttk.Button(bottom, text="選択タグを入力へ追加", command=self._add_selected).pack(side="left")
        ttk.Button(bottom, text="結果をクリップボードへ", command=self._copy_results).pack(side="left", padx=8)
        ttk.Label(bottom, text="ダブルクリックでも入力へ追加できます。").pack(side="left", padx=8)

        self.status = ttk.Label(bottom, text="起動中…")
        self.status.pack(side="right")

    def _start_loading(self):
        required = [
            DATA / "available_tags.csv",
            DATA / "cooccurrence_all_normalized.npz",
        ]
        missing = [p.name for p in required if not p.exists()]
        if missing:
            self.status.config(text="共起データ未取得")
            messagebox.showinfo(
                "初回データが必要です",
                "共起データがまだありません。\n\n"
                "先に DOWNLOAD_DATA.bat を実行してください。\n"
                "約456MBの共起行列とタグ索引を取得します。",
            )
            return

        self.status.config(text="共起行列をロード中…")
        threading.Thread(target=self._load_engine, daemon=True).start()

    def _load_engine(self):
        try:
            engine = CooccurrenceEngine(DATA)
            info = engine.load()
            self.engine = engine
            msg = (
                f"準備完了: {info['tag_count']:,} tags / "
                f"{info['matrix_shape'][0]:,}×{info['matrix_shape'][1]:,} / "
                f"RAM約{info['matrix_ram_gib']:.2f} GiB"
            )
            self.after(0, lambda: self.status.config(text=msg))
            self.after(0, lambda: self.search_btn.config(state="normal"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("ロード失敗", str(e)))
            self.after(0, lambda: self.status.config(text="ロード失敗"))

    def _raw_tags(self):
        txt = self.input_text.get("1.0", "end").strip()
        txt = txt.replace("\n", ",")
        return [x.strip() for x in txt.split(",") if x.strip()]

    def _search(self):
        if not self.engine:
            return

        mode_map = {
            "共通重視": "common",
            "バランス": "balanced",
            "最弱一致": "weakest",
            "件数重視": "frequency",
        }
        self.search_btn.config(state="disabled")
        self.status.config(text="計算中…")
        args = (
            self._raw_tags(),
            self.category.get(),
            mode_map[self.mode.get()],
            int(self.top_n.get()),
            bool(self.ignore_generic.get()),
        )
        threading.Thread(target=self._run_search, args=args, daemon=True).start()

    def _run_search(self, tags, category, mode, top_n, ignore_generic):
        try:
            resolved, results = self.engine.search(
                tags,
                category=category,
                mode=mode,
                top_n=top_n,
                ignore_generic=ignore_generic,
            )
            self.last_resolved = resolved
            self.last_results = results
            self.after(0, self._render_results)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("検索エラー", str(e)))
        finally:
            self.after(0, lambda: self.search_btn.config(state="normal"))
            self.after(0, lambda: self.status.config(text=f"結果: {len(self.last_results)}件"))

    def _render_results(self):
        self.tree.delete(*self.tree.get_children())

        resolution = " / ".join(
            f"{r.original} → {r.canonical} [{r.source}]"
            for r in self.last_resolved
        )
        self.resolution_label.config(text=f"入力解決: {resolution}")

        for rank, r in enumerate(self.last_results, 1):
            self.tree.insert(
                "",
                "end",
                iid=str(rank - 1),
                values=(
                    rank,
                    r.prompt_tag,
                    r.japanese,
                    r.category,
                    f"{r.score:.5f}",
                    f"{r.weakest:.5f}",
                    f"{r.coverage:.0%}",
                    f"{r.cooc_count:,}",
                    "" if r.current_count is None else f"{r.current_count:,}",
                ),
            )

    def _add_selected(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if idx >= len(self.last_results):
            return
        tag = self.last_results[idx].prompt_tag
        current = self.input_text.get("1.0", "end").strip()
        if current and not current.endswith(","):
            current += ", "
        current += tag
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", current)

    def _copy_results(self):
        if not self.last_results:
            return
        text = "\n".join(
            f"{r.prompt_tag}\t{r.japanese}\t{r.score:.6f}\t{r.cooc_count}"
            for r in self.last_results
        )
        self.clipboard_clear()
        self.clipboard_append(text)


if __name__ == "__main__":
    App().mainloop()
