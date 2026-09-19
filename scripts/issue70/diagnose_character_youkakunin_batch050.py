#!/usr/bin/env python3
"""Classify remaining Issue #70 Character rows whose translation_note is '要確認'.
Diagnostic only; production data is never modified.
"""
from __future__ import annotations
import csv,json,re,shutil,subprocess,sys,unicodedata
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-batch050'
OUT=AUDIT/'character_youkakunin_batch050_diagnostic.json'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
JA=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]')
NOTE='要確認'
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(v):return ' '.join(unicodedata.normalize('NFKC',v or '').strip().lower().replace('_',' ').replace('・',' ').split())
def terms(v):return [x.strip() for x in (v or '').split('|') if x.strip()]
def audited():
    s=set()
    for p in AUDIT.glob('*.csv'):
        if 'diagnostic' in p.name:continue
        try:rows=read(p)
        except Exception:continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID and (r.get('row_id') or '').strip():s.add(r['row_id'].strip())
    return s
def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read(TMP/'audit_ledger_template.csv')
def main():
    done=audited(); rows=[]; buckets=Counter(); signatures=Counter(); bucket_samples=defaultdict(list)
    strong_fields=('existing_display_ja','existing_search_ja','verified_aliases','source_aliases')
    fields=['row_id','canonical_tag','post_count','display_ja','search_ja','translation_status','translation_note','risk_flags','source_aliases','verified_aliases','existing_display_ja','existing_search_ja','existing_candidate_ja','existing_rejected_ja','related_copyright_top1','related_copyright_top1_coverage','family_base_canonical','family_base_display_ja']
    for r in census():
        if r.get('row_id') in done or r.get('category_name')!='Character':continue
        if r.get('translation_status')!='REVIEW_REQUIRED' or (r.get('translation_note') or '')!=NOTE:continue
        disp=(r.get('display_ja') or '').strip(); nd=norm(disp)
        strong=[]
        for f in strong_fields:
            for t in terms(r.get(f) or ''):
                if JA.search(t):strong.append((f,t))
        exact=[(f,t) for f,t in strong if norm(t)==nd]
        raw=[t for t in terms(r.get('existing_candidate_ja') or '') if JA.search(t)]
        raw_exact=any(norm(t)==nd for t in raw)
        rejected=[t for t in terms(r.get('existing_rejected_ja') or '') if JA.search(t)]
        rejected_exact=any(norm(t)==nd for t in rejected)
        flags={x.strip() for x in (r.get('risk_flags') or '').split('|') if x.strip()}
        if rejected_exact:bucket='DISPLAY_MATCHES_REJECTED'
        elif exact and not ({'DUPLICATE_DISPLAY_WITHIN_CATEGORY','DISAMBIGUATOR_NOT_VISIBLE','VARIANT_DISPLAY_MISSING_BASE_IDENTITY','RAW_TAG_SYNTAX_IN_DISPLAY'} & flags):bucket='EXACT_STRONG_NO_IDENTITY_FLAG'
        elif exact:bucket='EXACT_STRONG_WITH_IDENTITY_FLAG'
        elif strong:bucket='STRONG_JA_EXISTS_BUT_DISPLAY_DIFFERS'
        elif raw_exact and (r.get('family_base_display_ja') or '').strip():bucket='RAW_ONLY_WITH_FAMILY_BASE'
        elif raw_exact:bucket='RAW_ONLY_NO_FAMILY_BASE'
        elif JA.search(disp):bucket='JA_DISPLAY_NO_JA_EVIDENCE'
        else:bucket='NON_JA_DISPLAY'
        buckets[bucket]+=1; signatures[(bucket,'|'.join(sorted(flags)))]+=1
        item={k:r.get(k,'') for k in fields}; item.update({'diagnostic_bucket':bucket,'strong_exact_terms':' | '.join(f'{f}:{t}' for f,t in exact),'strong_ja_terms':' | '.join(f'{f}:{t}' for f,t in strong),'raw_candidate_exact':raw_exact,'rejected_exact':rejected_exact})
        rows.append(item)
        if len(bucket_samples[bucket])<12:bucket_samples[bucket].append(item)
    rows.sort(key=lambda r:(-int(r.get('post_count') or 0),r['row_id']))
    sig=[{'bucket':b,'risk_flags':f,'count':c} for (b,f),c in signatures.most_common()]
    data={'format_version':1,'issue':70,'production_modified':False,'population':len(rows),'bucket_counts':dict(buckets),'top_signatures':sig,'samples':dict(bucket_samples),'rows':rows}
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'population':len(rows),'bucket_counts':dict(buckets),'production_modified':False})
if __name__=='__main__':main()
