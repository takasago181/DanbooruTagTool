"""Stage 7A single-window Special-first Tkinter UI."""
from __future__ import annotations

from pathlib import Path
from queue import Empty, SimpleQueue
import tkinter as tk
from tkinter import ttk

from .knowledge import TagKnowledgeCore
from .search import TagSearchEngine
from .stage7a_presenter import SearchPresentation, SpecialSearchPresenter
from .stage9c_session import Stage9ComposerSession
from .stage7a_warnings import Stage7AWarningPresenter
from .stage7b_recommendations import RecommendationController, RecommendationResult
from .stage8a_semantics import DecoratedRecommendationCandidate, Stage8ASemantics
from .stage8b_support import (
    COMBINATION_LABELS_JA,
    SUPPORT_CLASS_LABELS_JA,
    SUPPORT_SLOT_LABELS_JA,
    SupportKnowledgeStore,
)
from .recommendations import RecommendationEngine
from .runtime_index import RuntimeIndex
from .canonical_overlay import CanonicalOverlay


def wire_vertical_scrollbar(listbox, scrollbar):
    """Connect both sides of the standard Tk listbox/scrollbar contract."""
    listbox.configure(yscrollcommand=scrollbar.set)
    scrollbar.configure(command=listbox.yview)


def set_general_results_visible(results_frame, general_box, visible):
    """Give the full result pane to Special when no General result exists."""
    if visible:
        results_frame.rowconfigure(0, weight=3)
        results_frame.rowconfigure(1, weight=2)
        general_box.grid()
    else:
        results_frame.rowconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=0)
        general_box.grid_remove()


