#!/usr/bin/env python3
"""Generate Issue #70 Character audit batch 013.

For REVIEW_REQUIRED Character rows whose Japanese candidate is short/kana-only
and ambiguous only because the work context is invisible, append the related
Copyright display to make the identity usable. Rows with a known
VARIANT_DISPLAY_MISSING_BASE_IDENTITY signal are excluded; those need variant
identity repair instead.

Copyright context prefers already-proposed semantic audit corrections, then
falls back to the frozen runtime Copyright display.
Proposal-only: production data is never modified.
"""
from __future__ import annotations

import csv
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "docs/issue70/audit"
TMP = ROOT / "artifacts/issue70-semantic-audit-v3-batch013"
OUT = AUDIT_DIR / "character_context_disambiguation_batch013.csv"
RUNTIME = ROOT / "docs/issue70/data/runtime/issue70_translation_results.csv"
NOTE = "short kana-only candidate is too ambiguous without contextual search evidence"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer=csv.DictWriter(fh, fieldnames=fields); writer.writeheader(); writer.writerows(rows)


def prior_ids() -> set[str]:
    ids=set()
    for path in AUDIT_DIR.glob('*.csv'):
        if path.name == OUT.name: continue
        try: rows=read_csv(path)
        except Exception: continue
        for row in rows:
            if row.get('row_id') and row.get('audit_verdict'): ids.add(row['row_id'].strip())
    return ids


def run_census() -> Path:
    if TMP.exists(): shutil.rmtree(TMP)
    subprocess.run([sys.executable, str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'), '--out', str(TMP), '--sample-per-category', '300'], cwd=ROOT, check=True)
    return TMP/'audit_ledger_template.csv'


def preferred_copyright_displays() -> dict[str,str]:
    result={}
    # Frozen runtime baseline first.
    for row in read_csv(RUNTIME):
        if row.get('category') == '3' and row.get('canonical_tag'):
            result[row['canonical_tag']] = (row.get('display_ja') or '').strip()
    # Audit proposals override baseline where available.
    for path in sorted(AUDIT_DIR.glob('*.csv')):
        if path.name == OUT.name: continue
        try: rows=read_csv(path)
        except Exception: continue
        for row in rows:
            canonical=(row.get('canonical_tag') or '').strip()
            proposed=(row.get('proposed_display_ja') or '').strip()
            verdict=(row.get('audit_verdict') or '').strip()
            if canonical and proposed and verdict in {'FIX_DISPLAY','FIX_BOTH'}:
                # Only use it as Copyright context if the canonical exists in the runtime Copyright map.
                if canonical in result: result[canonical]=proposed
    return result


def has_brackets(value: str) -> bool:
    return any(ch in (value or '') for ch in '()（）[]【】')


def main() -> int:
    audited=prior_ids(); ledger=read_csv(run_census()); cp=preferred_copyright_displays()
    rows=[]
    for row in ledger:
        if row.get('row_id') in audited: continue
        if row.get('category_name') != 'Character' or row.get('translation_status') != 'REVIEW_REQUIRED': continue
        if row.get('translation_note') != NOTE: continue
        flags=row.get('risk_flags') or ''
        if 'VARIANT_DISPLAY_MISSING_BASE_IDENTITY' in flags: continue
        if not ('DUPLICATE_DISPLAY_WITHIN_CATEGORY' in flags or 'DISAMBIGUATOR_NOT_VISIBLE' in flags): continue
        display=(row.get('display_ja') or '').strip()
        if not display or has_brackets(display): continue
        related=(row.get('related_copyright_top1') or '').strip()
        context=(cp.get(related) or '').strip()
        if not related or not context: continue
        proposed=f"{display}（{context}）"
        if proposed == display: continue
        rows.append({
            'row_id':row['row_id'],'canonical_tag':row['canonical_tag'],'post_count':row['post_count'],
            'display_ja':display,'related_copyright_top1':related,'copyright_display_context':context,
            'audit_verdict':'FIX_DISPLAY','proposed_display_ja':proposed,'proposed_search_ja':'',
            'reason_code':'ADD_COPYRIGHT_CONTEXT_TO_AMBIGUOUS_SHORT_CHARACTER_NAME','confidence':'HIGH',
            'evidence_refs':'current Japanese candidate + related_copyright_top1 + audited/frozen Copyright display',
            'audit_note':'短い日本語名そのものは保持し、同名衝突/不可視disambiguatorだけを作品名で解消。variant identity欠落行は別laneへ除外。',
            'approval_status':'PROPOSED',
        })
    rows.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    write_csv(OUT,rows,['row_id','canonical_tag','post_count','display_ja','related_copyright_top1','copyright_display_context','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status'])
    print({'rows':len(rows),'production_modified':False})
    return 0

if __name__=='__main__': raise SystemExit(main())
