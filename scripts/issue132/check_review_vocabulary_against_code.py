#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load_validator():
    path=ROOT/"scripts/issue132/validate_luna_pass_a.py"
    spec=importlib.util.spec_from_file_location("issue132_validator_vocab", path)
    if spec is None or spec.loader is None:
        raise SystemExit("unable to load validator vocabulary")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def block(text: str, start: str, end: str) -> str:
    i=text.find(start)
    if i < 0:
        raise SystemExit(f"missing block start: {start}")
    j=text.find(end, i)
    if j < 0:
        raise SystemExit(f"missing block end after: {start}")
    return text[i:j]

def parse_general_route_map(text: str) -> dict[str,str]:
    b=block(text, "public static string? GeneralRoute", "public static string? SpecialRoute")
    result={}
    pattern=re.compile(r'((?:"[A-Z0-9_]+"s*(?:ors*)?)+)s*=>s*"([A-Z0-9_]+)"')
    for lhs,rhs in pattern.findall(b):
        for genre in re.findall(r'"([A-Z0-9_]+)"', lhs):
            result[genre]=rhs
    return result

def main():
    v=load_validator()

    unified=(ROOT/"src/DanbooruTagTool.Core/UnifiedBrowse.cs").read_text(encoding="utf-8")
    special=(ROOT/"src/DanbooruTagTool.Core/SpecialBrowseV2.cs").read_text(encoding="utf-8")
    taxonomy=json.loads((ROOT/"docs/issue64/production_candidate/general_taxonomy.json").read_text(encoding="utf-8"))

    routes_block=block(
        unified,
        "public static readonly UnifiedBrowseRouteDefinition[] Routes",
        "public static string Label"
    )
    code_routes=set(re.findall(r'new\("([A-Z0-9_]+)"\s*,', routes_block))
    if code_routes != set(v.ROUTES):
        missing=sorted(code_routes-set(v.ROUTES))
        extra=sorted(set(v.ROUTES)-code_routes)
        raise SystemExit(f"route vocabulary drift: validator_missing={missing} validator_extra={extra}")

    general_map=parse_general_route_map(unified)
    expected_local={}
    genres=taxonomy.get("genres",{})
    for genre,meta in genres.items():
        parent=general_map.get(genre)
        if parent is None:
            continue
        for sub in (meta.get("subgenres") or {}):
            expected_local[f"{genre}/{sub}"]=parent

    for genre in ("EXPRESSION_EMOTION","GAZE_ORIENTATION","CLOTHING_STATE_EXPOSURE"):
        if genre in genres:
            parent=general_map.get(genre)
            if parent is None:
                raise SystemExit(f"local-source genre has no Unified route: {genre}")
            expected_local[f"{genre}/"]=parent

    if dict(sorted(expected_local.items())) != dict(sorted(v.LOCAL_PARENT.items())):
        expected=set(expected_local.items())
        actual=set(v.LOCAL_PARENT.items())
        missing=sorted(expected-actual)
        extra=sorted(actual-expected)
        raise SystemExit(f"local refinement vocabulary drift: missing={missing} extra={extra}")

    body_block=block(
        special,
        "public static readonly SpecialBrowseV2FacetDefinition[] BodySites",
        "public static readonly SpecialBrowseV2FacetDefinition[] Themes"
    )
    theme_block=block(
        special,
        "public static readonly SpecialBrowseV2FacetDefinition[] Themes",
        "public static string Label"
    )
    code_body=set(re.findall(r'new\("([A-Z0-9_]+)"\s*,', body_block))
    code_themes=set(re.findall(r'new\("([A-Z0-9_]+)"\s*,', theme_block))

    if code_body != set(v.BODY):
        raise SystemExit(
            f"body facet vocabulary drift: code={sorted(code_body)} validator={sorted(v.BODY)}"
        )
    if code_themes != set(v.THEMES):
        raise SystemExit(
            f"theme facet vocabulary drift: code={sorted(code_themes)} validator={sorted(v.THEMES)}"
        )

    result={
        "schema_version":"issue132-review-vocabulary-code-check-v1",
        "route_count":len(code_routes),
        "local_refinement_count":len(expected_local),
        "body_site_count":len(code_body),
        "theme_count":len(code_themes),
        "routes":sorted(code_routes),
        "local_refinement_parent":dict(sorted(expected_local.items())),
        "body_site_ids":sorted(code_body),
        "theme_ids":sorted(code_themes),
        "status":"PASS"
    }
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
