from __future__ import annotations
import sys, tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core import Catalog, has_japanese
from reference_cooccurrence import ReferenceCooccurrence

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Danbooru Tag Explorer TRIAL v0.2")
        self.geometry("1220x840")
        self.minsize(1000, 700)
        self.catalog = Catalog(ROOT / "data" / "catalog_20260902.json.gz")
        self.cooc = ReferenceCooccurrence(ROOT / "data" / "reference_cooccurrence")
        self.selected = []
        self.loras = []
        self.search_after = None
        self.last_results = []
        self._build()
        self._refresh_status()
        self._refresh_prompt()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)

        head = ttk.Frame(self, padding=(12,10,12,4))
        head.grid(row=0, column=0, sticky="ew")
        head.columnconfigure(0, weight=1)
        ttk.Label(head, text="日本語・英語どちらでもタグを入力", font=("", 12, "bold")).grid(row=0,column=0,sticky="w")
        self.status = ttk.Label(head, text="")
        self.status.grid(row=0,column=1,sticky="e")

        inp = ttk.Frame(self, padding=(12,0,12,4))
        inp.grid(row=1,column=0,sticky="ew")
        inp.columnconfigure(0, weight=1)
        self.entry = ttk.Entry(inp, font=("", 12))
        self.entry.grid(row=0,column=0,sticky="ew")
        self.entry.bind("<KeyRelease>", self._on_key)
        self.entry.bind("<Return>", self._choose_first)
        self.entry.bind("<Tab>", self._choose_first)
        ttk.Button(inp, text="現在の入力を追加", command=self._add_current_tokens).grid(row=0,column=1,padx=(8,0))

        auto = ttk.LabelFrame(self, text="入力候補", padding=6)
        auto.grid(row=2,column=0,sticky="ew",padx=12)
        auto.columnconfigure(0, weight=1)
        self.auto = ttk.Treeview(auto, columns=("en","ja","count","cat","special"), show="headings", height=7)
        for c,t,w,a in [
            ("en","英語",300,"w"),("ja","日本語",260,"w"),("count","現在使用数",120,"e"),
            ("cat","カテゴリ",90,"center"),("special","特殊辞書",75,"center")]:
            self.auto.heading(c,text=t); self.auto.column(c,width=w,anchor=a)
        self.auto.grid(row=0,column=0,sticky="ew")
        sb=ttk.Scrollbar(auto,orient="vertical",command=self.auto.yview); sb.grid(row=0,column=1,sticky="ns"); self.auto.configure(yscrollcommand=sb.set)
        self.auto.bind("<Double-1>", self._choose_tree)
        self.auto.bind("<Return>", self._choose_tree)

        sel = ttk.LabelFrame(self, text="選択中タグ", padding=6)
        sel.grid(row=3,column=0,sticky="ew",padx=12,pady=(6,0))
        sel.columnconfigure(0,weight=1)
        self.sel = ttk.Treeview(sel, columns=("en","ja","count","special"), show="headings", height=4)
        for c,t,w,a in [("en","英語",340,"w"),("ja","日本語",300,"w"),("count","現在使用数",120,"e"),("special","特殊辞書",75,"center")]:
            self.sel.heading(c,text=t); self.sel.column(c,width=w,anchor=a)
        self.sel.grid(row=0,column=0,sticky="ew")
        btns=ttk.Frame(sel); btns.grid(row=0,column=1,sticky="ns",padx=(8,0))
        ttk.Button(btns,text="選択を削除",command=self._remove_selected).pack(fill="x")
        ttk.Button(btns,text="全解除",command=self._clear_selected).pack(fill="x",pady=(6,0))

        body = ttk.Panedwindow(self, orient="horizontal")
        body.grid(row=4,column=0,sticky="nsew",padx=12,pady=8)

        recbox=ttk.Frame(body); recbox.columnconfigure(0,weight=1); recbox.rowconfigure(1,weight=1)
        body.add(recbox, weight=3)
        topbar=ttk.Frame(recbox); topbar.grid(row=0,column=0,sticky="ew")
        ttk.Label(topbar,text="関連候補",font=("",11,"bold")).pack(side="left")
        self.rec_note=ttk.Label(topbar,text="",foreground="#555")
        self.rec_note.pack(side="left",padx=12)
        ttk.Button(topbar,text="更新",command=self._refresh_recommendations).pack(side="right")

        self.tabs=ttk.Notebook(recbox); self.tabs.grid(row=1,column=0,sticky="nsew",pady=(4,0))
        self.tab_special=ttk.Frame(self.tabs); self.tabs.add(self.tab_special,text="★ 特殊辞書")
        self.tab_cooc=ttk.Frame(self.tabs); self.tabs.add(self.tab_cooc,text="参考共起")
        self.tab_special.columnconfigure(0,weight=1); self.tab_special.rowconfigure(0,weight=1)
        self.tab_cooc.columnconfigure(0,weight=1); self.tab_cooc.rowconfigure(1,weight=1)

        self.special_tree=ttk.Treeview(self.tab_special,columns=("en","ja","count","layer","cat"),show="headings")
        for c,t,w,a in [("en","英語",250,"w"),("ja","日本語",230,"w"),("count","現在使用数",100,"e"),("layer","層",75,"center"),("cat","主カテゴリ",200,"w")]:
            self.special_tree.heading(c,text=t); self.special_tree.column(c,width=w,anchor=a)
        self.special_tree.grid(row=0,column=0,sticky="nsew")
        self.special_tree.bind("<Double-1>", lambda e:self._add_from_tree(self.special_tree))
        self.special_tree.bind("<Return>", lambda e:self._add_from_tree(self.special_tree))

        coocbar=ttk.Frame(self.tab_cooc,padding=4); coocbar.grid(row=0,column=0,sticky="ew")
        self.cooc_status=ttk.Label(coocbar,text="")
        self.cooc_status.pack(side="left")
        ttk.Button(coocbar,text="参考共起を読込",command=self._load_cooc).pack(side="right")
        self.cooc_tree=ttk.Treeview(self.tab_cooc,columns=("en","ja","rates","common","current","special"),show="headings")
        for c,t,w,a in [("en","英語",220,"w"),("ja","日本語",200,"w"),("rates","各入力タグとの一緒率",210,"w"),("common","共通相性",80,"e"),("current","現在使用数",100,"e"),("special","特殊",55,"center")]:
            self.cooc_tree.heading(c,text=t); self.cooc_tree.column(c,width=w,anchor=a)
        self.cooc_tree.grid(row=1,column=0,sticky="nsew")
        self.cooc_tree.bind("<Double-1>", lambda e:self._add_from_tree(self.cooc_tree))
        self.cooc_tree.bind("<Return>", lambda e:self._add_from_tree(self.cooc_tree))

        right=ttk.Frame(body); right.columnconfigure(0,weight=1)
        body.add(right, weight=2)

        lbox=ttk.LabelFrame(right,text="LoRA",padding=8); lbox.grid(row=0,column=0,sticky="ew")
        lbox.columnconfigure(1,weight=1)
        ttk.Label(lbox,text="名前").grid(row=0,column=0,sticky="w")
        self.lora_name=ttk.Entry(lbox); self.lora_name.grid(row=0,column=1,sticky="ew",padx=(6,0))
        ttk.Label(lbox,text="重み").grid(row=1,column=0,sticky="w",pady=(4,0))
        self.lora_weight=ttk.Entry(lbox,width=10); self.lora_weight.insert(0,"1.0"); self.lora_weight.grid(row=1,column=1,sticky="w",padx=(6,0),pady=(4,0))
        ttk.Label(lbox,text="Trigger").grid(row=2,column=0,sticky="w",pady=(4,0))
        self.lora_triggers=ttk.Entry(lbox); self.lora_triggers.grid(row=2,column=1,sticky="ew",padx=(6,0),pady=(4,0))
        ttk.Button(lbox,text="LoRAを追加",command=self._add_lora).grid(row=3,column=1,sticky="e",pady=(6,0))
        self.lora_list=tk.Listbox(lbox,height=5); self.lora_list.grid(row=4,column=0,columnspan=2,sticky="ew",pady=(6,0))
        ttk.Button(lbox,text="選択LoRAを削除",command=self._remove_lora).grid(row=5,column=1,sticky="e",pady=(4,0))

        pbox=ttk.LabelFrame(right,text="最終Prompt",padding=8); pbox.grid(row=1,column=0,sticky="nsew",pady=(8,0))
        right.rowconfigure(1,weight=1); pbox.columnconfigure(0,weight=1); pbox.rowconfigure(0,weight=1)
        self.prompt=tk.Text(pbox,height=10,wrap="word")
        self.prompt.grid(row=0,column=0,sticky="nsew")
        ttk.Button(pbox,text="コピー",command=self._copy_prompt).grid(row=1,column=0,sticky="e",pady=(6,0))

        note=ttk.Label(right,text="※ 参考共起は2026-05のペア統計。複数タグの正確なAND率ではありません。\n正確なAND共起は後でpost単位データへ差し替える設計です。",foreground="#555",justify="left")
        note.grid(row=2,column=0,sticky="ew",pady=(8,0))

    def _refresh_status(self):
        c=self.catalog.verified_special_counts
        self.status.config(text=f"Danbooru 2026-09: {len(self.catalog.tags):,} tags / 特殊辞書 {c['total']:,}語")
        self.cooc_status.config(text=f"状態: {self.cooc.status()}")

    def _current_token(self):
        text=self.entry.get()
        sep=max(text.rfind(","), text.rfind("\n"))
        return text[sep+1:].strip(), sep

    def _on_key(self,event=None):
        if event and event.keysym in ("Up","Down","Return","Tab","Escape"):
            return
        if self.search_after:
            self.after_cancel(self.search_after)
        self.search_after=self.after(160,self._run_search)

    def _run_search(self):
        token,_=self._current_token()
        self.last_results=self.catalog.search(token,40) if token else []
        for i in self.auto.get_children(): self.auto.delete(i)
        for r in self.last_results:
            self.auto.insert("", "end", iid=r["canonical"], values=(
                r["prompt"], r["japanese"] or "—", f"{r['post_count']:,}", r["category"], "★" if r["special"] else ""
            ))

    def _choose_first(self,event=None):
        kids=self.auto.get_children()
        if kids:
            self.auto.selection_set(kids[0]); self.auto.focus(kids[0]); self._choose_tree()
            return "break"
        self._add_current_tokens()
        return "break"

    def _choose_tree(self,event=None):
        sel=self.auto.selection()
        if not sel: return "break"
        can=sel[0]
        self._replace_current_token(can)
        self._add_canonical(can)
        return "break"

    def _replace_current_token(self,can):
        token,sep=self._current_token()
        t=self.catalog.tag(can)
        primary=self.catalog.japanese(can) if has_japanese(token) and self.catalog.japanese(can) else t["prompt"]
        text=self.entry.get()
        prefix=text[:sep+1]
        if sep>=0:
            new=prefix+" "+primary+", "
        else:
            new=primary+", "
        self.entry.delete(0,"end"); self.entry.insert(0,new); self.entry.icursor("end")
        for i in self.auto.get_children(): self.auto.delete(i)

    def _add_current_tokens(self):
        raw=[x.strip() for x in self.entry.get().replace("\n",",").split(",") if x.strip()]
        errors=[]
        for x in raw:
            r=self.catalog.resolve(x)
            if r.get("ok"): self._add_canonical(r["canonical"], refresh=False)
            else: errors.append(f"{x}: {r.get('error')}")
        self._refresh_selected(); self._refresh_prompt(); self._refresh_recommendations()
        if errors: messagebox.showwarning("解決できない入力","\n".join(errors[:12]))

    def _add_canonical(self,can,refresh=True):
        if can not in self.selected:
            self.selected.append(can)
        if refresh:
            self._refresh_selected(); self._refresh_prompt(); self._refresh_recommendations()

    def _add_from_tree(self,tree):
        sel=tree.selection()
        if sel: self._add_canonical(sel[0])

    def _refresh_selected(self):
        for i in self.sel.get_children(): self.sel.delete(i)
        for can in self.selected:
            t=self.catalog.tag(can)
            if not t: continue
            self.sel.insert("","end",iid=can,values=(t["prompt"],self.catalog.japanese(can) or "—",f"{int(t['post_count']):,}","★" if t.get("special") else ""))

    def _remove_selected(self):
        for can in list(self.sel.selection()):
            if can in self.selected: self.selected.remove(can)
        self._refresh_selected(); self._refresh_prompt(); self._refresh_recommendations()

    def _clear_selected(self):
        self.selected.clear()
        self._refresh_selected(); self._refresh_prompt(); self._refresh_recommendations()

    def _refresh_recommendations(self):
        for tr in (self.special_tree,self.cooc_tree):
            for i in tr.get_children(): tr.delete(i)
        rel=self.catalog.special_related(self.selected,80,True)
        for r in rel:
            self.special_tree.insert("","end",iid=r["canonical"],values=(r["prompt"],r["japanese"] or "—",f"{r['post_count']:,}",r["layer"],r["main"]))
        if self.selected and not rel:
            self.rec_note.config(text="特殊辞書上のカテゴリ関連候補なし")
        elif rel:
            self.rec_note.config(text="特殊辞書の分類が近い候補（共起統計ではありません）")
        else:
            self.rec_note.config(text="タグを選ぶと候補を表示")
        if self.cooc.loaded:
            self._populate_cooc()

    def _load_cooc(self):
        try:
            self.cooc.load()
            self._refresh_status()
            self._populate_cooc()
            self.tabs.select(self.tab_cooc)
        except FileNotFoundError:
            messagebox.showinfo("参考共起未導入","先に DOWNLOAD_REFERENCE_COOCCURRENCE.bat を実行してください。")
        except Exception as e:
            messagebox.showerror("共起データ読込エラー",str(e))

    def _populate_cooc(self):
        for i in self.cooc_tree.get_children(): self.cooc_tree.delete(i)
        if not self.selected: return
        try:
            rows,notes=self.cooc.recommend(self.selected,self.catalog,80,True)
        except Exception as e:
            self.cooc_status.config(text="共起エラー: "+str(e)); return
        for r in rows:
            rates=" / ".join(f"{x*100:.1f}%" for x in r["rates"])
            self.cooc_tree.insert("","end",iid=r["canonical"],values=(
                r["prompt"],r["japanese"] or "—",rates,f"{r['common_score']*100:.1f}",
                f"{r['current_count']:,}" if r["current_count"] is not None else "—","★" if r["special"] else ""
            ))
        text="参考共起 2026-05-18"
        if notes: text+=" / "+" / ".join(notes)
        self.cooc_status.config(text=text)

    def _add_lora(self):
        name=self.lora_name.get().strip()
        if not name: return
        w=self.lora_weight.get().strip() or "1.0"
        triggers=[x.strip() for x in self.lora_triggers.get().split(",") if x.strip()]
        self.loras.append({"name":name,"weight":w,"triggers":triggers})
        self.lora_list.insert("end",f"{name}  weight={w}  trigger={', '.join(triggers) if triggers else '—'}")
        self.lora_name.delete(0,"end"); self.lora_triggers.delete(0,"end")
        self._refresh_prompt()

    def _remove_lora(self):
        idxs=list(self.lora_list.curselection())
        for i in reversed(idxs):
            self.lora_list.delete(i); self.loras.pop(i)
        self._refresh_prompt()

    def _refresh_prompt(self):
        p=self.catalog.prompt_for(self.selected,self.loras)
        self.prompt.delete("1.0","end"); self.prompt.insert("1.0",p)

    def _copy_prompt(self):
        p=self.prompt.get("1.0","end-1c")
        self.clipboard_clear(); self.clipboard_append(p)
        self.update()
        self.status.config(text="Promptをコピーしました")

if __name__=="__main__":
    App().mainloop()
