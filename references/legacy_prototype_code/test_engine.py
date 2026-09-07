from pathlib import Path
import csv
import tempfile
import numpy as np

from engine import CooccurrenceEngine


def main():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)

        # Matrix index must be alphabetical among available=True rows:
        # blue_hair, long_hair, school_uniform, sitting, twintails
        rows = [
            ("twintails", 100, "general", "True"),
            ("school_uniform", 80, "general", "True"),
            ("long_hair", 120, "general", "True"),
            ("sitting", 90, "general", "True"),
            ("blue_hair", 110, "general", "True"),
        ]
        with (d / "available_tags.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["tag", "count", "category", "available"])
            w.writerows(rows)

        tags = sorted(r[0] for r in rows)
        idx = {t:i for i,t in enumerate(tags)}
        m = np.eye(len(tags), dtype=np.float32)
        # Candidate long_hair strongly co-occurs with both query tags.
        m[idx["long_hair"], idx["twintails"]] = 0.8
        m[idx["long_hair"], idx["school_uniform"]] = 0.7
        # blue_hair is strong with only one query -> should rank lower in common mode.
        m[idx["blue_hair"], idx["twintails"]] = 0.95
        m[idx["blue_hair"], idx["school_uniform"]] = 0.10
        # sitting medium with both.
        m[idx["sitting"], idx["twintails"]] = 0.5
        m[idx["sitting"], idx["school_uniform"]] = 0.5
        np.savez_compressed(d / "cooccurrence_all_normalized.npz", cooc_norm=m)

        for name, header in [
            ("alias_index_20260902.csv",
             ["NormalizedAlias","AliasRawVariants","AliasPrompt","TargetCount","CanonicalTargets",
              "CanonicalPromptTargets","ResolutionStatus","CanonicalPrecedenceTag","Special2788Terms"]),
            ("special2788_20260902.csv",
             ["ID","Tag","日本語","Layer","主カテゴリ","関連カテゴリ","元カテゴリ","性別スコープ",
              "Danbooru種別","post_count","件数帯","canonical_target","元の日本語説明","検索キー",
              "NormalizedTag","SourceMatchType","CanonicalTargets","ChosenCanonicalTag",
              "ChosenCanonicalPromptTag","DanbooruCategoryID","DanbooruCategory","Danbooruカテゴリ日本語",
              "VerifiedPostCount","CountCheck","LayerCheck","AliasAmbiguity","TranslationPairCheck",
              "TranslationQuality","TranslationReviewReason"]),
            ("danbooru_full_tag_kb_20260902.csv",
             ["DanbooruTag","PromptTag","DanbooruCategoryID","DanbooruCategory","カテゴリ日本語",
              "post_count","頻度帯","AliasesRaw","AliasesPromptUnique","AliasRawCount","AliasUniqueCount",
              "Special2788","SpecialMatchCount","Special2788MatchedTerms","SpecialMatchTypes","Special日本語",
              "SpecialLayer","Special主カテゴリ","Special関連カテゴリ","Special性別スコープ","Snapshot"]),
        ]:
            with (d / name).open("w", encoding="utf-8", newline="") as f:
                csv.writer(f).writerow(header)

        e = CooccurrenceEngine(d)
        info = e.load()
        resolved, results = e.search(
            ["twintails", "school uniform"],
            category="general",
            mode="common",
            top_n=3,
            ignore_generic=False,
        )

        assert [r.canonical for r in resolved] == ["twintails", "school_uniform"]
        assert results[0].tag == "long_hair", [r.tag for r in results]
        assert results[1].tag == "sitting", [r.tag for r in results]
        assert results[2].tag == "blue_hair", [r.tag for r in results]
        print("PASS")
        print(info)
        for r in results:
            print(r.tag, r.score, r.per_query)


if __name__ == "__main__":
    main()
