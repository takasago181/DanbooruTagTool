from __future__ import annotations
import bisect, gzip, json, math, re, unicodedata
from pathlib import Path

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", (s or "").strip().lower())
    s = s.replace("_", " ")
    s = re.sub(r"\s+", " ", s)
    return s

def has_japanese(s: str) -> bool:
    return bool(re.search(r"[\u3040-\u30ff\u3400-\u9fff]", s or ""))

def split_categories(s: str):
    if not s:
        return set()
    return {x.strip() for x in re.split(r"\s*/\s*|\s*\|\s*|、|,", s) if x.strip()}

class Catalog:
    def __init__(self, path: Path):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            d = json.load(f)
        self.version = d["version"]
        self.snapshot = d["snapshot"]
        self.tags = d["tags"]
        self.aliases = d["aliases"]
        self.special_terms = d["special_terms"]
        self.special_by_canonical = {k: v for k,v in d["special_by_canonical"].items()}
        self.entries = d["search_entries"]
        self.keys = [x["q"] for x in self.entries]
        self.verified_special_counts = d["verified_special_counts"]

    def tag(self, canonical):
        return self.tags.get(canonical)

    def japanese(self, canonical):
        t = self.tags.get(canonical)
        if not t:
            return ""
        vals = t.get("japanese") or []
        if vals:
            return " / ".join(dict.fromkeys(vals))
        idxs = self.special_by_canonical.get(canonical, [])
        vals = []
        for i in idxs:
            ja = self.special_terms[i].get("japanese","")
            if ja and ja not in vals:
                vals.append(ja)
        return " / ".join(vals)

    def resolve(self, raw):
        q = norm(raw)
        if not q:
            return {"ok": False, "error": "空のタグです"}
        canonical_guess = q.replace(" ", "_")
        if canonical_guess in self.tags:
            return {"ok": True, "canonical": canonical_guess, "source": "canonical"}

        a = self.aliases.get(q)
        if a:
            targets = [x for x in a.get("targets",[]) if x in self.tags]
            if len(targets) == 1:
                return {"ok": True, "canonical": targets[0], "source": "alias"}
            if len(targets) > 1:
                return {"ok": False, "ambiguous": targets, "error": "複数のalias候補があります"}

        # Special exact term/Japanese search.
        found = []
        lo = bisect.bisect_left(self.keys, q)
        i = lo
        while i < len(self.entries) and self.entries[i]["q"] == q:
            c = self.entries[i]["canonical"]
            if c not in found:
                found.append(c)
            i += 1
        if len(found) == 1:
            return {"ok": True, "canonical": found[0], "source": "special/search"}
        if len(found) > 1:
            return {"ok": False, "ambiguous": found, "error": "複数候補があります"}
        return {"ok": False, "error": "一致するcanonical/aliasが見つかりません"}

    def search(self, raw, limit=40):
        q = norm(raw)
        if not q:
            return []
        candidates = {}

        def push(entry, tier):
            can = entry["canonical"]
            t = self.tags.get(can)
            if not t:
                return
            current = candidates.get(can)
            special = bool(t.get("special") or entry.get("special"))
            # Lower tuple is better.
            rank = (
                tier,
                0 if special else 1,
                0 if entry["kind"] in ("canonical","prompt","japanese","special_japanese") else 1,
                -int(t.get("post_count") or 0),
                t.get("prompt") or can
            )
            if current is None or rank < current["rank"]:
                candidates[can] = {"entry": entry, "tag": t, "rank": rank}

        # Exact.
        lo = bisect.bisect_left(self.keys, q)
        i = lo
        while i < len(self.entries) and self.entries[i]["q"] == q:
            push(self.entries[i], 0)
            i += 1

        # Prefix.
        i = lo
        max_scan = 1500
        scanned = 0
        while i < len(self.entries) and self.entries[i]["q"].startswith(q) and scanned < max_scan:
            push(self.entries[i], 1)
            i += 1
            scanned += 1

        # Word/substring fallback. The catalog is small enough for this on >=2 chars.
        if len(candidates) < limit and len(q) >= 2:
            for e in self.entries:
                s = e["q"]
                if q not in s or s.startswith(q):
                    continue
                tier = 2 if re.search(r"(^|[\s\-])" + re.escape(q), s) else 3
                push(e, tier)
                if len(candidates) >= limit * 8:
                    break

        out = []
        for can, c in sorted(candidates.items(), key=lambda kv: kv[1]["rank"])[:limit]:
            t = c["tag"]
            out.append({
                "canonical": can,
                "prompt": t["prompt"],
                "japanese": self.japanese(can),
                "post_count": int(t.get("post_count") or 0),
                "category": t.get("category",""),
                "category_ja": t.get("category_ja",""),
                "special": bool(t.get("special") or c["entry"].get("special")),
                "match_kind": c["entry"]["kind"],
                "matched": c["entry"]["display"],
            })
        return out

    def special_related(self, selected, limit=80, special_only=True):
        selected = [x for x in selected if x in self.tags]
        if not selected:
            return []
        wanted_main = set()
        wanted_related = set()
        for can in selected:
            for idx in self.special_by_canonical.get(can, []):
                s = self.special_terms[idx]
                wanted_main |= split_categories(s.get("main",""))
                wanted_related |= split_categories(s.get("related",""))

        if not wanted_main and not wanted_related:
            return []

        scored = {}
        for s in self.special_terms:
            can = s.get("chosen_canonical","")
            if not can or can not in self.tags or can in selected:
                continue
            t = self.tags[can]
            if special_only and not t.get("special"):
                continue
            cm = split_categories(s.get("main",""))
            cr = split_categories(s.get("related",""))
            score = 0.0
            score += 5.0 * len(cm & wanted_main)
            score += 2.0 * len(cr & wanted_related)
            score += 2.0 * len(cm & wanted_related)
            score += 1.0 * len(cr & wanted_main)
            if s.get("layer") == "Core":
                score += 0.5
            if score <= 0:
                continue
            score += min(1.5, math.log10(max(1, int(t.get("post_count") or 0))) / 5.0)
            old = scored.get(can)
            if old is None or score > old[0]:
                scored[can] = (score, s)

        out = []
        for can, (score, s) in sorted(scored.items(), key=lambda x: (-x[1][0], -int(self.tags[x[0]].get("post_count") or 0)))[:limit]:
            t = self.tags[can]
            out.append({
                "canonical": can,
                "prompt": t["prompt"],
                "japanese": self.japanese(can),
                "post_count": int(t.get("post_count") or 0),
                "category": t.get("category",""),
                "special": bool(t.get("special")),
                "layer": s.get("layer",""),
                "main": s.get("main",""),
                "score": score,
            })
        return out

    def prompt_for(self, selected, loras):
        parts = []
        seen = set()
        for can in selected:
            t = self.tags.get(can)
            if not t:
                continue
            p = t.get("prompt") or can.replace("_"," ")
            if p not in seen:
                seen.add(p)
                parts.append(p)
        for l in loras:
            for trig in l.get("triggers", []):
                trig = trig.strip()
                if trig and trig not in seen:
                    seen.add(trig)
                    parts.append(trig)
            name = l.get("name","").strip()
            weight = l.get("weight","1.0").strip() or "1.0"
            if name:
                parts.append(f"<lora:{name}:{weight}>")
        return ", ".join(parts)
