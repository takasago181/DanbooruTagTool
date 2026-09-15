"""Issue #97 read-only Special expansion quality audit.

Checks committed #96 authority surfaces and, with --catalog, the built
production catalog. Never opens or mutates UserData/user.db.
"""
from __future__ import annotations

import argparse, csv, json, re, sqlite3, sys
from collections import Counter
from pathlib import Path
from typing import Iterable

BASE_SPECIAL_COUNT = 2788
EXPANDED_SPECIAL_COUNT = 2983
PROMOTION_START_ID = 2789
PROMOTION_COUNT = 195

PROMOTION = Path("docs/issue96/special_expansion_promotion_proposal_v1.csv")
JA_METADATA = Path("docs/issue96/special_expansion_ja_metadata_v1.csv")
TAXONOMY = Path("docs/issue96/special_expansion_taxonomy_final_v1.csv")
DUPLICATE_VALIDATED = Path("docs/issue96/special_expansion_duplicate_validated_v1.csv")
GENERATION_PROFILE = Path("data/generation/special2788_generation_profile.csv")
PRODUCT_FIT = Path("data/special2788/product_fit_verdicts.csv")

STATUS_NAMES = {0:"AutoCandidate",1:"HumanResolved",2:"ReferenceOnlyNoDirectBrowse",3:"DeferProductFitReview",4:"OutOfScopeNoBrowse"}
EXPECTED_STATUS = {"AutoCandidate":2745,"HumanResolved":210,"ReferenceOnlyNoDirectBrowse":21,"DeferProductFitReview":6,"OutOfScopeNoBrowse":1}
ACTIVE_2788_SCAN = (
    Path("src/DanbooruTagTool.Data/AcceptedAssetImporter.cs"),
    Path("src/DanbooruTagTool.Data/SpecialBrowseV2Overlay.cs"),
    Path("scripts/maintenance/catalog_health.py"),
    Path("scripts/maintenance/check_local_health.ps1"),
    Path("src/DanbooruTagTool.Tests/ProductionTests.cs"),
    Path("src/DanbooruTagTool.Tests/TechnicalFixTests.cs"),
)

def read_csv(root:Path, rel:Path)->list[dict[str,str]]:
    path=root/rel
    if not path.is_file(): raise RuntimeError(f"missing audit input: {rel.as_posix()}")
    with path.open("r",encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))

def exact(rows:Iterable[dict[str,str]],field:str,expected:range,label:str)->dict[int,dict[str,str]]:
    out={}
    for row in rows:
        try: item_id=int(row[field])
        except (KeyError,TypeError,ValueError) as e: raise RuntimeError(f"{label}: invalid {field}") from e
        if item_id in out: raise RuntimeError(f"{label}: duplicate id {item_id}")
        out[item_id]=row
    want=set(expected); got=set(out)
    if got!=want: raise RuntimeError(f"{label}: id coverage mismatch missing={sorted(want-got)[:20]} extra={sorted(got-want)[:20]}")
    return out

def nonblank(row:dict[str,str],fields:Iterable[str],label:str)->None:
    blank=[f for f in fields if not row.get(f,"").strip()]
    if blank: raise RuntimeError(f"{label}: blank fields {blank}")

