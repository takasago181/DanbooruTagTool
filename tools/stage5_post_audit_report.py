"""Finish audit tables, validate accounting, and render the audit report."""
import csv
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.stage5_post_audit import OUT, save, table, fingerprints
from danbooru_tag_tool.runtime_index import RuntimeIndex

def main():
    s=json.loads((OUT/'mapping_summary.json').read_text(encoding='utf-8'))
    rows=list(csv.DictReader((OUT/'all_source_tags.csv').open(encoding='utf-8-sig')))
    special=list(csv.DictReader((OUT/'special_impact.csv').open(encoding='utf-8-sig')))
    x=RuntimeIndex(ROOT/'data/runtime_index',verify_hashes=True)
    assert len(rows)==len(x.tags)==103198
    assert sum(v['unique_tags'] for v in s['categories'].values())==103198
    assert sum(v['occurrences'] for v in s['categories'].values())==354571220
    assert np.array_equal(np.diff(x.tag_post_offsets),x.runtime_global_counts)
    assert int(x.post_tag_offsets[-1])==354571220
    from collections import defaultdict
    from danbooru_tag_tool.normalization import normalize_lookup
    normalized=defaultdict(list)
    for tag in x.tags: normalized[normalize_lookup(tag)].append(tag)
    collisions={key:tags for key,tags in normalized.items() if len(tags)>1}
    save('source_normalization_collisions.json',collisions)
    assert not collisions
    groups=defaultdict(list)
    for r in rows:
        if r['target']: groups[r['target']].append(r['source_tag'])
    all_counts=[]
    duplicate_posts=set()
    duplicate_entries=0
    for t,sources in groups.items():
        raw=int(x.runtime_global_counts[x.tag_id(t)]) if t in x.tag_to_id else 0
        summed=sum(int(x.runtime_global_counts[x.tag_id(v)]) for v in sources)
        if len(sources)>1:
            ords,freq=np.unique(np.concatenate([x.postings(v) for v in sources]),return_counts=True)
            union=len(ords)
            for ordinal in ords[freq>1]:
                a,b=x.post_tag_offsets[int(ordinal):int(ordinal)+2]
                reverse={x.tags[int(i)] for i in x.post_tag_ids[int(a):int(b)]}
                n=len(reverse.intersection(sources)); assert n>=2
                duplicate_posts.add(int(ordinal)); duplicate_entries+=n-1
        else: union=summed
        all_counts.append(dict(canonical=t,source_tags=json.dumps(sources),raw_global_count=raw,
                               summed_source_counts=summed,union_global_count=union,added_posts=union-raw))
    assert len(duplicate_posts)==s['posts_with_any_canonical_duplicate']
    assert duplicate_entries==s['duplicate_entries']
    table('all_canonical_global_counts.csv',all_counts)
    threshold={str(n):len({r['canonical'] for r in special if int(r['category'])==0 and int(r['raw_global_count'])>n}) for n in [100000,500000,1000000]}
    absent=[r for r in special if int(r['merged_global_count'])==0]
    save('validation.json',dict(accounting_pass=True,posting_lengths_equal_global_counts=True,
        duplicate_posts_reverse_checked=len(duplicate_posts),duplicate_entries_reverse_checked=duplicate_entries,
        threshold_unique_special_canonicals=threshold,still_missing_special_entries=absent,
        protected_hashes_unchanged=fingerprints()==json.loads((OUT/'input_hashes_before.json').read_text(encoding='utf-8'))))
    assert json.loads((OUT/'validation.json').read_text(encoding='utf-8'))['protected_hashes_unchanged']
    cases=[json.loads(p.read_text(encoding='utf-8')) for p in sorted(OUT.glob('workload_[0-9][0-9].json'))]
    assert len(cases)==len(json.loads((OUT/'workload_plan.json').read_text(encoding='utf-8')))==12
    save('special_workloads.json',cases)
    lines=['# Stage 5 追加監査 — 2026-09-05','',
        '**再判定: APPROVE WITH CONDITIONS。** raw sourceの双方向indexは保持可能。ただしcanonical query/countの意味統一と、大規模Specialの待ち時間対策は次の承認条件として残す。Stage 6、production rebuild、Counter最適化は実施していない。','',
        '## A. 全source General tagの対応','',
        '既存TagKnowledgeCore.resolve_exactとverified alias CSVを使用。literal canonicalを最優先し、次にnormalized canonical、aliasを評価。曖昧候補は統合しない。Semantic/Japaneseの概念一致だけでsource tagをcanonicalへ変換しない。今回normalized canonicalのみの一意一致も0件であり、下表の第5分類に一意一致は混入していない。','',
        '指定6分類に含まれないcurrent non-General canonical完全一致を第7分類として追加した。これはsource Generalという分類とcurrent dictionary分類の差であり、aliasではない。','',
        '| 分類 | unique tags | runtime occurrences | 全entries比 | 1語以上含むposts |','|---|---:|---:|---:|---:|']
    labels=['1. exact current General canonical','2. unique alias → current General','3. unique alias → current non-General','4. ambiguous alias','5. normalization衝突/曖昧','6. runtime-only','7. exact current non-General（追加）']
    for label,(_,v) in zip(labels,s['categories'].items()):
        lines.append(f"| {label} | {v['unique_tags']:,} | {v['occurrences']:,} | {v['entry_percent']:.6f}% | {v['posts']:,} |")
    lines += ['', '合計103,198語 / 354,571,220 entries。post列は分類間で重複するため加算しない。母集団は11,218,362 posts。今回のambiguous/normalizationが0件でも、辞書全体に曖昧aliasが存在しないことは意味しない。canonical exactにshadowされたaliasは優先順位どおり不採用。', '',
        '前回「72,607語未解決」はGeneral canonical完全一致以外という意味だった。alias 102語とnon-General完全一致14語を除くとruntime-onlyは72,491語。語数は多いが出現比は0.268998%、それを含むpostは820,086（約7.31%）。少数出現だから無視してよいとは解釈しない。', '',
        '代表例: alias `china_dress → qipao` 73,589回、`holding_shoes → holding_unworn_shoes` 4,197回。runtime-only `eyebrows` 37,203、`looking_away` 33,968、`uniform` 24,926。Semantic一致だけの65語（例 `areolae`）もruntime-onlyのまま。non-General完全一致例 `listen!!` 511回。分類ごとの最大50件はmapping_summary.json、全件はall_source_tags.csvに保存。','',
        '## Canonical統合の影響','',
        f"同じcurrent canonicalへ複数source tagが対応するのは{s['merge_groups']}グループ、source tag合計{s['merge_source_tags']}語。うち{s['groups_with_same_post_duplicates']}グループで同一post重複がある。重複postの和集合は{s['posts_with_any_canonical_duplicate']} posts、単純加算が余計に数えるentriesは{s['duplicate_entries']}。全重複postはpost→tags側でも確認した。",'',
        'global countは各source postingの和集合の件数。全current対応canonicalのraw count / source count合計 / union count / 増分をall_canonical_global_counts.csv、複数sourceグループと実post例をcanonical_merges.csvに保存。単独aliasだけが対応しcanonicalのraw postingがないケースも全件表に含めた。','',
        '| canonical | raw count | 統合後union count | 増分 |','|---|---:|---:|---:|']
    for r in sorted(all_counts,key=lambda r:-r['added_posts'])[:8]:
        lines.append(f"| `{r['canonical']}` | {r['raw_global_count']:,} | {r['union_global_count']:,} | {r['added_posts']:,} |")
    lines += ['',f"Specialはresolved **2,443エントリ / distinct canonical 1,724語**。2,443はunique canonical数ではない。統合で変わるのは{s['special_changed_entries']}エントリ / {s['special_changed_canonicals']} canonical。rawで0件の12エントリ中4エントリ（2 canonical）が回復し、8エントリは対応sourceなしのまま。",'',
        '| 影響するSpecial canonical | raw | union |','|---|---:|---:|']
    changed={r['canonical']:r for r in special if int(r['added_posts'])}
    for t,r in sorted(changed.items()): lines.append(f"| `{t}` | {r['raw_global_count']} | {r['merged_global_count']} |")
    lines += ['', '全Special ID・原語・日本語・対応source・増分はspecial_impact.csvに保存。current dictionary post_countはこの統計計算に使用していない。General-only source列からcurrent non-Generalへ対応するcountは、そのcanonicalの全カテゴリpost数を網羅する保証がないため別扱いが必要。','',
        '## A/B/C案の評価（提案のみ）','',
        '| 案 | 評価 |','|---|---|',
        '| A: raw ID維持＋canonical mapping layer | **推奨**。既存indexと証拠post/source名を保ち、少数のalias差分を明示できる。dictionary/alias hashと解決方針versionを対応表に固定する。 |',
        '| B: build時collapse | 現時点で不要。raw identityを失うか別保存が必要になり、再buildも必要。General/current非Generalの扱いを未決定のまま固定すべきでない。 |',
        '| C: raw exactのみ＋未対応を表示 | 暫定監査閲覧には最小だが、回復可能なSpecialを0件扱いする問題が残り完成版には不十分。 |','',
        'Aの意味契約: 1 canonical内では対応source postingをOR、異なるCore canonical間ではAND。candidateもpostごとにcanonicalで重複除去し、global/base/coすべてに同一mappingを適用する。raw co_countを表示名だけ変えて加算してはいけない。曖昧aliasは保留し、raw-onlyとresolved canonicalのnamespaceを区別する。これは設計提案でありruntime APIは変更していない。','',
        '## B. 実Special workload','',
        f"Generalかつraw postingのあるresolved Specialから選定。unique canonicalでbase>100,000は{threshold['100000']}語、>500,000は{threshold['500000']}語、>1,000,000は{threshold['1000000']}語。各閾値を超える実条件を測定した。最小の正のbaseは11であり、base=1を捏造していない。",'',
        '単一6条件＋2/3/5 Special各2条件、計12条件。複数Specialは上位100 canonicalから固定seed 20260905で各60組抽出し、base≈100/10,000に近い組を選定。全語に実Special IDを記録し、同一canonicalを別Specialとして水増ししない。これは実在語による負荷試験であり、人間のCore選択分布を代表する利用ログではない。','',
        '条件ごとに新しいprocessを起動し、TagKnowledgeCoreや対応監査のメモリを持ち込まない。1回warm-up後、ANDは15回、aggregate/totalはbase>100,000で5回、その他15回。p95はNumPy線形percentileで、5標本のtail推定は粗い。OS cacheはwarmの可能性があるためcold startとは呼ばない。totalはANDとaggregateをまとめて別に反復測定しており、各medianの単純和ではない。RSSは各条件内のaggregate反復終了直後のworking set。mmapのfile sizeやvirtual sizeではない。','',
        '| Special条件（canonical） | base | AND median/p95 ms | Aggregate median/p95 ms | Total median/p95 ms | aggregate後RSS MiB |','|---|---:|---:|---:|---:|---:|']
    for c in cases:
        def pair(field): return f"{c[field]['median_ms']:.3f} / {c[field]['p95_ms']:.3f}"
        lines.append(f"| {' + '.join(c['tags'])} | {c['base_count']:,} | {pair('and')} | {pair('aggregation')} | {pair('total')} | {c['rss_after_aggregation_bytes']/2**20:.1f} |")
    large=max(cases,key=lambda c:c['base_count'])
    lines += ['',f"最大測定base {large['base_count']:,}ではAggregate median {large['aggregation']['median_ms']/1000:.2f}秒、total median {large['total']['median_ms']/1000:.2f}秒。現Counter実装は大きい核を選ぶ操作で秒単位の待ち時間になり、インタラクティブな完成版として即時更新を保証できない。論理双方向構造やpacked CSRの問題とCounter traversalの問題は分けて評価する。今回最適化していない。",'',
        '## 再判定と停止条件','',
        '**APPROVE WITH CONDITIONS**: raw統計基盤としてのStage 5は維持。無条件の製品完成承認ではない。条件は (1) Aのcanonical/raw namespaceと統計意味契約を監査承認する、(2) 大規模Specialの応答時間目標と集計改善を別依頼で検証する、(3) Forge同居の実測を行う。今回のデータでphysical format再設計やproduction再buildを正当化する根拠はない。Stage 6に進まず停止する。','',
        '## 作業報告（8項目）','',
        '1. 変更した項目: 追加監査のrunner・CSV/JSON・本報告のみ追加。',
        '2. 変更しなかった項目: production index全ファイル、runtime/knowledge/search実装、正本、Stage 2/5既存Decision、Stage 6。前後SHA-256一致を保存。',
        '3. 新規作成ファイル: tools/stage5_post_audit.py、tools/stage5_post_audit_report.py、benchmarks/stage5_post_audit/配下、docs/stage_reports/STAGE5_POST_AUDIT.md。',
        '4. バックアップ先: 既存ファイルの上書きなし。入力hash記録はbenchmarks/stage5_post_audit/input_hashes_*.json。',
        '5. 実施したテスト: 全分類合計・全posting長/global count一致・全重複postのreverse照合・既存index hash/構造検証・保護ファイル前後hash・既存pytest。',
        '6. テスト結果: 数値検算とhash検証PASS。既存pytest 61 passed in 8.73s。実行記録はbenchmarks/stage5_post_audit/pytest_result.txt。',
        '7. 未解決事項: 上記3条件、p95の標本数制約、未測定の他Special/実利用分布。raw Parquetの再走査は今回行わず、既存検証済みindex上の監査である。',
        '8. 次にChatGPTへ渡す情報: 本書、mapping_summary.json、all_source_tags.csv、all_canonical_global_counts.csv、canonical_merges.csv、special_impact.csv、special_workloads.json、validation.json。既存docs/decisions/DATA_SOURCE_DECISION.md / docs/architecture/INDEX_ARCHITECTURE_DECISION.mdと併読。','']
    (ROOT/'docs/stage_reports/STAGE5_POST_AUDIT.md').write_text('\n'.join(lines),encoding='utf-8')
    print('report complete; all accounting and hashes PASS')

if __name__=='__main__': main()
