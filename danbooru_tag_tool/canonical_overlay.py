"""Current-dictionary overlay for the immutable Stage 5 raw index."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Iterable

import numpy as np


OVERLAY_FORMAT_VERSION = "stage5-canonical-overlay-v1"
STATISTICS_TAG_SCOPE = "general"


class OverlayError(ValueError):
    pass


class CanonicalOverlay:
    """Logical current-canonical view over raw source tag postings.

    Raw source identities remain authoritative.  A canonical posting is the
    union of all source postings mapped to it; no occurrence is added twice.
    """

    def __init__(self, index, path: str | Path, *, expected_snapshot_id: str | None = None):
        self.index = index
        self.path = Path(path)
        try:
            document = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise OverlayError("Invalid canonical overlay JSON") from exc
        self.metadata = document.get("metadata", {})
        if self.metadata.get("overlay_format_version") != OVERLAY_FORMAT_VERSION:
            raise OverlayError("Unsupported overlay format")
        if self.metadata.get("statistics_dataset_snapshot_id") != index.snapshot_id:
            raise OverlayError("Overlay and raw index snapshot mismatch")
        if expected_snapshot_id is not None and self.metadata["statistics_dataset_snapshot_id"] != expected_snapshot_id:
            raise OverlayError("Requested statistics snapshot does not match overlay")
        self.source_tag_identities = tuple(document.get("source_tag_identities", ()))
        self.canonical_to_source_tag_ids = {
            key: tuple(int(value) for value in values)
            for key, values in document.get("canonical_to_source_tag_ids", {}).items()
        }
        if len(self.source_tag_identities) != len(index.tags):
            raise OverlayError("Overlay source identity count does not match raw index")
        for source_id, item in enumerate(self.source_tag_identities):
            if item.get("source_tag") != index.tags[source_id]:
                raise OverlayError("Overlay source identity order does not match raw index")
        self._posting_cache: dict[str, np.ndarray] = {}
        self._global_count_cache: dict[str, int] = {}

    def source_status(self, source_tag: str) -> str:
        source_id = self.index.tag_id(source_tag)
        return self.source_tag_identities[source_id]["identity"]

    def source_canonical(self, source_tag: str) -> str | None:
        source_id = self.index.tag_id(source_tag)
        return self.source_tag_identities[source_id].get("canonical")

    def source_tag_ids(self, canonical: str) -> tuple[int, ...]:
        return self.canonical_to_source_tag_ids.get(canonical, ())

    def canonical_postings(self, canonical: str) -> np.ndarray:
        cached = self._posting_cache.get(canonical)
        if cached is not None:
            return cached
        source_ids = self.source_tag_ids(canonical)
        if not source_ids:
            raise KeyError(f"Unknown overlay canonical: {canonical}")
        postings = [self.index.tag_post_ordinals[
            int(self.index.tag_post_offsets[source_id]):int(self.index.tag_post_offsets[source_id + 1])
        ] for source_id in source_ids]
        result = np.unique(np.concatenate(postings)) if postings else np.empty(0, dtype=np.uint32)
        self._posting_cache[canonical] = result
        return result

    def global_count(self, canonical: str) -> int:
        cached = self._global_count_cache.get(canonical)
        if cached is not None:
            return cached
        source_ids = self.source_tag_ids(canonical)
        if not source_ids:
            raise KeyError(f"Unknown overlay canonical: {canonical}")
        # Almost every logical canonical has exactly one raw identity.  Reuse
        # its precomputed snapshot count instead of faulting a posting list;
        # merged aliases still use the required posting-union cardinality.
        result = (int(self.index.runtime_global_counts[source_ids[0]]) if len(source_ids) == 1
                  else int(self.canonical_postings(canonical).size))
        self._global_count_cache[canonical] = result
        return result

    def intersect(self, canonicals: Iterable[str]):
        names = tuple(dict.fromkeys(canonicals))
        if not names:
            raise ValueError("At least one canonical tag is required")
        postings = sorted((self.canonical_postings(name) for name in names), key=len)
        result = np.asarray(postings[0], dtype=np.uint32)
        for posting in postings[1:]:
            result = np.intersect1d(result, posting, assume_unique=True)
            if not len(result):
                break
        from .runtime_index import AndResult
        return AndResult(result, self.index.post_ids[result])

    def aggregate(self, base_posts, *, exclude: Iterable[str] = ()) -> dict[str, int]:
        """Aggregate by logical canonical, unioning aliases per post."""
        ordinals = base_posts.post_ordinals if hasattr(base_posts, "post_ordinals") else np.asarray(tuple(base_posts), dtype=np.uint32)
        excluded = set(exclude)
        counts: Counter[str] = Counter()
        source_to_canonical = {
            source_id: item.get("canonical")
            for source_id, item in enumerate(self.source_tag_identities)
        }
        for ordinal in ordinals:
            start, end = self.index.post_tag_offsets[int(ordinal):int(ordinal) + 2]
            logical = set()
            for source_id in self.index.post_tag_ids[int(start):int(end)]:
                canonical = source_to_canonical.get(int(source_id))
                logical.add(canonical if canonical else self.index.tags[int(source_id)])
            for tag in logical:
                if tag not in excluded:
                    counts[tag] += 1
        return dict(counts)

    def validate(self) -> None:
        expected_hash = self.metadata.get("overlay_payload_sha256")
        payload = {
            "canonical_to_source_tag_ids": {key: list(value) for key, value in sorted(self.canonical_to_source_tag_ids.items())},
            "source_tag_identities": list(self.source_tag_identities),
        }
        digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if expected_hash and digest != expected_hash:
            raise OverlayError("Overlay payload SHA-256 mismatch")