class Stage7AApp(ttk.Frame):
    def __init__(self, master, *, root_path: Path | None = None):
        super().__init__(master, padding=18)
        self.root_path = root_path or Path(__file__).resolve().parents[1]
        self.knowledge = TagKnowledgeCore.load(self.root_path)
        self.profile_store = self.knowledge.load_generation_profile_store(self.root_path)
        self.presenter = SpecialSearchPresenter(
            self.knowledge, TagSearchEngine(self.knowledge), self.profile_store
        )
        self.warning_presenter = Stage7AWarningPresenter(self.knowledge, self.profile_store)
        self.stage8a_semantics = Stage8ASemantics.load(self.root_path)
        self.support_knowledge = SupportKnowledgeStore.load(
            self.root_path, self.knowledge, self.profile_store
        )
        self.semantic_support_candidates = ()
        self.session = Stage9ComposerSession(
            self.knowledge, self.warning_presenter, self.support_knowledge
        )
        self.search_after = None
        self.presentation = SearchPresentation((), ())
        self.special_rows = []
        self.general_rows = []
        self.recommendation_after = None
        self.recommendation_poll = None
        self.recommendation_queue = SimpleQueue()
        self.recommendation_controller = None
        self.active_recommendation_request = 0
        self.recommendation_result = RecommendationResult(0, (), None, status="empty")
        self.recommendation_canvases = []
        self._build()
        self.pack(fill="both", expand=True)
        self.search_entry.focus_set()
        self._init_recommendation_controller()
        self.recommendation_poll = self.after(50, self._poll_recommendation_queue)
        self.winfo_toplevel().bind("<Configure>", self._resize_recommendation_view, add="+")

    def _init_recommendation_controller(self):
        """Open the existing read-only Stage 5 index without changing it."""
        try:
            index_dir = self.root_path / "data/runtime_index"
            index = RuntimeIndex(index_dir)
            self.statistics_snapshot_id = index.snapshot_id
            overlay = CanonicalOverlay(index, index_dir / "canonical_overlay.json")
            self.recommendation_controller = RecommendationController(
                RecommendationEngine(overlay, self.knowledge)
            )
        except Exception:
            # A missing/incompatible optional statistics index must not prevent
            # the Stage 7A search, Prompt, or copy path from starting.
            self.recommendation_controller = RecommendationController(None)

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        search_box = ttk.Frame(self)
        search_box.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_box.columnconfigure(0, weight=1)
        ttk.Label(search_box, text="Specialを探す", font=("Yu Gothic UI", 15, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_box, textvariable=self.search_var, font=("Yu Gothic UI", 12))
        self.search_entry.grid(row=1, column=0, sticky="ew", pady=(6, 0), ipady=6)
        self.search_entry.insert(0, "")
        self.search_entry.bind("<KeyRelease>", self._on_search_key)
        self.search_entry.bind("<Down>", self._focus_first_result)
        self.search_entry.bind("<Up>", self._focus_last_result)
        self.search_entry.bind("<Return>", self._choose_focused)
        self.search_entry.bind("<Tab>", self._choose_focused)
        self.search_entry.bind("<Escape>", self._close_results)
        ttk.Label(search_box, text="日本語・英語で検索　例: 拘束 / 機械 / 断面",
                  foreground="#60646c").grid(row=2, column=0, sticky="w", pady=(4, 0))

        content = ttk.Panedwindow(self, orient="horizontal")
        content.grid(row=1, column=0, sticky="nsew")

        self.results_frame = ttk.Frame(content, padding=(0, 0, 12, 0))
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.rowconfigure(0, weight=1)
        self.results_frame.rowconfigure(1, weight=0)
        content.add(self.results_frame, weight=3)

        special_box = ttk.LabelFrame(self.results_frame, text="Special Core Dictionary", padding=8)
        special_box.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        special_box.columnconfigure(0, weight=1)
        special_box.rowconfigure(0, weight=1)
        self.special_list = tk.Listbox(special_box, height=1, activestyle="none", exportselection=False,
                                       font=("Yu Gothic UI", 11), selectmode="browse")
        self.special_list.grid(row=0, column=0, sticky="nsew")
        self.special_scrollbar = ttk.Scrollbar(special_box, orient="vertical")
        self.special_scrollbar.grid(row=0, column=1, sticky="ns")
        wire_vertical_scrollbar(self.special_list, self.special_scrollbar)
        self.special_list.bind("<ButtonRelease-1>", self._add_clicked_special)
        self.special_list.bind("<Return>", self._choose_focused)
        self.special_list.bind("<Tab>", self._choose_focused)
        self.special_list.bind("<Escape>", self._close_results)

        self.general_box = ttk.LabelFrame(self.results_frame, text="その他のDanbooruタグ", padding=8)
        self.general_box.grid(row=1, column=0, sticky="nsew")
        self.general_box.columnconfigure(0, weight=1)
        self.general_box.rowconfigure(0, weight=1)
        self.general_list = tk.Listbox(self.general_box, height=1, activestyle="none", exportselection=False,
                                       font=("Yu Gothic UI", 10), selectmode="browse")
        self.general_list.grid(row=0, column=0, sticky="nsew")
        self.general_scrollbar = ttk.Scrollbar(self.general_box, orient="vertical")
        self.general_scrollbar.grid(row=0, column=1, sticky="ns")
        wire_vertical_scrollbar(self.general_list, self.general_scrollbar)
        self.general_list.bind("<ButtonRelease-1>", self._add_clicked_general)
        self.general_list.bind("<Return>", self._choose_focused)
        self.general_list.bind("<Tab>", self._choose_focused)
        self.general_list.bind("<Escape>", self._close_results)
        set_general_results_visible(self.results_frame, self.general_box, False)

        selected = ttk.Frame(content)
        selected.columnconfigure(0, weight=1)
        content.add(selected, weight=4)

        ttk.Label(selected, text="選んだSpecial", font=("Yu Gothic UI", 13, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        self.selected_special_frame = ttk.Frame(selected)
        self.selected_special_frame.grid(row=1, column=0, sticky="ew", pady=(2, 2))
        self.selected_special_frame.columnconfigure(0, weight=1)

        ttk.Label(selected, text="補助タグ", font=("Yu Gothic UI", 11, "bold")).grid(
            row=2, column=0, sticky="w"
        )
        self.auxiliary_frame = ttk.Frame(selected)
        self.auxiliary_frame.grid(row=3, column=0, sticky="ew", pady=(2, 2))
        self.auxiliary_frame.columnconfigure(0, weight=1)

        self.warning_box = ttk.LabelFrame(selected, text="必要な時だけ確認", padding=8)
        self.warning_box.columnconfigure(0, weight=1)

        self.recommendation_box = ttk.LabelFrame(selected, text="関連候補", padding=5)
        self.recommendation_box.grid(row=5, column=0, sticky="ew", pady=(4, 0))
        self.recommendation_box.columnconfigure(0, weight=1)
        self.recommendation_status = ttk.Label(self.recommendation_box, text="")
        self.recommendation_status.grid(row=0, column=0, sticky="w")
        self.recommendation_notebook = ttk.Notebook(self.recommendation_box)
        self.recommendation_notebook.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        self.common_recommendation_tab, self.common_recommendations = self._build_recommendation_scroller(
            self.recommendation_notebook
        )
        self.rare_recommendation_tab, self.rare_recommendations = self._build_recommendation_scroller(
            self.recommendation_notebook
        )
        self.semantic_support_tab, self.semantic_support_frame = self._build_recommendation_scroller(
            self.recommendation_notebook
        )
        self.recommendation_notebook.add(self.common_recommendation_tab, text="よく使われる")
        self.recommendation_notebook.add(self.rare_recommendation_tab, text="珍しい関連")
        self.recommendation_notebook.add(self.semantic_support_tab, text="意味から補助")
        self.recommendation_box.grid_remove()

        self.prompt_bar = ttk.LabelFrame(self, text="Prompt preview", padding=8)
        self.prompt_bar.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        self.prompt_bar.columnconfigure(0, weight=1)
        self.prompt_text = tk.Text(self.prompt_bar, height=3, wrap="word", font=("Consolas", 10),
                                   state="disabled")
        self.prompt_text.grid(row=0, column=0, sticky="ew")
        self.copy_button = ttk.Button(self.prompt_bar, text="Promptをコピー", command=self._copy_prompt)
        self.copy_button.grid(row=0, column=1, sticky="e", padx=(8, 0))
        self.copy_feedback = ttk.Label(self.prompt_bar, text="")
        self.copy_feedback.grid(row=1, column=1, sticky="e", pady=(4, 0))

        self._refresh_state()

    def _build_recommendation_scroller(self, notebook):
        tab = ttk.Frame(notebook)
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)
        canvas = tk.Canvas(tab, height=68, highlightthickness=0)
        self.recommendation_canvases.append(canvas)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)
        rows = ttk.Frame(canvas)
        rows.columnconfigure(0, weight=1)
        window = canvas.create_window((0, 0), window=rows, anchor="nw")
        rows.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window, width=event.width))
        return tab, rows

    def _resize_recommendation_view(self, event=None):
        root = self.winfo_toplevel()
        if event is not None and event.widget is not root:
            return
        height = 270 if root.winfo_height() >= 700 else 68
        for canvas in self.recommendation_canvases:
            canvas.configure(height=height)

    def _on_search_key(self, event=None):
        if event and event.keysym in {"Up", "Down", "Return", "Tab", "Escape"}:
            return
        if self.search_after is not None:
            self.after_cancel(self.search_after)
        self.search_after = self.after(240, self._run_search)

    def _run_search(self):
        self.search_after = None
        query = self.search_var.get().strip()
        self.presentation = self.presenter.search(query, limit=50) if query else SearchPresentation((), ())
        self.special_rows = list(self.presentation.special)
        self.general_rows = list(self.presentation.general)
        self.special_list.delete(0, "end")
        self.general_list.delete(0, "end")
        for item in self.special_rows:
            self.special_list.insert("end", f"{item.japanese or item.original_term}　/　{item.original_term}")
        for item in self.general_rows:
            label = item.display_japanese or item.prompt_text
            self.general_list.insert("end", f"{label}　/　{item.canonical}")
        set_general_results_visible(self.results_frame, self.general_box, bool(self.general_rows))

    def _focus_first_result(self, event=None):
        target = self.special_list if self.special_rows else self.general_list
        if target.size():
            target.selection_clear(0, "end")
            target.selection_set(0)
            target.activate(0)
            target.focus_set()
        return "break"

    def _focus_last_result(self, event=None):
        target = self.general_list if self.general_rows else self.special_list
        if target.size():
            index = target.size() - 1
            target.selection_clear(0, "end")
            target.selection_set(index)
            target.activate(index)
            target.focus_set()
        return "break"

    def _choose_focused(self, event=None):
        if self.special_list.curselection():
            self._add_special_index(self.special_list.curselection()[0])
        elif self.general_list.curselection():
            self._add_general_index(self.general_list.curselection()[0])
        elif self.special_rows:
            self._add_special_index(0)
        elif self.general_rows:
            self._add_general_index(0)
        return "break"

    def _add_clicked_special(self, event=None):
        if self.special_list.curselection():
            self._add_special_index(self.special_list.curselection()[0])

    def _add_clicked_general(self, event=None):
        if self.general_list.curselection():
            self._add_general_index(self.general_list.curselection()[0])

    def _add_special_index(self, index):
        changed = self.session.add_special(self.special_rows[index].special_id)
        self._refresh_state()
        if changed:
            self._schedule_recommendations()

    def _add_general_index(self, index):
        self.session.add_auxiliary(self.general_rows[index].canonical)
        self._refresh_state()

    def _schedule_recommendations(self):
        self.active_recommendation_request = -1
        if self.recommendation_after is not None:
            self.after_cancel(self.recommendation_after)
            self.recommendation_after = None
        if self.recommendation_controller is None:
            return
        self.recommendation_box.grid(row=5, column=0, sticky="ew", pady=(4, 0))
        self.recommendation_status.config(text="関連候補を調べています…")
        self.recommendation_after = self.after(350, self._request_recommendations)

    def _request_recommendations(self):
        self.recommendation_after = None
        core = self.session.statistics_core_canonicals()
        if core is None:
            request_id = self.recommendation_controller.invalidate()
            self.active_recommendation_request = request_id
            self._show_recommendation_result(RecommendationResult(
                request_id, (), None,
                status="unavailable",
                message="このSpecial組み合わせでは関連候補を計算できません。Promptにはそのまま使用できます。",
            ))
            return
        self.active_recommendation_request = self.recommendation_controller.request(
            core, self._on_recommendation_result
        )

    def _on_recommendation_result(self, result):
        # Background workers never call Tk. The UI thread drains this queue.
        self.recommendation_queue.put(result)

    def _poll_recommendation_queue(self):
        self.recommendation_poll = None
        try:
            while True:
                result = self.recommendation_queue.get_nowait()
                if result.request_id == self.active_recommendation_request:
                    self._show_recommendation_result(result)
        except Empty:
            pass
        self.recommendation_poll = self.after(50, self._poll_recommendation_queue)

    def _clear_recommendation_rows(self, frame):
        for child in frame.winfo_children():
            child.destroy()

    def _candidate_headline(self, decorated: DecoratedRecommendationCandidate):
        candidate = decorated.candidate
        display = self.knowledge.japanese_overlay.display_by_canonical.get(candidate.canonical)
        display = display or candidate.canonical.replace("_", " ")
        badge = f"[{decorated.semantic_label_ja}] " if decorated.semantic_label_ja else ""
        return f"{badge}{display} / {candidate.canonical}"

    def _candidate_statistics(self, decorated: DecoratedRecommendationCandidate, bucket):
        candidate = decorated.candidate
        rate = f"{candidate.conditional_rate * 100:.1f}%"
        text = f"{candidate.co_count} / {candidate.base_count}枚 ・ {rate}"
        if bucket == "rare":
            text += f" ・ Lift {candidate.raw_lift:.2f}"
        if candidate.co_count <= 2:
            text += "  （根拠がかなり少ない候補です）"
        return text

    def _render_candidate_rows(self, frame, candidates, *, bucket):
        self._clear_recommendation_rows(frame)
        decorated_rows = self.stage8a_semantics.decorate_many(
            candidates,
            core_canonicals=self.recommendation_result.core_canonicals,
            bucket=bucket,
        )
        grid_row = 0
        for decorated in decorated_rows:
            candidate = decorated.candidate
            first_row = grid_row
            frame.rowconfigure(first_row, weight=0)
            ttk.Label(frame, text=self._candidate_headline(decorated),
                      wraplength=520, justify="left").grid(
                          row=first_row, column=0, sticky="w", pady=(4, 0)
                      )
            ttk.Label(frame, text=self._candidate_statistics(decorated, bucket),
                      wraplength=520, justify="left", foreground="#50545c").grid(
                          row=first_row + 1, column=0, sticky="w"
                      )
            next_row = first_row + 2
            if decorated.generation_hint_ja:
                ttk.Label(frame, text=decorated.generation_hint_ja,
                          wraplength=520, justify="left", foreground="#3f536b").grid(
                              row=next_row, column=0, sticky="w", pady=(0, 4)
                          )
                next_row += 1
            for note in decorated.evidence_notes_ja:
                ttk.Label(frame, text=f"補足: {note}",
                          wraplength=520, justify="left", foreground="#6b5b45").grid(
                              row=next_row, column=0, sticky="w", pady=(0, 4)
                          )
                next_row += 1
            added = candidate.canonical in self.session.manual_auxiliary_canonicals
            ttk.Button(frame, text="追加済み" if added else "＋追加",
                       state="disabled" if added else "normal",
                       command=(None if added else lambda tag=candidate.canonical: self._add_recommended(tag))
                       ).grid(row=first_row, column=1, rowspan=next_row - first_row, sticky="e",
                              padx=(6, 0), pady=4)
            grid_row = next_row

    def _add_recommended(self, canonical):
        if self.session.add_auxiliary(canonical):
            if self.session.has_cooccurrence(canonical):
                self.session.include_cooccurrence(canonical)
            self._refresh_state()
            self._show_recommendation_result(self.recommendation_result)

    def _render_semantic_support(self):
        frame = self.semantic_support_frame
        self._clear_recommendation_rows(frame)
        ttk.Label(
            frame,
            text="投稿統計ではなく、選択したSpecialの意味と生成構造から補助候補を表示しています。",
            wraplength=520,
            justify="left",
            foreground="#50545c",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(4, 6))
        if not self.semantic_support_candidates:
            ttk.Label(
                frame,
                text="登録済みの意味補助候補はありません。",
                foreground="#60646c",
            ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 6))
            return
        grid_row = 1
        for candidate in self.semantic_support_candidates:
            display = self.knowledge.japanese_overlay.display_by_canonical.get(candidate.canonical)
            display = display or candidate.canonical.replace("_", " ")
            ttk.Label(
                frame,
                text=f"{display} / {candidate.canonical}",
                wraplength=520,
                justify="left",
            ).grid(row=grid_row, column=0, sticky="w", pady=(4, 0))
            next_row = grid_row + 1
            for relation in candidate.relations:
                owner = self.knowledge.special[relation.owner_special_id].term
                slot = SUPPORT_SLOT_LABELS_JA[relation.support_slot]
                support_class = SUPPORT_CLASS_LABELS_JA[relation.support_class]
                ttk.Label(
                    frame,
                    text=f"[{owner}] [{slot}] [{support_class}]",
                    wraplength=520,
                    justify="left",
                    foreground="#50545c",
                ).grid(row=next_row, column=0, sticky="w")
                next_row += 1
                ttk.Label(
                    frame, text=relation.reason_ja, wraplength=520, justify="left",
                    foreground="#3f536b",
                ).grid(row=next_row, column=0, sticky="w")
                next_row += 1
                if relation.combination_mode:
                    ttk.Label(
                        frame,
                        text=COMBINATION_LABELS_JA[relation.combination_mode],
                        foreground="#6b5b45",
                    ).grid(row=next_row, column=0, sticky="w", pady=(0, 4))
                    next_row += 1
            added = candidate.canonical in self.session.manual_auxiliary_canonicals
            ttk.Button(
                frame,
                text="追加済み" if added else "＋追加",
                state="disabled" if added else "normal",
                command=(
                    None if added
                    else lambda tag=candidate.canonical: self._add_recommended(tag)
                ),
            ).grid(
                row=grid_row, column=1, rowspan=max(1, next_row - grid_row),
                sticky="e", padx=(6, 0), pady=4,
            )
            grid_row = next_row

    def _refresh_semantic_support(self):
        self.semantic_support_candidates = self.support_knowledge.candidates(
            self.session.selected_special_ids
        )
        self._render_semantic_support()
        if self.session.selected_special_ids:
            self.recommendation_box.grid(row=5, column=0, sticky="ew", pady=(4, 0))

    def _show_recommendation_result(self, result):
        if result.request_id != self.active_recommendation_request:
            return
        if result.status == "ready" and set(result.core_canonicals) != set(
                self.session.statistics_core_canonicals() or ()):
            return
        if result.status not in {"ready", "empty", "unavailable", "error"}:
            return
        try:
            self.session.set_candidate_buckets(
                self.stage8a_semantics.decorate_many(
                    result.common, core_canonicals=result.core_canonicals, bucket="common"
                ) if result.status == "ready" else (),
                self.stage8a_semantics.decorate_many(
                    result.rare, core_canonicals=result.core_canonicals, bucket="rare"
                ) if result.status == "ready" else (),
                snapshot_id=getattr(self, "statistics_snapshot_id", None),
            )
        except (KeyError, ValueError):
            # Reject invalid payloads without replacing the last valid UI state.
            return
        self.recommendation_result = result
        self._refresh_state()
        if not self.session.selected_special_ids:
            self.recommendation_box.grid_remove()
            return
        self.recommendation_box.grid(row=5, column=0, sticky="ew", pady=(4, 0))
        if result.status == "ready":
            self.recommendation_status.config(
                text=f"このSpecial組み合わせが確認できる投稿: {result.base_count}件"
            )
            self._render_candidate_rows(
                self.common_recommendations, result.common, bucket="common"
            )
            self._render_candidate_rows(
                self.rare_recommendations, result.rare, bucket="rare"
            )
            if not result.common and not result.rare:
                self.recommendation_status.config(
                    text=f"このSpecial組み合わせが確認できる投稿: {result.base_count}件　関連候補は見つかりませんでした。"
                )
        else:
            self.recommendation_status.config(text=result.message)
            self._clear_recommendation_rows(self.common_recommendations)
            self._clear_recommendation_rows(self.rare_recommendations)

    def _close_results(self, event=None):
        self.presentation = SearchPresentation((), ())
        self.special_rows = []
        self.general_rows = []
        self.special_list.delete(0, "end")
        self.general_list.delete(0, "end")
        set_general_results_visible(self.results_frame, self.general_box, False)
        return "break"

    def _refresh_state(self):
        for child in self.selected_special_frame.winfo_children():
            child.destroy()
        for row, special_id in enumerate(self.session.selected_special_ids):
            special = self.knowledge.special[special_id]
            chip = ttk.Frame(self.selected_special_frame, padding=(3, 0))
            chip.grid(row=row, column=0, sticky="ew")
            chip.columnconfigure(0, weight=1)
            ttk.Label(chip, text=f"{special.japanese} / {special.term}", justify="left").grid(
                row=0, column=0, sticky="w"
            )
            ttk.Button(chip, text="×", width=3,
                       command=lambda sid=special_id: self._remove_special(sid)).grid(
                row=0, column=1, sticky="e"
            )

        for child in self.auxiliary_frame.winfo_children():
            child.destroy()
        for row, canonical in enumerate(self.session.manual_auxiliary_canonicals):
            display = self.knowledge.japanese_overlay.display_by_canonical.get(canonical)
            chip = ttk.Frame(self.auxiliary_frame, padding=(4, 1))
            chip.grid(row=row, column=0, sticky="ew")
            chip.columnconfigure(0, weight=1)
            ttk.Label(chip, text=display or canonical.replace("_", " ")).grid(row=0, column=0, sticky="w")
            ttk.Button(chip, text="×", width=3,
                       command=lambda tag=canonical: self._remove_auxiliary(tag)).grid(
                row=0, column=1, sticky="e"
            )

        self._refresh_semantic_support()

        for child in self.warning_box.winfo_children():
            child.destroy()
        notices = self.session.warnings
        if notices:
            self.warning_box.grid(row=4, column=0, sticky="nsew", pady=(0, 8))
            for row, notice in enumerate(notices):
                prefix = "注意" if notice.severity == "warning" else "情報"
                ttk.Label(self.warning_box, text=f"{prefix}: {notice.message}", wraplength=520,
                          justify="left").grid(row=row, column=0, sticky="w", pady=2)
        else:
            self.warning_box.grid_remove()

        preview = self.session.prompt_preview
        self.prompt_text.config(state="normal")
        self.prompt_text.delete("1.0", "end")
        self.prompt_text.insert("1.0", preview)
        self.prompt_text.config(state="disabled")

    def _remove_special(self, special_id):
        self.session.remove_special(special_id)
        self._refresh_state()
        if self.session.selected_special_ids:
            self._schedule_recommendations()
        else:
            self.active_recommendation_request = -1
            self.recommendation_box.grid_remove()

    def _remove_auxiliary(self, canonical):
        self.session.remove_auxiliary(canonical)
        self._refresh_state()
        if self.recommendation_result.status == "ready":
            self._show_recommendation_result(self.recommendation_result)

    def _copy_prompt(self):
        text = self.session.clipboard_text
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update_idletasks()
        self.copy_feedback.config(text="コピーしました")
        self.after(1500, lambda: self.copy_feedback.config(text=""))

    def close(self):
        if self.recommendation_after is not None:
            self.after_cancel(self.recommendation_after)
            self.recommendation_after = None
        if self.recommendation_poll is not None:
            self.after_cancel(self.recommendation_poll)
            self.recommendation_poll = None
        if self.recommendation_controller is not None:
            self.recommendation_controller.close()


def create_window(root_path: Path | None = None):
    root = tk.Tk()
    root.title("DanbooruTagTool — Special-first")
    root.geometry("1120x760")
    root.minsize(900, 540)
    app = Stage7AApp(root, root_path=root_path)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.close(), root.destroy()))
    return root


def main():
    create_window().mainloop()


if __name__ == "__main__":
    main()
