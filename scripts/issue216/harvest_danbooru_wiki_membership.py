#!/usr/bin/env python3
"""Bulk harvest explicit Danbooru Copyright Character/Member wiki sections.

This is a read-only discovery step. It searches by Copyright root, fetches only
root-scoped pages/list pages, and writes regenerable results under ignored tmp.
Only direct canonical wiki-link targets in explicit Character/Member headings
and list/table rows are emitted. Canonical ledgers are never written here.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import re
import threading
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
ISSUE216 = ROOT / "docs/issue216"
API = "https://danbooru.donmai.us"
USER_AGENT = "DanbooruTagTool-Issue216-ReadOnly-AuthorityResearch/1.0"
THREADS = 4
MIN_REQUEST_INTERVAL_SEC = 0.40
LINK_RE = re.compile(r"\[\[([^\[\]|#]+)(?:\|[^\]]*)?\]\]")
HEADING_PATTERNS = (
    re.compile(r"^h[1-6](?:#[^.]*)?\.(.*?)\s*$", re.IGNORECASE),
    re.compile(r"^\s*={2,6}\s*(.*?)\s*={2,6}\s*$"),
    re.compile(r"^\s*#{1,6}\s+(.*?)\s*#*\s*$"),
)
MEMBER_HEADING_RE = re.compile(r"\b(?:characters?|members?)\b", re.IGNORECASE)


class RateLimiter:
    def __init__(self, interval: float) -> None:
        self.interval = interval
        self.lock = threading.Lock()
        self.next_request = 0.0

    def wait(self) -> None:
        with self.lock:
            now = time.monotonic()
            delay = max(0.0, self.next_request - now)
            if delay:
                time.sleep(delay)
            self.next_request = time.monotonic() + self.interval


LIMITER = RateLimiter(MIN_REQUEST_INTERVAL_SEC)
NETWORK_SEMAPHORE = threading.Semaphore(THREADS)


def cache_path(directory: Path, key: str) -> Path:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return directory / f"{digest}.json"


def read_json(path: Path) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def get_json(url: str, path: Path) -> object:
    cached = read_json(path)
    if cached is not None:
        return cached
    path.parent.mkdir(parents=True, exist_ok=True)
    last_error: Exception | None = None
    for attempt in range(6):
        LIMITER.wait()
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with NETWORK_SEMAPHORE:
                with urllib.request.urlopen(request, timeout=40) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            return payload
        except Exception as error:  # retry transient 429/5xx and preserve progress
            last_error = error
            if attempt == 5:
                break
            time.sleep(min(60.0, 2.0 ** attempt))
    raise RuntimeError(f"Danbooru request failed after retries: {url}: {last_error}")


def tag_slug(value: str) -> str:
    value = value.strip().lower().replace("_(series)", "_series")
    return re.sub(r"\s+", "_", value)


def list_title_scoped_to(title: str, root_slugs: set[str]) -> bool:
    name = title.lower()
    if not name.startswith("list_of_"):
        return False
    if not re.search(r"(?:character|member|cast)", name):
        return False
    return any(slug and slug in name[len("list_of_"):] for slug in root_slugs)


def candidate_pages_for_root(root: str, search_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    slugs = {tag_slug(root)}
    if root.endswith("_(series)"):
        slugs.add(tag_slug(root[:-len("_(series)")] + "_series"))
    selected = []
    for row in search_rows:
        title = str(row.get("title", "")).strip()
        page_id = row.get("id")
        if not title or not page_id:
            continue
        if title.lower() == root.lower() or list_title_scoped_to(title, slugs):
            selected.append({"id": int(page_id), "title": title})
    return selected


def explicit_member_links(body: str) -> list[tuple[str, str]]:
    headings: list[tuple[int, str]] = []
    lines = body.replace("\r", "").split("\n")
    for index, line in enumerate(lines):
        heading = None
        for pattern in HEADING_PATTERNS:
            match = pattern.match(line.strip())
            if match:
                heading = match.group(1).strip()
                break
        if heading is not None:
            headings.append((index, heading))
    result: list[tuple[str, str]] = []
    for position, (start, heading) in enumerate(headings):
        if not MEMBER_HEADING_RE.search(heading):
            continue
        end = headings[position + 1][0] if position + 1 < len(headings) else len(lines)
        for line in lines[start + 1:end]:
            stripped = line.lstrip()
            # Only explicit list entries or table rows count; never harvest prose links.
            if not (stripped.startswith(("*", "-", "#", "|"))):
                continue
            match = LINK_RE.search(stripped)
            if not match:
                continue
            surface = match.group(1).strip()
            target = re.sub(r"\s+", "_", surface).strip("_").lower()
            if target:
                result.append((heading, target))
    return result


def load_root_rows() -> list[str]:
    # Queue v2 is ordered by measured exact roster overlap and empirical source
    # family yield. Keep that order; alphabetic sorting silently discarded the
    # research priority signal and repeatedly favored no meaningful portfolio.
    queue_v2 = ISSUE216 / "SOURCE_YIELD_QUEUE_V2.csv"
    queue_path = queue_v2 if queue_v2.exists() else ISSUE216 / "SOURCE_YIELD_QUEUE_V1.csv"
    with queue_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if queue_path == queue_v2:
        rows.sort(key=lambda row: int(row.get("priority_rank", "0") or 0))
    return list(dict.fromkeys(row["candidate_root"].strip() for row in rows
                              if row.get("candidate_root", "").strip()))


def canonical_source_url(value: str) -> str:
    parsed = urlparse((value or "").strip())
    path = re.sub(r"/+", "/", parsed.path).rstrip("/")
    return urllib.parse.urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", parsed.query, ""))


def reviewed_source_urls() -> set[str]:
    """URLs whose source scope is already in a reviewed/current registry or scout row."""
    urls = set()
    for path in (ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv",
                 ISSUE216 / "ROSTER_SCOUT_INVENTORY_V1.csv"):
        if not path.exists():
            continue
        with path.open(encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                if path.name.startswith("ROSTER_SCOUT") and row.get("review_state", "").upper() not in {"SCOUTED", "REGISTRY_REJOIN"}:
                    continue
                value = row.get("source_url", "").strip()
                if value:
                    urls.add(canonical_source_url(value))
    return urls


def run(output_dir: Path, roots: list[str] | None = None) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    search_cache = output_dir / "search_cache"
    page_cache = output_dir / "page_cache"
    root_rows = roots or load_root_rows()

    def search_root(root: str) -> tuple[str, list[dict[str, object]], str | None]:
        query = urllib.parse.urlencode({"search[body_matches]": root, "limit": 100, "only": "id,title"})
        url = f"{API}/wiki_pages.json?{query}"
        try:
            response = get_json(url, cache_path(search_cache, root))
            records = response if isinstance(response, list) else []
            return root, candidate_pages_for_root(root, records), None
        except Exception as error:
            return root, [], str(error)

    page_candidates: dict[int, dict[str, object]] = {}
    root_errors: list[dict[str, str]] = []
    completed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as pool:
        for root, pages, error in pool.map(search_root, root_rows):
            completed += 1
            for page in pages:
                page_candidates[int(page["id"])] = page
            if error:
                root_errors.append({"candidate_root": root, "error": error})
            if completed % 100 == 0:
                print(f"root searches complete: {completed}/{len(root_rows)}; page candidates={len(page_candidates)}", flush=True)

    # A page title is mapped to a canonical Copyright root only when exactly one
    # validated canonical/alias slug identifies it.
    canonical_roots = {row["copyright_canonical"] for row in csv.DictReader(
        (ISSUE216 / "COPYRIGHT_ROOTS_V1.csv").open(encoding="utf-8-sig", newline=""))}
    with (ROOT / "docs/issue180/v3/migrated_evidence_seed_v3.csv").open(encoding="utf-8-sig", newline="") as stream:
        alias_rows = [row for row in csv.DictReader(stream)
                      if row.get("subject_type") == "Family" and row.get("relation_type") == "FAMILY_HOME"
                      and row.get("review_state") == "VALIDATED"]
    slugs_to_roots: dict[str, set[str]] = defaultdict(set)
    for root in canonical_roots:
        slugs_to_roots[tag_slug(root)].add(root)
        if root.endswith("_(series)"):
            slugs_to_roots[tag_slug(root[:-len("_(series)")] + "_series")].add(root)
    for row in alias_rows:
        if row.get("object_key") in canonical_roots:
            slugs_to_roots[tag_slug(row["subject_key"])].add(row["object_key"])

    # Keep only scoped root pages or lists whose title resolves to one canonical root.
    source_roots_by_page: dict[int, set[str]] = defaultdict(set)
    for page in page_candidates.values():
        title = str(page["title"])
        if title in canonical_roots:
            source_roots_by_page[int(page["id"])].add(title)
        elif title.lower().startswith("list_of_"):
            rest = title.lower()[len("list_of_"):]
            for slug, matching_roots in slugs_to_roots.items():
                if slug and slug in rest:
                    source_roots_by_page[int(page["id"])].update(matching_roots)

    cohort_rows = list(csv.DictReader((ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv").open(encoding="utf-8-sig", newline="")))
    decision_rows = list(csv.DictReader((ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv").open(encoding="utf-8-sig", newline="")))
    cohort_tags = {row["canonical_character"] for row in cohort_rows}
    open_tags = {row["canonical_character"] for row in decision_rows if row["research_state"] == "UNRESEARCHED"}
    page_evidence: list[dict[str, str]] = []
    page_errors: list[dict[str, str]] = []

    def fetch_page(page_id: int, title: str) -> tuple[int, str, object | None, str | None]:
        url = f"{API}/wiki_pages/{page_id}.json"
        try:
            payload = get_json(url, page_cache / f"{page_id}.json")
            return page_id, title, payload, None
        except Exception as error:
            return page_id, title, None, str(error)

    reviewed_urls = reviewed_source_urls()
    candidate_scoped_pages = [(pid, str(meta["title"])) for pid, meta in page_candidates.items()
                              if len(source_roots_by_page.get(pid, set())) == 1]
    selected_pages = sorted((pid, title) for pid, title in candidate_scoped_pages
                            if canonical_source_url(
                                f"https://danbooru.donmai.us/wiki_pages/{urllib.parse.quote(title, safe='()!:#,._-')}"
                            ) not in reviewed_urls)
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as pool:
        futures = [pool.submit(fetch_page, pid, title) for pid, title in selected_pages]
        for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
            page_id, title, payload, error = future.result()
            if error:
                page_errors.append({"page_id": str(page_id), "title": title, "error": error})
                continue
            root = next(iter(source_roots_by_page[page_id]))
            body = str(payload.get("body", "")) if isinstance(payload, dict) else ""
            exact_links = explicit_member_links(body)
            url = f"{API}/wiki_pages/{urllib.parse.quote(title, safe='()!:#,._-')}"
            for heading, target in exact_links:
                if target not in cohort_tags or target not in open_tags:
                    continue
                page_evidence.append({
                    "canonical_character": target, "semantic_root": root, "page_id": str(page_id),
                    "page_title": title, "source_url": url, "section_heading": heading,
                    "matched_surface": target, "mapping_method": "EXACT_CANONICAL",
                    "mapping_evidence": f"Direct canonical wiki link [[{target}]] in explicit {heading} section; list/table row only.",
                })
            if index % 100 == 0:
                print(f"wiki pages parsed: {index}/{len(selected_pages)}; exact open rows={len(page_evidence)}", flush=True)

    with (output_dir / "EXACT_DANBOORU_CHARACTER_MEMBER_LINKS.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = ["canonical_character", "semantic_root", "page_id", "page_title", "source_url",
                  "section_heading", "matched_surface", "mapping_method", "mapping_evidence"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(page_evidence, key=lambda row: (row["canonical_character"], row["semantic_root"], row["page_id"])))
    (output_dir / "ROOT_SEARCH_ERRORS.json").write_text(json.dumps(root_errors, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "PAGE_FETCH_ERRORS.json").write_text(json.dumps(page_errors, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "candidate_root_count": len(root_rows), "unique_wiki_pages_discovered": len(page_candidates),
        "reviewed_source_url_repeats_skipped": len(candidate_scoped_pages) - len(selected_pages),
        "unique_explicit_scope_pages_fetched": len(selected_pages), "open_exact_membership_rows": len(page_evidence),
        "unique_open_characters": len({row["canonical_character"] for row in page_evidence}),
        "characters_with_multiple_roots": sum(1 for tag in {row["canonical_character"] for row in page_evidence}
                                               if len({row["semantic_root"] for row in page_evidence if row["canonical_character"] == tag}) > 1),
        "root_search_errors": len(root_errors), "page_fetch_errors": len(page_errors),
        "scope_policy": "explicit Character/Member headings + direct [[canonical]] link in bullet/list/table row only; exact title/root alias joins only",
    }
    (output_dir / "SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".tmp-issue216-work/danbooru-wiki-harvest")
    parser.add_argument("--root-limit", type=int, default=0, help="debug only; 0 processes the complete source-yield root queue")
    args = parser.parse_args()
    roots = load_root_rows()
    if args.root_limit:
        roots = roots[:args.root_limit]
    summary = run(args.output, roots)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