def check_authority(root:Path)->tuple[dict[int,dict[str,str]],dict[str,int]]:
    ids=range(PROMOTION_START_ID,EXPANDED_SPECIAL_COUNT+1)
    promotion=exact(read_csv(root,PROMOTION),"proposed_special_id",ids,"promotion")
    ja=exact(read_csv(root,JA_METADATA),"proposed_special_id",ids,"ja metadata")
    taxonomy=exact(read_csv(root,TAXONOMY),"proposed_special_id",ids,"taxonomy")
    duplicate=exact(read_csv(root,DUPLICATE_VALIDATED),"proposed_special_id",ids,"duplicate validation")
    surfaces=set()
    for item_id in ids:
        row=promotion[item_id]; label=f"promotion {item_id}"
        nonblank(row,("canonical_tag","display_ja","search_ja","kind_id","duplicate_guard","proposal_status"),label)
        row_surfaces={row["canonical_tag"],*[v.strip() for v in row.get("canonical_aliases","").split("|") if v.strip()]}
        overlap=surfaces & row_surfaces
        if overlap: raise RuntimeError(f"{label}: duplicate promoted canonical/alias surface {sorted(overlap)}")
        surfaces.update(row_surfaces)
        if row["duplicate_guard"]!="CURRENT_SPECIAL_GAP_PASS" or row["proposal_status"]!="PREP_READY_FOR_DEV_REVIEW":
            raise RuntimeError(f"{label}: promotion gate not passed")
        j=ja[item_id]; nonblank(j,("canonical_tag","display_ja","search_ja","ja_status"),f"ja {item_id}")
        if any(j[f]!=row[f] for f in ("canonical_tag","display_ja","search_ja")): raise RuntimeError(f"ja {item_id}: authority mismatch")
        t=taxonomy[item_id]; nonblank(t,("canonical_tag","kind_id","browse_status","validation_status"),f"taxonomy {item_id}")
        if t["canonical_tag"]!=row["canonical_tag"] or t["validation_status"]!="TAXONOMY_RESOLVED": raise RuntimeError(f"taxonomy {item_id}: unresolved/mismatch")
        d=duplicate[item_id]; nonblank(d,("canonical_tag","duplicate_guard","validation_status"),f"duplicate {item_id}")
        if d["canonical_tag"]!=row["canonical_tag"] or d["duplicate_guard"]!="PASS_GENERAL_ONLY_GAP_CURRENT_SPECIAL_2788" or d["validation_status"]!="IDENTITY_LAYER_TAXONOMY_DUPLICATE_READY":
            raise RuntimeError(f"duplicate {item_id}: duplicate gate not passed")
    return promotion,{"promotion":len(promotion),"ja_metadata_promoted":len(ja),"taxonomy_promoted":len(taxonomy),"duplicate_validated_promoted":len(duplicate)}

def check_sidecars(root:Path,promotion:dict[int,dict[str,str]])->dict[str,int]:
    ids=range(1,EXPANDED_SPECIAL_COUNT+1)
    profile=exact(read_csv(root,GENERATION_PROFILE),"SpecialID",ids,"generation profile")
    fit=exact(read_csv(root,PRODUCT_FIT),"special_id",ids,"product fit")
    for item_id,row in fit.items(): nonblank(row,("product_fit_verdict",),f"product fit {item_id}")
    for item_id,p in promotion.items():
        row=profile[item_id]
        if row.get("Tag")!=p["canonical_tag"] or row.get("EvidenceClass")!="ISSUE96_ACCEPTED_SPECIAL_EXPANSION": raise RuntimeError(f"generation profile {item_id}: Issue96 mismatch")
    return {"generation_profile":len(profile),"product_fit":len(fit)}

def parse_special_id(value:str)->int:
    if not value.startswith("S:"): raise RuntimeError(f"invalid Special catalog id: {value}")
    try: return int(value[2:])
    except ValueError as e: raise RuntimeError(f"invalid Special catalog id: {value}") from e

