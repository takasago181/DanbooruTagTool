"""Stage 5 packed, read-only runtime index for true post-level co-occurrence.

The on-disk format is deliberately small and boring: contiguous native-endian
integer arrays plus JSON metadata.  Runtime access uses read-only NumPy mmap;
no Python post/tag graph is expanded in memory.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
import hashlib
from pathlib import Path
from typing import Iterable

import numpy as np


INDEX_FORMAT_VERSION = "stage5-packed-csr-v1"
_REQUIRED_FILES = {
    "post_ids.u32", "post_tag_offsets.u64", "post_tag_ids.u32",
    "tag_post_offsets.u64", "tag_post_ordinals.u32",
    "runtime_global_counts.u32", "tags.json", "index_metadata.json",
    "BUILD_MANIFEST.json",
}


class RuntimeIndexError(ValueError):
    """The requested index is missing, corrupt, or incompatible."""


@dataclass(frozen=True, slots=True)
class AndResult:
    post_ordinals: np.ndarray
    post_ids: np.ndarray

    @property
    def base_count(self) -> int:
        return int(self.post_ordinals.size)


class RuntimeIndex:
    """Read-only bidirectional General-tag index.

    ``intersect`` is a true N-way intersection of sorted posting lists.
    ``aggregate`` walks only the matched posts' reverse tag lists.
    """

    def __init__(self, directory: str | Path, *, expected_snapshot_id: str | None = None,
                 verify_hashes: bool = False):
        self.directory = Path(directory)
        missing = sorted(name for name in _REQUIRED_FILES if not (self.directory / name).is_file())
        if missing:
            raise RuntimeIndexError(f"Incomplete runtime index: missing {', '.join(missing)}")
        self.metadata = self._read_json("index_metadata.json")
        self.manifest = self._read_json("BUILD_MANIFEST.json")
        self._full_validation = verify_hashes
        self._validate_metadata(expected_snapshot_id)
        if verify_hashes:
            self._validate_hashes()
        self.tags: tuple[str, ...] = tuple(self._read_json("tags.json"))
        self.tag_to_id = {tag: tag_id for tag_id, tag in enumerate(self.tags)}
        self.post_ids = self._map("post_ids.u32", np.uint32)
        self.post_tag_offsets = self._map("post_tag_offsets.u64", np.uint64)
        self.post_tag_ids = self._map("post_tag_ids.u32", np.uint32)
        self.tag_post_offsets = self._map("tag_post_offsets.u64", np.uint64)
        self.tag_post_ordinals = self._map("tag_post_ordinals.u32", np.uint32)
        self.runtime_global_counts = self._map("runtime_global_counts.u32", np.uint32)
        self._validate_arrays()

    def _read_json(self, name: str):
        try:
            return json.loads((self.directory / name).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeIndexError(f"Invalid {name}") from exc

    def _map(self, name: str, dtype: np.dtype) -> np.memmap:
        size = (self.directory / name).stat().st_size
        if size % np.dtype(dtype).itemsize:
            raise RuntimeIndexError(f"Corrupt array byte length: {name}")
        return np.memmap(self.directory / name, dtype=dtype, mode="r")

    def _validate_metadata(self, expected_snapshot_id: str | None) -> None:
        snapshot = self.metadata.get("statistics_dataset_snapshot_id")
        if self.metadata.get("index_format_version") != INDEX_FORMAT_VERSION or not snapshot:
            raise RuntimeIndexError("Invalid index metadata")
        if self.manifest.get("statistics_dataset_snapshot_id") != snapshot:
            raise RuntimeIndexError("Snapshot mismatch between index and manifest")
        if expected_snapshot_id is not None and snapshot != expected_snapshot_id:
            raise RuntimeIndexError("Requested statistics snapshot does not match index")

    def _validate_hashes(self) -> None:
        hashes = self.manifest.get("index_file_sha256")
        if not isinstance(hashes, dict):
            raise RuntimeIndexError("Manifest has no index file hashes")
        for name, expected in hashes.items():
            hasher = hashlib.sha256()
            with (self.directory / name).open("rb") as source:
                for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
                    hasher.update(chunk)
            if hasher.hexdigest() != expected:
                raise RuntimeIndexError(f"Index file SHA-256 mismatch: {name}")

    def _validate_arrays(self) -> None:
        post_count, tag_count = len(self.post_ids), len(self.tags)
        if (len(self.post_tag_offsets) != post_count + 1
                or len(self.tag_post_offsets) != tag_count + 1
                or len(self.runtime_global_counts) != tag_count):
            raise RuntimeIndexError("Index array dimensions do not match metadata")
        if (self.post_tag_offsets[0] != 0 or self.tag_post_offsets[0] != 0
                or self.post_tag_offsets[-1] != len(self.post_tag_ids)
                or self.tag_post_offsets[-1] != len(self.tag_post_ordinals)):
            raise RuntimeIndexError("Index offset terminal values are invalid")
        # Full scans would fault ~3 GB of mmap pages at every normal startup.
        # Build/repair verification requests ``verify_hashes=True`` and performs
        # these stronger structural checks deliberately.
        if self._full_validation:
            if (np.any(self.post_tag_offsets[1:] < self.post_tag_offsets[:-1])
                    or np.any(self.tag_post_offsets[1:] < self.tag_post_offsets[:-1])):
                raise RuntimeIndexError("Index offsets are not monotonic")
            if (len(self.post_tag_ids) and int(self.post_tag_ids.max()) >= tag_count) or (
                    len(self.tag_post_ordinals) and int(self.tag_post_ordinals.max()) >= post_count):
                raise RuntimeIndexError("Index IDs are outside their declared bounds")

    @property
    def snapshot_id(self) -> str:
        return self.metadata["statistics_dataset_snapshot_id"]

    @property
    def total_posts(self) -> int:
        return int(len(self.post_ids))

    def tag_id(self, canonical: str) -> int:
        try:
            return self.tag_to_id[canonical]
        except KeyError as exc:
            raise KeyError(f"Unknown runtime General tag: {canonical}") from exc

    def postings(self, canonical: str) -> np.ndarray:
        tag_id = self.tag_id(canonical)
        start, end = self.tag_post_offsets[tag_id:tag_id + 2]
        return self.tag_post_ordinals[int(start):int(end)]

    def intersect(self, canonicals: Iterable[str]) -> AndResult:
        names = tuple(dict.fromkeys(canonicals))
        if not names:
            raise ValueError("At least one canonical tag is required")
        postings = sorted((self.postings(name) for name in names), key=len)
        result = np.asarray(postings[0], dtype=np.uint32)
        for posting in postings[1:]:
            result = np.intersect1d(result, posting, assume_unique=True)
            if not len(result):
                break
        return AndResult(result, self.post_ids[result])

    def aggregate(self, base_posts: Iterable[int] | AndResult, *, exclude: Iterable[str] = ()) -> dict[str, int]:
        ordinals = base_posts.post_ordinals if isinstance(base_posts, AndResult) else np.asarray(tuple(base_posts), dtype=np.uint32)
        excluded = {self.tag_id(tag) for tag in exclude}
        counts: Counter[int] = Counter()
        for ordinal in ordinals:
            start, end = self.post_tag_offsets[int(ordinal):int(ordinal) + 2]
            counts.update(map(int, self.post_tag_ids[int(start):int(end)]))
        return {self.tags[tag_id]: count for tag_id, count in counts.items() if tag_id not in excluded}
