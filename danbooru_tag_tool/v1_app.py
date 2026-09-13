"""Issue #66 beginner-first v1 desktop shell.

Flow: existing Prompt -> discover (search / Special / General) -> visible selection
-> canonical-English preview/copy.
"""
from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from .knowledge import TagKnowledgeCore
from .search import SearchResult, TagSearchEngine
from .v1_browse import PendingGeneralBrowseProvider, SpecialBrowseProvider
from .v1_search import V1SearchService
from .v1_workspace import PromptWorkspace


ROOT = Path(__file__).resolve().parents[1]


class V1App:
    def __init__(self, root: tk.Tk, knowledge: TagKnowledgeCore | None = None):
        self.root = root
        self.knowledge = knowledge or TagKnowledgeCore.load(ROOT)
        self.workspace = PromptWorkspace(self.knowledge)
        self.search_service = V1SearchService(TagSearchEngine(self.knowledge))
        self.special_provider = SpecialBrowseProvider(self.knowledge, ROOT)
        self.general_provider = PendingGeneralBrowseProvider()
        self._search_results: dict[str, SearchResult] = {}
        self._special_rows: dict[str, str] = {}

        root.title("DanbooruTagTool v1")
        root.geometry("1120x760")
        root.minsize(860, 620)
        self._build()
        self._refresh_workspace()

    def _build(self) -> None:
        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(2, weight=1)

        ttk.Label(outer, text="DanbooruTagTool v1", font=("TkDefaultFont", 15, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(outer, text="日本語で探す → 選ぶ → 並べる → 画面どおりのEnglish Promptをコピー").grid(row=1, column=0, sticky="w", pady=(2, 10))

        body = ttk.Panedwindow(outer, orient="horizontal")
        body.grid(row=2, column=0, sticky="nsew")
        discover = ttk.Frame(body, padding=(0, 0, 8, 0))
        workspace = ttk.Frame(body, padding=(8, 0, 0, 0))
        body.add(discover, weight=3)
        body.add(workspace, weight=2)
        self._build_discovery(discover)
        self._build_workspace(workspace)

        output = ttk.LabelFrame(outer, text="3. 出力", padding=8)
        output.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        output.columnconfigure(0, weight=1)
        self.preview = tk.Text(output, height=4, wrap="word")
        self.preview.grid(row=0, column=0, sticky="ew")
        self.preview.configure(state="disabled")
        ttk.Button(output, text="Promptをコピー", command=self._copy_prompt).grid(row=0, column=1, sticky="ns", padx=(8, 0))
        self.output_status = ttk.Label(output, text="")
        self.output_status.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

    def _build_discovery(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        existing = ttk.LabelFrame(parent, text="1. 既存Promptを読み込む", padding=8)
        existing.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        existing.columnconfigure(0, weight=1)
        self.existing_text = tk.Text(existing, height=4, wrap="word")
        self.existing_text.grid(row=0, column=0, sticky="ew")
        ttk.Button(existing, text="読み込む", command=self._load_existing).grid(row=0, column=1, sticky="ns", padx=(8, 0))
        ttk.Label(existing, text="不明なタグは消さずに『未解決』としてそのまま保持します。").grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

        discovery = ttk.LabelFrame(parent, text="2. タグを発見する", padding=8)
        discovery.grid(row=1, column=0, sticky="nsew")
        discovery.columnconfigure(0, weight=1)
        discovery.rowconfigure(0, weight=1)
        tabs = ttk.Notebook(discovery)
        tabs.grid(row=0, column=0, sticky="nsew")
        self._build_search_tab(tabs)
        self._build_special_tab(tabs)
        self._build_general_tab(tabs)

    def _build_search_tab(self, tabs: ttk.Notebook) -> None:
        tab = ttk.Frame(tabs, padding=8)
        tabs.add(tab, text="検索")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        line = ttk.Frame(tab)
        line.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        line.columnconfigure(0, weight=1)
        self.search_var = tk.StringVar()
        entry = ttk.Entry(line, textvariable=self.search_var)
        entry.grid(row=0, column=0, sticky="ew")
        entry.bind("<Return>", lambda _event: self._run_search())
        ttk.Button(line, text="検索", command=self._run_search).grid(row=0, column=1, padx=(6, 0))

        search_frame = ttk.Frame(tab)
        search_frame.grid(row=1, column=0, sticky="nsew")
        search_frame.columnconfigure(0, weight=1)
        search_frame.rowconfigure(0, weight=1)
        self.search_tree = ttk.Treeview(search_frame, columns=("ja", "en", "match"), show="headings", selectmode="browse", height=14)
        self.search_tree.heading("ja", text="日本語")
        self.search_tree.heading("en", text="English / canonical")
        self.search_tree.heading("match", text="一致")
        self.search_tree.column("ja", width=170, anchor="w")
        self.search_tree.column("en", width=260, anchor="w")
        self.search_tree.column("match", width=80, anchor="w")
        self.search_tree.grid(row=0, column=0, sticky="nsew")
        search_scroll = ttk.Scrollbar(search_frame, orient="vertical", command=self.search_tree.yview)
        search_scroll.grid(row=0, column=1, sticky="ns")
        self.search_tree.configure(yscrollcommand=search_scroll.set)
        self.search_tree.bind("<Double-1>", lambda _event: self._add_search_selected())
        self.search_status = ttk.Label(tab, text="日本語 / English / mixed で検索できます。")
        self.search_status.grid(row=2, column=0, sticky="w", pady=(5, 0))
        ttk.Button(tab, text="選択をPromptへ追加", command=self._add_search_selected).grid(row=3, column=0, sticky="e", pady=(6, 0))

    def _build_special_tab(self, tabs: ttk.Notebook) -> None:
        tab = ttk.Frame(tabs, padding=8)
        tabs.add(tab, text="Special browse")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(2, weight=1)
        controls = ttk.Frame(tab)
        controls.grid(row=0, column=0, sticky="ew")
        controls.columnconfigure(4, weight=1)
        ttk.Label(controls, text="ジャンル").grid(row=0, column=0, sticky="w")
        self.special_category = tk.StringVar(value="すべて")
        category_combo = ttk.Combobox(controls, textvariable=self.special_category,
                                      values=("すべて", *self.special_provider.categories()),
                                      state="readonly", width=20)
        category_combo.grid(row=0, column=1, sticky="w", padx=(5, 8))
        category_combo.bind("<<ComboboxSelected>>", self._special_category_changed)
        ttk.Label(controls, text="詳細").grid(row=0, column=2, sticky="w")
        self.special_subcategory = tk.StringVar(value="すべて")
        self.special_subcategory_combo = ttk.Combobox(controls, textvariable=self.special_subcategory,
                                                      values=("すべて",), state="readonly", width=18)
        self.special_subcategory_combo.grid(row=0, column=3, sticky="w", padx=(5, 8))
        self.special_subcategory_combo.bind("<<ComboboxSelected>>", lambda _event: self._refresh_special())
        self.special_query = tk.StringVar()
        query = ttk.Entry(controls, textvariable=self.special_query)
        query.grid(row=0, column=4, sticky="ew")
        query.bind("<Return>", lambda _event: self._refresh_special())
        ttk.Button(controls, text="絞り込み", command=self._refresh_special).grid(row=0, column=5, padx=(6, 0))
        ttk.Label(tab, text="Issue #56で監査済みのジャンル/詳細経路です。日本語を主表示し、Englishを併記します。").grid(row=1, column=0, sticky="w", pady=(5, 5))

        tree_frame = ttk.Frame(tab)
        tree_frame.grid(row=2, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        self.special_tree = ttk.Treeview(tree_frame, columns=("ja", "en", "path"), show="headings", selectmode="browse", height=14)
        self.special_tree.heading("ja", text="日本語")
        self.special_tree.heading("en", text="English")
        self.special_tree.heading("path", text="分類")
        self.special_tree.column("ja", width=170, anchor="w")
        self.special_tree.column("en", width=210, anchor="w")
        self.special_tree.column("path", width=210, anchor="w")
        self.special_tree.grid(row=0, column=0, sticky="nsew")
        special_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.special_tree.yview)
        special_scroll.grid(row=0, column=1, sticky="ns")
        self.special_tree.configure(yscrollcommand=special_scroll.set)
        self.special_tree.bind("<Double-1>", lambda _event: self._add_special_selected())
        ttk.Button(tab, text="選択をPromptへ追加", command=self._add_special_selected).grid(row=3, column=0, sticky="e", pady=(6, 0))
        self._refresh_special()

    def _build_general_tab(self, tabs: ttk.Notebook) -> None:
        tab = ttk.Frame(tabs, padding=16)
        tabs.add(tab, text="General browse")
        ttk.Label(tab, text="General browse", font=("TkDefaultFont", 12, "bold")).pack(anchor="w")
        ttk.Label(tab, text=self.general_provider.status_text, wraplength=500).pack(anchor="w", pady=(8, 0))
        ttk.Label(tab, text="#64の分類データはこの画面から編集・推測しません。accepted sidecar受領後にproviderだけ差し替えます。", wraplength=500).pack(anchor="w", pady=(8, 0))

    def _build_workspace(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        ttk.Label(parent, text="選択中のPrompt", font=("TkDefaultFont", 12, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 6))
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        self.workspace_tree = ttk.Treeview(tree_frame, columns=("ja", "en", "source"), show="headings", selectmode="browse", height=20)
        self.workspace_tree.heading("ja", text="日本語")
        self.workspace_tree.heading("en", text="English")
        self.workspace_tree.heading("source", text="由来")
        self.workspace_tree.column("ja", width=145, anchor="w")
        self.workspace_tree.column("en", width=220, anchor="w")
        self.workspace_tree.column("source", width=110, anchor="w")
        self.workspace_tree.grid(row=0, column=0, sticky="nsew")
        workspace_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.workspace_tree.yview)
        workspace_scroll.grid(row=0, column=1, sticky="ns")
        self.workspace_tree.configure(yscrollcommand=workspace_scroll.set)
        buttons = ttk.Frame(parent)
        buttons.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        ttk.Button(buttons, text="↑ 上へ", command=lambda: self._move_selected(-1)).pack(side="left")
        ttk.Button(buttons, text="↓ 下へ", command=lambda: self._move_selected(1)).pack(side="left", padx=(6, 0))
        ttk.Button(buttons, text="削除", command=self._remove_selected).pack(side="left", padx=(6, 0))
        ttk.Button(buttons, text="全クリア", command=self._clear_workspace).pack(side="right")
        self.workspace_status = ttk.Label(parent, text="")
        self.workspace_status.grid(row=3, column=0, sticky="w", pady=(5, 0))

    def _load_existing(self) -> None:
        self.workspace.load_existing_prompt(self.existing_text.get("1.0", "end-1c"))
        self._refresh_workspace()

    def _run_search(self) -> None:
        query = self.search_var.get().strip()
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        self._search_results.clear()
        if not query:
            self.search_status.configure(text="検索語を入力してください。")
            return
        response = self.search_service.search_one(query, limit=50)
        for index, result in enumerate(response.results):
            row_id = f"r{index}"
            self._search_results[row_id] = result
            self.search_tree.insert("", "end", iid=row_id, values=(result.japanese[0] if result.japanese else "", result.prompt_representation or "(canonical未確定)", result.match_type))
        if not response.results:
            text = "一致する候補がありません。"
        elif response.suppressed_loose_count:
            text = f"強い一致を優先表示中（弱いsubstring候補 {response.suppressed_loose_count}件を非表示）"
        else:
            text = f"{len(response.results)}件"
        if response.mixed_fallback_used:
            text += " / 日本語+Englishを同じ検索欄で照合"
        self.search_status.configure(text=text)

    def _add_search_selected(self) -> None:
        selected = self.search_tree.selection()
        if not selected:
            return
        try:
            self.workspace.add_search_result(self._search_results[selected[0]])
        except ValueError as exc:
            messagebox.showinfo("追加できません", str(exc), parent=self.root)
            return
        self._refresh_workspace()

    def _special_category_changed(self, _event=None) -> None:
        category = self.special_category.get()
        values = () if category == "すべて" else self.special_provider.subcategories(category)
        self.special_subcategory_combo.configure(values=("すべて", *values))
        self.special_subcategory.set("すべて")
        self._refresh_special()

    def _refresh_special(self) -> None:
        if not hasattr(self, "special_tree"):
            return
        for item in self.special_tree.get_children():
            self.special_tree.delete(item)
        self._special_rows.clear()
        category = self.special_category.get()
        category = "" if category == "すべて" else category
        subcategory = self.special_subcategory.get()
        subcategory = "" if subcategory == "すべて" else subcategory
        rows = self.special_provider.browse(category=category, subcategory=subcategory,
                                            query=self.special_query.get(), limit=500)
        for index, row in enumerate(rows):
            row_id = f"s{index}"
            self._special_rows[row_id] = row.item_id
            self.special_tree.insert("", "end", iid=row_id, values=(row.japanese, row.english, row.category))

    def _add_special_selected(self) -> None:
        selected = self.special_tree.selection()
        if not selected:
            return
        self.workspace.add_special(self._special_rows[selected[0]])
        self._refresh_workspace()

    def _refresh_workspace(self) -> None:
        for item in self.workspace_tree.get_children():
            self.workspace_tree.delete(item)
        unresolved = 0
        for item in self.workspace.items:
            if not item.resolved:
                unresolved += 1
            japanese = item.japanese or "—"
            if not item.resolved:
                japanese = "⚠ " + japanese
            self.workspace_tree.insert("", "end", iid=item.item_id, values=(japanese, item.english, item.source))
        self.workspace_status.configure(text=f"{len(self.workspace.items)}件" + (f" / ⚠ 未解決 {unresolved}件（原文保持）" if unresolved else ""))
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", self.workspace.preview)
        self.preview.configure(state="disabled")
        self.output_status.configure(text="表示中の項目だけを、この順番でコピーします。自動追加はありません。")

    def _selected_workspace_id(self) -> str | None:
        selected = self.workspace_tree.selection()
        return selected[0] if selected else None

    def _move_selected(self, delta: int) -> None:
        item_id = self._selected_workspace_id()
        if item_id is None:
            return
        if self.workspace.move(item_id, delta):
            self._refresh_workspace()
            self.workspace_tree.selection_set(item_id)
            self.workspace_tree.focus(item_id)

    def _remove_selected(self) -> None:
        item_id = self._selected_workspace_id()
        if item_id is None:
            return
        self.workspace.remove(item_id)
        self._refresh_workspace()

    def _clear_workspace(self) -> None:
        self.workspace.clear()
        self._refresh_workspace()

    def _copy_prompt(self) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(self.workspace.clipboard_text)
        self.output_status.configure(text="コピーしました。画面のEnglish Promptと同一です。")


def main() -> None:
    root = tk.Tk()
    V1App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
