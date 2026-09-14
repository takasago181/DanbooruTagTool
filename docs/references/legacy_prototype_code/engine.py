from __future__ import annotations

import csv
import math
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


def norm_input(s: str) -> str:
    s = unicodedata.normalize("NFKC", s.strip().lower())
    s = re.sub(r"\\([()])", r"\1", s)
    s = s.replace("_", " ")
    s = re.sub(r"\s+", " ", s)
    return s


def to_internal_tag(s: str) -> str:
    return norm_input(s).replace(" ", "_")


def to_prompt_tag(s: str) -> str:
    return s.replace("_", " ")


@dataclass
class ResolvedInput:
    original: str
    canonical: str
    source: str


@dataclass
class SearchResult:
    tag: str
    prompt_tag: str
    japanese: str
    category: str
    cooc_count: int
    current_count: int | None
    score: float
    geometric_mean: float
    weakest: float
    coverage: float
    per_query: list[float]


class CooccurrenceEngine:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)

        self.available_csv = self.data_dir / "available_tags.csv"
        self.matrix_npz = self.data_dir / "cooccurrence_all_normalized.npz"
        self.alias_csv = self.data_dir / "alias_index_20260902.csv"
        self.special_csv = self.data_dir / "special2788_20260902.csv"
        self.full_kb_csv = self.data_dir / "danbooru_full_tag_kb_20260902.csv"

        self.tags: list[str] = []
        self.counts: np.ndarray | None = None
        self.categories: list[str] = []
        self.tag_to_idx: dict[str, int] = {}
        self.matrix: np.ndarray | None = None

        self.alias_map: dict[str, tuple[str, list[str]]] = {}
        self.special_map: dict[str, list[dict]] = {}
        self.current_counts: dict[str, int] = {}
        self.japanese_by_canonical: dict[str, list[str]] = {}

    def load(self) -> dict:
        self._load_available_tags()
        self._load_local_kb()
        self._load_matrix()

        n = len(self.tags)
        assert self.matrix is not None
        return {
            "tag_count": n,
            "matrix_shape": tuple(int(x) for x in self.matrix.shape),
            "matrix_dtype": str(self.matrix.dtype),
            "matrix_ram_gib": float(self.matrix.nbytes / (1024 ** 3)),
        }

    def _load_available_tags(self):
        if not self.available_csv.exists():
            raise FileNotFoundError(f"Missing {self.available_csv}")
        rows: list[tuple[str, int, str]] = []
        with self.available_csv.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            required = {"tag", "count", "category", "available"}
            if not required.issubset(reader.fieldnames or []):
                raise RuntimeError("available_tags.csv schema mismatch")
            for row in reader:
                if row.get("available", "").lower() != "true":
                    continue
                rows.append((row["tag"], int(row["count"]), row["category"]))

        # The public reference implementation assigns indices after alphabetical sort.
        rows.sort(key=lambda x: x[0])
        self.tags = [x[0] for x in rows]
        self.counts = np.asarray([x[1] for x in rows], dtype=np.int64)
        self.categories = [x[2] for x in rows]
        self.tag_to_idx = {tag: i for i, tag in enumerate(self.tags)}

    def _load_local_kb(self):
        if self.alias_csv.exists():
            with self.alias_csv.open("r", encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f):
                    key = norm_input(row["NormalizedAlias"])
                    status = row["ResolutionStatus"]
                    targets = [x for x in row["CanonicalTargets"].split(";") if x]
                    if status == "CANONICAL_PRECEDENCE" and row["CanonicalPrecedenceTag"]:
                        self.alias_map[key] = ("canonical_precedence", [row["CanonicalPrecedenceTag"]])
                    elif status == "ALIAS_UNIQUE" and len(targets) == 1:
                        self.alias_map[key] = ("alias", targets)
                    elif targets:
                        self.alias_map[key] = ("ambiguous", targets)

        if self.full_kb_csv.exists():
            with self.full_kb_csv.open("r", encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f):
                    try:
                        self.current_counts[row["DanbooruTag"]] = int(row["post_count"])
                    except Exception:
                        pass

        if self.special_csv.exists():
            with self.special_csv.open("r", encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f):
                    key = norm_input(row["Tag"])
                    self.special_map.setdefault(key, []).append(row)
                    canonical = row.get("ChosenCanonicalTag", "")
                    ja = row.get("日本語", "")
                    if canonical and ja:
                        vals = self.japanese_by_canonical.setdefault(canonical, [])
                        if ja not in vals:
                            vals.append(ja)

    def _load_matrix(self):
        if not self.matrix_npz.exists():
            raise FileNotFoundError(f"Missing {self.matrix_npz}")
        archive = np.load(self.matrix_npz, allow_pickle=False)
        if "cooc_norm" not in archive.files:
            raise RuntimeError("cooccurrence_all_normalized.npz has no 'cooc_norm' array")
        matrix = archive["cooc_norm"]
        n = len(self.tags)
        if matrix.ndim != 2 or matrix.shape != (n, n):
            raise RuntimeError(
                f"Matrix/index mismatch: matrix={matrix.shape}, available tags={n}. "
                "The two public files must come from the same revision."
            )
        self.matrix = matrix

    def resolve_one(self, raw: str) -> ResolvedInput:
        original = raw.strip()
        if not original:
            raise ValueError("空のタグ")

        internal = to_internal_tag(original)
        if internal in self.tag_to_idx:
            return ResolvedInput(original, internal, "canonical")

        key = norm_input(original)

        alias_info = self.alias_map.get(key)
        if alias_info:
            kind, targets = alias_info
            usable = [t for t in targets if t in self.tag_to_idx]
            if len(usable) == 1:
                return ResolvedInput(original, usable[0], kind)
            if len(usable) > 1:
                raise ValueError(
                    f"{original!r} は複数のalias候補があります: {', '.join(usable[:8])}"
                )

        special_rows = self.special_map.get(key, [])
        special_targets = []
        for row in special_rows:
            target = row.get("ChosenCanonicalTag", "")
            if target and target in self.tag_to_idx and target not in special_targets:
                special_targets.append(target)
        if len(special_targets) == 1:
            return ResolvedInput(original, special_targets[0], "special2788")
        if len(special_targets) > 1:
            raise ValueError(
                f"{original!r} は特殊辞書から複数候補へつながります: {', '.join(special_targets)}"
            )

        raise ValueError(
            f"{original!r} は2026-05-18共起データにありません。"
            "新しいDanbooruタグ、Semantic語、または表記違いの可能性があります。"
        )

    def resolve_many(self, raw_tags: Iterable[str]) -> list[ResolvedInput]:
        out = []
        seen = set()
        for raw in raw_tags:
            if not raw.strip():
                continue
            r = self.resolve_one(raw)
            if r.canonical not in seen:
                seen.add(r.canonical)
                out.append(r)
        if not out:
            raise ValueError("検索タグがありません")
        return out

    def search(
        self,
        raw_tags: Iterable[str],
        *,
        category: str = "general",
        mode: str = "common",
        top_n: int = 100,
        ignore_generic: bool = True,
    ) -> tuple[list[ResolvedInput], list[SearchResult]]:
        if self.matrix is None or self.counts is None:
            raise RuntimeError("Engine not loaded")

        resolved = self.resolve_many(raw_tags)
        qidx = np.asarray([self.tag_to_idx[r.canonical] for r in resolved], dtype=np.int64)

        # Matrix rows are candidate tags. Values are row-normalized co-occurrence:
        # roughly P(query_tag | candidate_tag).
        probs = np.asarray(self.matrix[:, qidx], dtype=np.float32)
        if probs.ndim == 1:
            probs = probs[:, None]

        positive_all = np.all(probs > 0, axis=1)
        coverage = np.mean(probs > 0, axis=1).astype(np.float32)
        weakest = np.min(probs, axis=1)

        safe_probs = np.clip(probs, 1e-12, 1.0)
        geometric = np.exp(np.mean(np.log(safe_probs), axis=1)).astype(np.float32)
        geometric[~positive_all] = 0.0

        # Harmonic mean punishes a candidate that is strong for one query but weak for another.
        harmonic = np.zeros(len(self.tags), dtype=np.float32)
        if probs.shape[1] == 1:
            harmonic = probs[:, 0].copy()
        else:
            denom = np.sum(1.0 / safe_probs, axis=1)
            harmonic = (probs.shape[1] / denom).astype(np.float32)
            harmonic[~positive_all] = 0.0

        freq_weight = np.log1p(self.counts.astype(np.float64))
        max_fw = float(freq_weight.max()) if len(freq_weight) else 1.0
        freq_weight = (freq_weight / max_fw).astype(np.float32)

        if mode == "common":
            score = harmonic
        elif mode == "balanced":
            score = geometric
        elif mode == "weakest":
            score = weakest
        elif mode == "frequency":
            score = geometric * (0.25 + 0.75 * freq_weight)
        else:
            raise ValueError(f"Unknown mode: {mode}")

        # Candidate category.
        if category != "all":
            cat_mask = np.fromiter(
                (c == category for c in self.categories),
                dtype=bool,
                count=len(self.categories),
            )
            score = np.where(cat_mask, score, -1.0)

        # Do not recommend inputs themselves.
        score[qidx] = -1.0

        if ignore_generic:
            generic = {
                "1girl", "1boy", "2girls", "2boys", "multiple_girls", "multiple_boys",
                "solo", "solo_focus", "censored", "uncensored",
                "general", "sensitive", "questionable", "explicit",
            }
            for tag in generic:
                idx = self.tag_to_idx.get(tag)
                if idx is not None:
                    score[idx] = -1.0

        valid = np.flatnonzero(score > 0)
        if len(valid) == 0:
            return resolved, []

        top_n = max(1, min(int(top_n), len(valid)))
        if len(valid) > top_n:
            sel = valid[np.argpartition(score[valid], -top_n)[-top_n:]]
        else:
            sel = valid
        sel = sel[np.argsort(score[sel])[::-1]]

        results: list[SearchResult] = []
        for idx in sel:
            tag = self.tags[int(idx)]
            ja = " / ".join(self.japanese_by_canonical.get(tag, []))
            results.append(
                SearchResult(
                    tag=tag,
                    prompt_tag=to_prompt_tag(tag),
                    japanese=ja,
                    category=self.categories[int(idx)],
                    cooc_count=int(self.counts[int(idx)]),
                    current_count=self.current_counts.get(tag),
                    score=float(score[int(idx)]),
                    geometric_mean=float(geometric[int(idx)]),
                    weakest=float(weakest[int(idx)]),
                    coverage=float(coverage[int(idx)]),
                    per_query=[float(x) for x in probs[int(idx)].tolist()],
                )
            )
        return resolved, results
