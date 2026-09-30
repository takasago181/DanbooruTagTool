"""Freeze read-only corpus inputs for a reproducible textbook view."""
import csv, hashlib, json, subprocess, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA = '9142071e6b10a456a89cb8594ae62d95a07a50b2'
MAIN = '4e85099737e0f01adbd2dea9640abded9af20638'
def git(*args):
    return subprocess.check_output(['git', *args])

if __name__ == '__main__':
    paths = git('ls-tree', '-r', '--name-only', SHA, 'docs/knowledge').decode().splitlines()
    inventory = []
    source_records = {}
    for path in paths:
        raw = git('show', f'{SHA}:{path}')
        category = '複数資料を統合'
        if '/current/' in path: category = '直接利用可能・判定正本'
        if '/catalog/' in path: category = '直接利用可能・解説'
        if any(x in path for x in ['LEGACY', 'EVOLUTION', 'REASSESSMENT', 'WAI17_LOCAL']): category = 'HISTORICAL・現行判定と照合'
        if 'HOLD' in path: category = 'HOLD・削除せず参照'
        if any(x in path for x in ['SELF_AUDIT', 'ASSET_INVENTORY', '10_FILE_MAP', 'INDEX']): category = '重複入口・本文への転載不要'
        if 'evaluator_coverage' in path: category = '補助監査・詳細は原資料へ'
        inventory.append({'path':path,'sha256':hashlib.sha256(raw).hexdigest(),'classification':category})
        if path.endswith('.md'):
            print(path, ' | '.join(l.lstrip('# ') for l in raw.decode('utf-8-sig').splitlines() if l.startswith('## ')))
            content = raw.decode('utf-8-sig')
            for match in re.finditer(r'\*\*(S-[A-Z0-9-]+)[^*\n]*\*\*',content):
                end = content.find('\n**S-',match.end())
                block=content[match.end():end if end>=0 else len(content)]
                url=re.search(r'- URL: (https?://[^\s<>]+)',block)
                source_records.setdefault(match.group(1),{'registry_path':path,'source_url':url.group(1).rstrip(').') if url else None,'corpus_sha':SHA})
    for name in ['CLAIM_REGISTRY.csv','VERSION_FRESHNESS_LEDGER.csv','HOLD_CONFLICT_REGISTER.md']:
        (ROOT/'references'/name).write_bytes(git('show',f'{SHA}:docs/knowledge/current/{name}'))
    (ROOT/'references'/'CORPUS_INVENTORY.json').write_text(json.dumps({'corpus_sha':SHA,'main_sha':MAIN,'files':inventory},ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'references'/'SOURCE_RECORDS.json').write_text(json.dumps(source_records,ensure_ascii=False,indent=2),encoding='utf-8')
