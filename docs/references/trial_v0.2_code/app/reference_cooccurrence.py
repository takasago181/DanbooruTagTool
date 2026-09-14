from __future__ import annotations
import csv, math
from pathlib import Path

class ReferenceCooccurrence:
    """
    2026-05-18 public normalized matrix.
    Row q is interpreted as P(candidate | input=q), because each source row
    is normalized by the row tag's self/diagonal count.
    Multi-input results are pairwise summaries, NOT exact post-level AND statistics.
    """
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.available = self.data_dir / "available_tags.csv"
        self.matrix_path = self.data_dir / "cooccurrence_all_normalized.npz"
        self.loaded = False

    def status(self):
        if not self.available.exists() or not self.matrix_path.exists():
            return "未導入"
        return "ファイルあり（未読込）" if not self.loaded else "参考共起 2026-05-18 読込済み"

    def load(self):
        import numpy as np
        rows = []
        with self.available.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                if row.get("available","").lower() != "true":
                    continue
                rows.append((row["tag"], int(row["count"]), row["category"]))
        rows.sort(key=lambda x: x[0])
        self.tags = [x[0] for x in rows]
        self.counts = np.asarray([x[1] for x in rows], dtype=np.int64)
        self.categories = [x[2] for x in rows]
        self.tag_to_idx = {t:i for i,t in enumerate(self.tags)}
        arc = np.load(self.matrix_path, allow_pickle=False)
        if "cooc_norm" not in arc.files:
            raise RuntimeError("cooccurrence npz に cooc_norm がありません")
        self.matrix = arc["cooc_norm"]
        if self.matrix.shape != (len(self.tags), len(self.tags)):
            raise RuntimeError(f"行列とtag indexのshape不一致: {self.matrix.shape} / {len(self.tags)}")
        self.loaded = True

    def recommend(self, selected, catalog, top_n=80, general_only=True):
        if not self.loaded:
            self.load()
        import numpy as np
        usable = [x for x in selected if x in self.tag_to_idx]
        if not usable:
            return [], ["選択タグが2026-05参考共起データにありません"]
        qidx = np.asarray([self.tag_to_idx[x] for x in usable], dtype=np.int64)
        # Correct direction for UI meaning: input rows -> candidate columns.
        probs = np.asarray(self.matrix[qidx, :], dtype=np.float32)
        if probs.ndim == 1:
            probs = probs[None, :]

        safe = np.clip(probs, 1e-12, 1.0)
        if probs.shape[0] == 1:
            common = probs[0].copy()
        else:
            denom = np.sum(1.0 / safe, axis=0)
            common = (probs.shape[0] / denom).astype(np.float32)
            common[np.any(probs <= 0, axis=0)] = 0.0

        for q in usable:
            common[self.tag_to_idx[q]] = 0.0

        order = np.argpartition(common, -min(top_n*8, len(common)))[-min(top_n*8, len(common)):]
        order = order[np.argsort(common[order])[::-1]]

        out = []
        for idx in order:
            tag = self.tags[int(idx)]
            cat = self.categories[int(idx)]
            if general_only and cat not in ("0","general","General"):
                continue
            t = catalog.tag(tag)
            current = int(t.get("post_count") or 0) if t else None
            ja = catalog.japanese(tag) if t else ""
            rates = [float(x) for x in probs[:, int(idx)]]
            out.append({
                "canonical": tag,
                "prompt": (t.get("prompt") if t else tag.replace("_"," ")),
                "japanese": ja,
                "reference_count": int(self.counts[int(idx)]),
                "current_count": current,
                "category": cat,
                "special": bool(t and t.get("special")),
                "rates": rates,
                "common_score": float(common[int(idx)])
            })
            if len(out) >= top_n:
                break
        missing = [x for x in selected if x not in self.tag_to_idx]
        notes = []
        if missing:
            notes.append("2026-05参考共起に無い入力: " + ", ".join(missing))
        if len(usable) > 1:
            notes.append("複数タグはペア共起の共通評価であり、正確なAND画像率ではありません")
        return out, notes
