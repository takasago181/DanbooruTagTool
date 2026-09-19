#!/usr/bin/env python3
"""Summarize Issue #70 second-stage external resolution progress.

The primary semantic audit is immutable.  Rows initially deferred as
NEEDS_EXTERNAL_CHECK are closed by root-level ``external_resolution_*.csv``
overlays.  This script reports the effective external queue without mutating
production translation/source data.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import shutil
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'docs/issue70/audit'
OUT = AUDIT / 'EXTERNAL_PROGRESS_LIVE.json'
TMP = ROOT / 'artifacts/issue70-external-progress'
OVERLAY_PREFIX = 'external_resolution_'
FINAL = {'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH'}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def census_rows():
    if TMP.exists(): shutil.rmtree(TMP)
    subprocess.run([
        sys.executable,
        str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),
        '--out', str(TMP), '--sample-per-category', '300'
    ], cwd=ROOT, check=True)
    return read_csv(TMP/'audit_ledger_template.csv')


def decision(r):
    return (
        (r.get('audit_verdict') or '').strip(),
        (r.get('proposed_display_ja') or '').strip(),
        (r.get('proposed_search_ja') or '').strip(),
    )


def main():
    ledger = census_rows()
    by_id = {r['row_id']: r for r in ledger}

    # Initial external queue comes only from primary (non-overlay) audit files.
    external_ids = {}
    for p in sorted(AUDIT.glob('*.csv')):
        if p.name.startswith(OVERLAY_PREFIX) or 'diagnostic' in p.name:
            continue
        try: rows = read_csv(p)
        except Exception: continue
        for r in rows:
            rid=(r.get('row_id') or '').strip()
            if rid in by_id and (r.get('audit_verdict') or '').strip()=='NEEDS_EXTERNAL_CHECK':
                l=by_id[rid]
                external_ids[rid] = {
                    'category': l.get('category_name') or '',
                    'canonical_tag': l.get('canonical_tag') or r.get('canonical_tag') or '',
                    'post_count': int(l.get('post_count') or r.get('post_count') or 0),
                    'display_ja': l.get('display_ja') or r.get('display_ja') or '',
                    'search_ja': l.get('search_ja') or r.get('search_ja') or '',
                    'translation_note': l.get('translation_note') or r.get('translation_note') or '',
                    'primary_source_file': p.name,
                }

    observations=defaultdict(list)
    for p in sorted(AUDIT.glob(f'{OVERLAY_PREFIX}*.csv')):
        try: rows=read_csv(p)
        except Exception: continue
        for r in rows:
            rid=(r.get('row_id') or '').strip(); v=(r.get('audit_verdict') or '').strip()
            if rid not in external_ids or v not in FINAL: continue
            observations[rid].append({
                'audit_verdict':v,
                'proposed_display_ja':(r.get('proposed_display_ja') or '').strip(),
                'proposed_search_ja':(r.get('proposed_search_ja') or '').strip(),
                'source_file':p.name,
            })

    resolved={}; conflicts=[]; duplicate_same=0; superseded=0
    for rid, entries in observations.items():
        ds={decision(e) for e in entries}
        if len(ds)==1:
            resolved[rid]=entries[-1]
            if len(entries)>1: duplicate_same += len(entries)-1
        else:
            # Distinct external decisions are never silently overwritten.
            conflicts.append({'row_id':rid,'canonical_tag':external_ids[rid]['canonical_tag'],'entries':entries})

    remaining=[rid for rid in external_ids if rid not in resolved]
    remaining.sort(key=lambda rid:(-external_ids[rid]['post_count'], rid))
    by_v=Counter(v['audit_verdict'] for v in resolved.values())
    by_cat_res=Counter(external_ids[r]['category'] for r in resolved)
    by_cat_rem=Counter(external_ids[r]['category'] for r in remaining)

    # Primary conflict count is still useful as a guard, but effective external
    # closure is governed by this second-stage overlay view.
    primary_conflicts=0
    progress=AUDIT/'PROGRESS_LIVE.json'
    if progress.exists():
        try: primary_conflicts=int(json.loads(progress.read_text(encoding='utf-8')).get('conflicted_unique_rows',0))
        except Exception: pass

    top=[]
    for rid in remaining[:30]:
        x=external_ids[rid]
        top.append({'row_id':rid, **x})

    result={
        'format_version':3,
        'issue':70,
        'production_modified':False,
        'primary_rows_with_observations':len(by_id),
        'effective_primary_rows':len(by_id),
        'primary_conflicted_rows':primary_conflicts,
        'primary_defer_markers_suppressed_by_concrete':0,
        'initial_external_rows':len(external_ids),
        'resolved_external_rows':len(resolved),
        'remaining_external_rows':len(remaining),
        'conflicted_external_rows':len(conflicts),
        'duplicate_same_decision_rows':duplicate_same,
        'superseded_external_rows':superseded,
        'resolved_verdict_counts':dict(sorted(by_v.items())),
        'resolved_by_category':dict(sorted(by_cat_res.items())),
        'remaining_by_category':dict(sorted(by_cat_rem.items())),
        'top_remaining':top,
        'primary_conflicts':[],
        'conflicts':conflicts,
        'next_step':'resolve only effective NEEDS_EXTERNAL_CHECK rows from the root external-resolution overlay queue; keep production read-only until external closure',
    }
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if not conflicts and primary_conflicts==0 else 2


if __name__=='__main__':
    raise SystemExit(main())