def check_catalog(path:Path)->dict[str,object]:
    if not path.is_file(): raise RuntimeError(f"catalog not found: {path}")
    uri=f"file:{path.resolve()}?mode=ro&immutable=1"
    with sqlite3.connect(uri,uri=True) as con: rows=con.execute("SELECT id,payload FROM entries ORDER BY ordinal").fetchall()
    specials={}
    for catalog_id,text in rows:
        payload=json.loads(text)
        if payload.get("IsSpecial") is True:
            item_id=parse_special_id(catalog_id)
            if item_id in specials: raise RuntimeError(f"catalog duplicate Special id: {item_id}")
            specials[item_id]=payload
    if set(specials)!=set(range(1,EXPANDED_SPECIAL_COUNT+1)): raise RuntimeError("catalog Special IDs are not exact 1..2983")
    for item_id,p in specials.items():
        if not str(p.get("Japanese") or "").strip(): raise RuntimeError(f"catalog Japanese display missing at {item_id}")
        if not p.get("JapaneseSearch"): raise RuntimeError(f"catalog Japanese search missing at {item_id}")
        if not str(p.get("ProductFit") or "").strip(): raise RuntimeError(f"catalog product fit missing at {item_id}")
        browse=p.get("SpecialBrowseV2")
        if not isinstance(browse,dict): raise RuntimeError(f"catalog Browse v2 missing at {item_id}")
        status=browse.get("Status"); has_route=bool(browse.get("KindId") or browse.get("BodySiteIds") or browse.get("ThemeIds"))
        if status not in STATUS_NAMES: raise RuntimeError(f"catalog unknown Browse v2 status at {item_id}: {status!r}")
        if status in (0,1) and not has_route: raise RuntimeError(f"catalog browsable Special has no v2 route at {item_id}")
        if status in (2,3,4) and has_route: raise RuntimeError(f"catalog non-browse Special still has v2 route at {item_id}")
    statuses=Counter(STATUS_NAMES[specials[i]["SpecialBrowseV2"]["Status"]] for i in specials)
    if dict(statuses)!=EXPECTED_STATUS: raise RuntimeError(f"catalog Browse v2 status distribution drift: {dict(statuses)}")
    promoted=range(PROMOTION_START_ID,EXPANDED_SPECIAL_COUNT+1)
    if any(specials[i]["SpecialBrowseV2"]["Status"]!=1 for i in promoted): raise RuntimeError("promoted Special rows are not all HumanResolved")
    base_surfaces=set()
    for i in range(1,BASE_SPECIAL_COUNT+1):
        p=specials[i]
        base_surfaces.update(str(v) for v in [p.get("English"),p.get("Canonical"),*(p.get("Aliases") or [])] if v)
    promoted_surfaces=set()
    for i in promoted:
        p=specials[i]
        row_surfaces={str(v) for v in [p.get("English"),p.get("Canonical"),*(p.get("Aliases") or [])] if v}
        overlap=row_surfaces & base_surfaces
        if overlap: raise RuntimeError(f"promoted canonical/alias overlaps base Special at {i}: {sorted(overlap)}")
        collision=row_surfaces & promoted_surfaces
        if collision: raise RuntimeError(f"promoted canonical/alias collision at {i}: {sorted(collision)}")
        promoted_surfaces.update(row_surfaces)
    return {"special":len(specials),"japanese_display":len(specials),"japanese_search":len(specials),"browse_v2":len(specials),"product_fit_catalog":len(specials),"status":dict(statuses),"promoted_human_resolved":PROMOTION_COUNT,"promoted_base_surface_overlap":0}

def stale_candidates(root:Path)->list[dict[str,object]]:
    number=re.compile(r"(?<![A-Za-z0-9_])(?:2788|2,788)(?![A-Za-z0-9_])")
    allowed=re.compile(r"\bBaseSpecialCount\s*=\s*(?:2788|2,788)\b")
    out=[]
    for rel in ACTIVE_2788_SCAN:
        path=root/rel
        if not path.is_file(): continue
        for n,line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(),1):
            if number.search(line) and not allowed.search(line): out.append({"path":rel.as_posix(),"line":n,"text":line.strip()})
    return out

def audit(root:Path,catalog:Path|None)->dict[str,object]:
    promotion,a=check_authority(root); b=check_sidecars(root,promotion); stale=stale_candidates(root)
    result={"issue":97,"read_only":True,"user_db_opened":False,"base_special_count":BASE_SPECIAL_COUNT,"expanded_special_count":EXPANDED_SPECIAL_COUNT,"promotion_range":[PROMOTION_START_ID,EXPANDED_SPECIAL_COUNT],"promotion_count":PROMOTION_COUNT,"counts":{**a,**b},"catalog":check_catalog(catalog) if catalog else None,"stale_2788_candidates":stale,"human_audit_candidates":stale}
    result["ok"]=not stale; result["full_catalog_checked"]=catalog is not None
    return result

def main()->int:
    parser=argparse.ArgumentParser(description="Issue #97 read-only Special quality audit")
    parser.add_argument("--catalog",type=Path,help="optional built catalog.db for full 2,983-row verification")
    args=parser.parse_args(); root=Path(__file__).resolve().parents[2]
    try: result=audit(root,args.catalog)
    except Exception as e:
        print(json.dumps({"ok":False,"issue":97,"error":str(e)},ensure_ascii=False,sort_keys=True)); return 1
    print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)); return 0 if result["ok"] else 2

if __name__=="__main__": sys.exit(main())
