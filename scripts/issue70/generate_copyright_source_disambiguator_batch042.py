#!/usr/bin/env python3
"""Generate Issue #70 Copyright audit batch 042 from batch041 safe diagnostics.

Use only a single unique Japanese disambiguated display already present in
existing_search_ja. Preserve the former display/search terms for discoverability.
Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'
SRC=AUDIT/'copyright_source_disambiguator_batch041_diagnostic.json'
OUT=AUDIT/'copyright_source_disambiguator_fix_batch042.csv'
def terms(v):return [x.strip() for x in (v or '').split('|') if x.strip()]
def main():
    d=json.loads(SRC.read_text(encoding='utf-8')); rows=d['safe_samples']
    assert len(rows)==d['safe_unique_rows']==6
    out=[]
    for r in rows:
        proposed=r['candidate_display_ja'].strip(); old=r['display_ja'].strip()
        st=[]
        for x in [proposed,old,*terms(r.get('existing_search_ja') or ''),*terms(r.get('search_ja') or '')]:
            if x and x not in st:st.append(x)
        out.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r['post_count'],
          'display_ja':old,'search_ja':r.get('search_ja') or '','existing_search_ja':r.get('existing_search_ja') or '',
          'risk_flags':r.get('risk_flags') or '','audit_verdict':'FIX_BOTH','proposed_display_ja':proposed,
          'proposed_search_ja':' | '.join(st),'reason_code':'SOURCE_BACKED_UNIQUE_COPYRIGHT_DISAMBIGUATOR','confidence':'HIGH',
          'evidence_refs':'existing_search_ja exact source-backed disambiguator; candidate unique across Copyright displays/candidates',
          'audit_note':'既存sourceの日本語検索語に明示的な区別表記があり、その候補がCopyright内で一意。表示へ昇格し旧表示も検索語に保持。',
          'approval_status':'PROPOSED'})
    fields=list(out[0].keys())
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    print({'rows':len(out),'fix_both':len(out),'production_modified':False})
if __name__=='__main__':main()
