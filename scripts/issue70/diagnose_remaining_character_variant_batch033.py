#!/usr/bin/env python3
"""Diagnose why remaining Issue #70 Character variant/parenthetical rows missed batch028.
Diagnostic only; no verdicts or production changes.
"""
from __future__ import annotations
import csv,json,re,shutil,subprocess,sys,unicodedata
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-batch033-diagnostic'
OUT=AUDIT/'character_remaining_variant_batch033_diagnostic.json'
NOTES={'parenthetical candidate does not map cleanly to a copyright disambiguator','variant/form rendering plausible but not independently verified'}
JA=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]'); PAREN=re.compile(r'_\(([^()]*)\)')
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def done():
    s=set()
    for p in AUDIT.glob('*.csv'):
        if 'diagnostic' in p.name: continue
        try: rows=read(p)
        except Exception: continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID and (r.get('row_id') or '').strip():s.add(r['row_id'].strip())
    return s
def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read(TMP/'audit_ledger_template.csv')
def norm(v):return ' '.join(unicodedata.normalize('NFKC',v or '').strip().lower().replace('_',' ').replace('・',' ').split())
def split(v):return [x.strip() for x in (v or '').split('|') if x.strip()]
def has_stronger(r):return any(JA.search(r.get(f) or '') for f in ('existing_display_ja','existing_search_ja','verified_aliases','source_aliases'))
def parens(tag):return [x.strip() for x in PAREN.findall(tag or '') if x.strip()]
def variant_tokens(canonical,base):
    c=parens(canonical); b=Counter(parens(base)); out=[]
    for x in c:
        if b[x]:b[x]-=1
        else:out.append(x)
    return out
def reason(r):
    base=(r.get('family_base_display_ja') or '').strip(); base_can=(r.get('family_base_canonical') or '').strip()
    cur=(r.get('display_ja') or '').strip(); cand={norm(x) for x in split(r.get('existing_candidate_ja') or '')}
    rs=[]
    if not base or not base_can or not JA.search(base):rs.append('NO_VERIFIED_JA_BASE')
    if has_stronger(r):rs.append('HAS_STRONGER_JA_EVIDENCE')
    if not cur:rs.append('EMPTY_DISPLAY')
    elif norm(cur) not in cand:rs.append('DISPLAY_NOT_RAW_CANDIDATE')
    if base_can and not variant_tokens(r.get('canonical_tag') or '',base_can):rs.append('NO_CANONICAL_VARIANT_DELTA')
    return '+'.join(rs) if rs else 'BATCH028_ELIGIBLE_UNEXPECTED'
def main():
    audited=done(); groups=defaultdict(list)
    for r in census():
        if r.get('row_id') in audited or r.get('category_name')!='Character':continue
        if r.get('translation_status')!='REVIEW_REQUIRED' or (r.get('translation_note') or '') not in NOTES:continue
        rr=reason(r)
        o={k:r.get(k) or '' for k in ['row_id','canonical_tag','post_count','display_ja','search_ja','translation_note','risk_flags','source_aliases','verified_aliases','existing_display_ja','existing_search_ja','existing_candidate_ja','existing_rejected_ja','related_copyright_top1','related_copyright_top1_coverage','family_base_canonical','family_base_display_ja']}
        groups[rr].append(o)
    total=sum(map(len,groups.values())); assert total==1199,total
    data={'format_version':1,'issue':70,'production_modified':False,'population':total,'groups':[]}
    for k,rows in sorted(groups.items(),key=lambda kv:(-len(kv[1]),kv[0])):
        rows.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
        data['groups'].append({'reason':k,'count':len(rows),'samples':rows[:12]})
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'population':total,'groups':[(g['reason'],g['count']) for g in data['groups']],'production_modified':False},ensure_ascii=False))
if __name__=='__main__':main()
