"""One-command A5 PDF builder. No production/corpus mutations or downloads."""
import argparse, csv, html, json, re, subprocess, hashlib
from collections import Counter
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A5
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Spacer, KeepTogether
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

ROOT = Path(__file__).resolve().parent
SHA = '9142071e6b10a456a89cb8594ae62d95a07a50b2'
MAIN = '4e85099737e0f01adbd2dea9640abded9af20638'
REPO = 'https://github.com/takasago181/DanbooruTagTool'
INK = colors.HexColor('#16353d')
ACCENT = colors.HexColor('#206778')
W,H = A5
M = 31
CONTENT = W-2*M
FIGURES = {
 'pipeline':('図0-1 入力と実行のレイヤー',['意図 / Prompt文字列','Runtime / 構文と条件付け','Checkpoint + LoRA / 推論','画像 / 観察と記録']),
 'support':('図3-1 核と補助の分離',['Special / 意味の核','Support / 補う役割を確認','Manual Auxiliary / 明示選択','結果 / 核が保たれたか']),
 'prompt':('図4-1 構造を読む座標',['Subject / 誰を描くか','Action + Relation / 何をするか','Pose + Viewpoint / 配置と観察','Appearance + Setting / 調整']),
 'camera':('図7-1 配置とカメラを別に読む',['Pose / 身体の配置','Orientation / 身体の向き','Viewpoint / 観察位置','Frame + Visibility / 見える範囲']),
 'binding':('図8-1 非性的な関係の例',['成人A / 本を渡す主体','本 / 移動する対象','成人B / 受け取る相手','別途観察 / 手と本の帰属']),
 'experiment':('図8-2 概念条件の比較',['A_ONLY / Aを単独で観察','B_ONLY / Bを単独で観察','AB / 組み合わせを観察','差分 / bindingと競合を分ける']),
 'intervention':('図10-1 補助処理の証拠を分離',['Base画像 / まず保存','補助 / LoRA・control・修復','Final画像 / 別に保存','結果 / 改善と損傷を区別']),
 'failure':('図11-1 診断の入口',['1 記録 / 条件を復元できるか','2 Identity / 語形は正しいか','3 Unary / 単独で現れるか','4 Binding / 複合で崩れるか']),
}
GLOSSARY = [
 ('Prompt / プロンプト','意図を表す入力文字列。実行時の条件付けと同一ではない。',0),
 ('Tag / タグ','辞書の表面とidentityを持つ語。カンマ区切りすべてがタグとは限らない。',2),
 ('Canonical tag / 基準タグ','辞書の基準identity。日本語表示やモデルtriggerと分ける。',2),
 ('Alias / 別名','identityの対応。生成反応の同一性まで保証しない。',2),
 ('Implication / 包含関係','同義関係ではなく、タグ間の包含・階層関係。',2),
 ('Token / トークン','入力処理の単位。文字数、語数、タグ数と一致するとは限らない。',5),
 ('Weight / 強調','runtimeによる入力条件の強調。成功率や画像の強さの倍率ではない。',5),
 ('Negative Prompt / 負の条件','避ける方向への条件付け。目標の意味と衝突する場合がある。',6),
 ('Model / モデル','学習済みの生成機構。family/version/profileを区別する。',1),
 ('Checkpoint / 学習済み重み','モデルの実体となるファイル。名前だけでなくhashを記録する。',1),
 ('LoRA / 追加重み','学習済みadapter。strength、学習base、triggerを別に記録する。',10),
 ('Embedding / 埋め込み','学習済み入力表現。個別embeddingの有効性は本corpusで不足。',5),
 ('Sampler / 推論手順','生成の実行条件。モデルのprediction方式と合わせて扱う。',1),
 ('CFG / guidance設定','条件付けに関係する推論設定。profileを跨ぐ万能な値は示さない。',1),
 ('Seed / 乱数条件','比較の中心条件。単独で完全再現や信頼性を保証しない。',12),
 ('Special / 意味の核','選んだ概念のidentity。生成補助や分類の役割とは別。',3),
 ('Support / 補助知識','意味、geometry、visibility、resource、aesthetic、冗長性の役割を分ける。',3),
 ('Anti-support / 競合する補助','意味的に適合しても生成時に条件競合を生む補助。',3),
 ('Binding / 結び付け','属性・部位・対象が正しい主体へ帰属すること。',8),
 ('Actor / 主体','行為の主体。実験条件A/Bとは区別する。',8),
 ('Target / 対象','行為や関係の相手・対象。存在だけで正しい帰属を証明しない。',8),
 ('Body site / 身体部位','必要な部位条件。誰の部位かというownershipも別に見る。',9),
 ('Semantic bleed / 意味の混線','強い概念などの条件が別の属性・人物へ混線する観察上の呼称。',8),
 ('Caption / 学習説明','学習データの説明表面。人間の操作順や辞書ontologyとは別。',1),
 ('Danbooru / タグ情報源','canonical語義・Alias・Implicationを辿る主な意味情報源。',2),
 ('Frame / 画面範囲','何をどれだけ見せるか。viewpointや身体の向きとは別。',7),
 ('Viewpoint / 観察位置','カメラがどこから見るか。body orientationとは別。',7),
 ('Topology / 接続関係','要素がどう繋がっているか。要素の存在と区別する。',9),
 ('fellatio / 口を用いる性的接触','陰茎への口を用いる性的接触を指す名称。臨床的な語義参照。',9),
 ('paizuri / 乳房を用いる性的行為','乳房を用いる性的行為の名称。生成レシピは本書の対象外。',9),
 ('cum / 精液','精液を指す俗称。物質、出来事、付着状態を区別する。',9),
 ('cum_on_body / 身体表面への精液付着','Fluidの物質・付着先・状態を読むタグ表面の例。',9),
 ('sex / 性行為','性的行為を指す表面。主体・対象・詳細を単語だけから補わない。',9),
 ('anal / 肛門に関わる表面','文脈とcanonical情報を確認する。単語だけで全状況を断定しない。',9),
 ('vaginal / 腟に関わる表面','部位と行為、主体と対象の説明を別にする。',9),
 ('nipple / 乳頭','解剖学的名称。部位語だけでは行為や関係を表さない。',9),
 ('penis / 陰茎','解剖学的名称。部位とownershipを分ける。',9),
 ('pussy / 外陰部を指す俗称','医学的な腟と単純に同一化しない。タグ境界はWiki再確認対象。',9),
]

def load():
    return list(csv.DictReader((ROOT/'references/CLAIM_REGISTRY.csv').open(encoding='utf-8-sig',newline='')))
def esc(s): return html.escape(str(s))
def link(label, target): return '<link href="'+esc(target)+'" color="#206778">'+esc(label)+'</link>'
def original(path):
    for sha in [SHA,MAIN]:
        result = subprocess.run(['git','cat-file','-e',f'{sha}:{path}'],capture_output=True)
        if result.returncode == 0: return f'{REPO}/blob/{sha}/{path}'
    return f'{REPO}/issues/44'

class Book(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if hasattr(flowable,'anchor'):
            self.canv.bookmarkPage(flowable.anchor)
            self.canv.addOutlineEntry(flowable.outline,flowable.anchor,flowable.level,False)
            self.locations[flowable.anchor] = self.page

def font_paths(args):
    normal = Path(args.font or 'C:/Windows/Fonts/BIZ-UDGothicR.ttc')
    bold = Path(args.bold_font or 'C:/Windows/Fonts/BIZ-UDGothicB.ttc')
    if not normal.exists() or not bold.exists():
        raise SystemExit('Japanese TrueType fonts required: --font and --bold-font. No font download is performed.')
    return normal,bold

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--font'); parser.add_argument('--bold-font')
    args=parser.parse_args()
    normal,bold=font_paths(args)
    pdfmetrics.registerFont(TTFont('JA',str(normal)))
    pdfmetrics.registerFont(TTFont('JAB',str(bold)))
    pdfmetrics.registerFontFamily('JA',normal='JA',bold='JAB',italic='JA',boldItalic='JAB')
    styles={
      'body':ParagraphStyle('body',fontName='JA',fontSize=13.5,leading=19.6,textColor=INK,spaceAfter=11,wordWrap='CJK',splitLongWords=True),
      'title':ParagraphStyle('title',fontName='JAB',fontSize=28,leading=36,textColor=INK,spaceAfter=20,wordWrap='CJK'),
      'h':ParagraphStyle('h',fontName='JAB',fontSize=20,leading=28,textColor=INK,spaceAfter=16,wordWrap='CJK',keepWithNext=True),
      'sub':ParagraphStyle('sub',fontName='JAB',fontSize=16,leading=23,textColor=ACCENT,spaceAfter=9,wordWrap='CJK',keepWithNext=True),
      'ref':ParagraphStyle('ref',fontName='JA',fontSize=11.5,leading=16.8,textColor=ACCENT,spaceAfter=9,wordWrap='CJK'),
      'box':ParagraphStyle('box',fontName='JA',fontSize=12,leading=18,textColor=INK,spaceBefore=9,spaceAfter=13,borderPadding=10,backColor=colors.HexColor('#edf3f3'),wordWrap='CJK'),
    }
    story=[]
    sections=[]
    def p(text,style='body'): return Paragraph(text,styles[style])
    def heading(text,anchor,level=0,style='h'):
        flow=p(esc(text),style); flow.anchor=anchor; flow.outline=text; flow.level=level; return flow
    def page():
        if story and not isinstance(story[-1],PageBreak): story.append(PageBreak())
    text=(ROOT/'IMAGE_GENERATION_TEXTBOOK_JA.md').read_text(encoding='utf-8')
    chapters=[]
    for line in text.splitlines():
        if line.startswith('## '):
            chapters.append({'title':line[3:],'sections':[]})
        elif line.startswith('### '):
            chapters[-1]['sections'].append({'title':line[4:],'lines':[]})
        elif chapters and chapters[-1]['sections'] and line.strip():
            chapters[-1]['sections'][-1]['lines'].append(line)
    story += [Spacer(1,32),p('画像生成を<br/>構造から理解する','title'),p('スマートフォンで読む<br/>日本語技術教科書','h'),p('#44 Knowledge Corpus view','sub'),p('意味を読む。条件を分ける。<br/>画像を観察する。'),Spacer(1,22),p('A5 / 1カラム / 本文13.5 pt<br/>編集日 2026-10-01 / v1','box'),p('基準corpus<br/>'+esc(SHA),'ref')]
    page(); story.append(heading('目次','toc'))
    story.append(p('章名をタップして移動できます。各ページ下部の「目次へ戻る」でこの目次へ戻れます。'))
    for n,ch in enumerate(chapters): story.append(p(link(ch['title'],f'#ch{n}'),'body'))
    for title,anchor in [('用語集','glossary'),('日本語・英語・タグ索引','index'),('知識索引 / 全Claim','claims'),('HOLD / CONFLICT','holds'),('モデル・version確認台帳','versions'),('参考資料と不足情報','sources')]: story.append(p(link(title,'#'+anchor)))
    used=Counter()
    def figure(key):
        title,labels=FIGURES[key]
        d=Drawing(CONTENT,180)
        svg=['<svg xmlns="http://www.w3.org/2000/svg" width="680" height="400" viewBox="0 0 680 400"><rect width="680" height="400" fill="white"/>']
        for i,label in enumerate(labels):
            y=143-i*43
            d.add(Rect(6,y,CONTENT-12,36,rx=5,ry=5,fillColor=colors.HexColor('#edf3f3'),strokeColor=ACCENT,strokeWidth=.8))
            d.add(String(CONTENT/2,y+12,label,fontName='JA',fontSize=12,textAnchor='middle',fillColor=INK))
            svg.append(f'<rect x="20" y="{i*95+8}" width="640" height="66" rx="8" fill="#edf3f3" stroke="#206778"/><text x="340" y="{i*95+48}" text-anchor="middle" font-family="BIZ UDGothic,sans-serif" font-size="25">{esc(label)}</text>')
            if i<3:
                d.add(Line(CONTENT/2,y-2,CONTENT/2,y-10,strokeColor=ACCENT))
                d.add(Polygon([CONTENT/2-3,y-8,CONTENT/2+3,y-8,CONTENT/2,y-12],fillColor=ACCENT,strokeColor=ACCENT))
        svg.append('</svg>')
        (ROOT/'figures'/f'{key}.svg').write_text(''.join(svg),encoding='utf-8')
        return KeepTogether([d,p(esc(title),'ref')])
    (ROOT/'figures').mkdir(exist_ok=True)
    for n,ch in enumerate(chapters):
        page(); story += [heading(f'{n:02d}',f'ch{n}',style='title'),p(esc(ch['title']),'h'),p('この章で読むこと','sub')]
        for s,sec in enumerate(ch['sections']):
            anchor=f'sec{n}-{s}'
            sections.append({'chapter':n,'title':sec['title'],'anchor':anchor})
            story.append(p(link(sec['title'],'#'+anchor)))
        for s,sec in enumerate(ch['sections']):
            page(); story += [heading(sec['title'],f'sec{n}-{s}',1),p(esc(ch['title']),'ref')]
            for line in sec['lines']:
                if line.startswith('CLAIMS: '):
                    ids=line[8:].split()
                    for cid in ids: used[cid]+=1
                    ref_flow=p('根拠 '+ ' / '.join(link(cid,'#'+cid) for cid in ids),'ref')
                    if isinstance(story[-1],KeepTogether):
                        story[-1]._content.append(ref_flow)
                    else:
                        story.append(ref_flow)
                elif line.startswith('FIGURE: '): story.append(figure(line[8:]))
                elif line.startswith('PROMPT '):
                    role,value=line[7:].split(': ',1)
                    story.append(p(esc(role)+'<br/>'+esc(value),'box'))
                elif re.match(r'^(POINT|注意|HOLD|MODEL DEPENDENT):',line):
                    label,value=line.split(': ',1)
                    story.append(p('<b>'+esc(label)+'</b><br/>'+esc(value),'box'))
                else: story.append(p(esc(line)))
    page(); story.append(heading('用語集','glossary'))
    story.append(p('日本語を主に理解する補助です。タグの厳密な境界、モデルでの効能、runtimeの処理を同一視しません。'))
    for i,(term,meaning,ch) in enumerate(GLOSSARY):
        if i%3==0: page()
        story.append(KeepTogether([p(esc(term),'sub'),p(esc(meaning)),p(link('本文へ',f'#ch{ch}'),'ref')]))
    page(); story.append(heading('日本語・英語・タグ索引','index'))
    story.append(p('項目をタップすると該当章へ移動します。用語集と本文の両方から探せます。'))
    entries=sorted([(part.strip(),ch) for term,_,ch in GLOSSARY for part in term.split(' / ')],key=lambda x:x[0].casefold())
    entries += [(tag,7) for tag in ['standing','sitting','from above','from below','full body','upper body','POV','close-up','multiple views']]
    for term,ch in entries: story.append(p(link(f'{term} → 第{ch}章',f'#ch{ch}')))
    claims=load(); ids={r['ID'] for r in claims}
    source_records=json.loads((ROOT/'references/SOURCE_RECORDS.json').read_text(encoding='utf-8'))
    if set(used)-ids: raise ValueError('Unknown Claim IDs: '+str(set(used)-ids))
    page(); story.append(heading('知識索引 / 全Claim','claims'))
    story.append(p('全90件の元Claimを保持します。本文は日本語による統合解説、ここは英語原文による監査カードです。英語を読む必要がある場合も拡大なしで追える文字サイズを維持します。'))
    status=Counter(r['STATUS'] for r in claims)
    story.append(p('判定内訳<br/>'+'<br/>'.join(f'{esc(k)}: {v}' for k,v in status.items()),'box'))
    story.append(p('本文で直接参照: '+str(len(used))+'件。索引のみのClaimも判定を省略しません。本文未使用一覧はreferences/COVERAGE.jsonにあります。'))
    for row in claims:
        page(); story.append(heading(row['ID'],row['ID'],1,style='h'))
        story.append(p(row['STATUS']+' / '+row['SOURCE_CLASS'],'sub'))
        story.append(p(esc(row['Claim'])))
        story.append(p('<b>適用範囲 / SCOPE</b><br/>'+esc(row['SCOPE']).replace(';','<br/>'),'box'))
        story.append(p('<b>検証 / VALIDATION</b><br/>'+esc(row['VALIDATION_STATE'])+'<br/><b>最終確認</b> '+esc(row['last_checked']),'box'))
        refs=[r.strip() for r in row['source/evidence'].split(';') if r.strip()]
        links=[]
        for i,ref in enumerate(refs):
            if ref.startswith('http'): target=ref
            elif ref.startswith('docs/'): target=original(ref)
            elif ref.startswith('Issue #'): target=REPO+'/issues/'+re.search(r'\d+',ref).group()
            elif ref in source_records: target=source_records[ref]['source_url'] or original(source_records[ref]['registry_path'])
            else: target=f'{REPO}/blob/{SHA}/docs/knowledge/GENERATION_KNOWLEDGE_SOURCES.md'
            label=ref if ref.startswith('S-') or ref.startswith('Issue') else '原資料 '+str(i+1)
            links.append(link(label,target))
        story.append(p('根拠 / SOURCE<br/>'+' / '.join(links),'ref'))
        if row['supersedes/contradicted_by']: story.append(p('履歴 / 対立<br/>'+esc(row['supersedes/contradicted_by']),'ref'))
        story.append(p('下流参照<br/>'+esc(row['downstream_relevance']),'ref'))
    page(); story.append(heading('HOLD / CONFLICT','holds'))
    story.append(p('active CONFLICTは0件です。未確定は反復やscope確認を経てRegistryが更新されるまでHOLDを保ちます。原registerの18件をタップして追跡できます。'))
    hold_text=(ROOT/'references/HOLD_CONFLICT_REGISTER.md').read_text(encoding='utf-8-sig')
    for line in hold_text.splitlines():
        if line.startswith('| H-K-'):
            fields=[v.strip() for v in line.strip('|').split('|')]
            page(); story += [p(fields[0],'h'),p('関連Claim '+ ' / '.join(link(cid,'#'+cid) for cid in fields[1].split('; ')),'ref'),p(esc(fields[2])),p('未解決の理由<br/>'+esc(fields[3]),'box'),p('原registerの必要確認<br/>'+esc(fields[4]),'box'),p(link('固定版HOLD registerを開く',f'{REPO}/blob/{SHA}/docs/knowledge/current/HOLD_CONFLICT_REGISTER.md'),'ref')]
    page(); story.append(heading('モデル・version確認台帳','versions'))
    story.append(p('原ledgerのversionと確認日を維持します。NOT_PINNEDやlocal未確認を、再検証済みと読み替えません。長いhashは文字サイズを下げず折り返します。'))
    ledger=list(csv.DictReader((ROOT/'references/VERSION_FRESHNESS_LEDGER.csv').open(encoding='utf-8-sig',newline='')))
    for row in ledger:
        page(); story += [p(esc(row['entity']),'h'),p(esc(row['exact_model/version']),'sub'),p('原資料確認日: '+row['source_checked_date']),p('hash / checkpoint<br/>'+esc(row['checkpoint/hash']),'box'),p('local検証<br/>'+esc(row['local_verified?']),'box'),p('原ledgerの位置付け<br/>'+esc(row['current_project_applicability'])+'<br/>再確認: '+esc(row['recheck_required?']),'ref'),p(link('作者・tool source',row['source_url']),'ref')]
        if row['superseded_by']: story.append(p(link('ledgerが示す別の参照先',row['superseded_by']),'ref'))
        story.append(p('全notesは固定版ledgerで確認できます。WAI優先度など、本文と原metadataの差は冒頭とgapsに記録しています。','ref'))
    page(); story.append(heading('参考資料と不足情報','sources'))
    story.append(p('本書の解説は固定版corpusを再編集したものです。外部画像や長い公開Promptを転載していません。図は同梱builderから再生成します。'))
    for path,label in [('docs/knowledge/KNOWLEDGE_CATALOG.md','Knowledge catalog'),('docs/knowledge/current/CURRENT_QUICK_REFERENCE.md','Quick Reference'),('docs/knowledge/KNOWLEDGE_HANDOFF_CURRENT_20260909.md','Handoff'),('docs/knowledge/GENERATION_KNOWLEDGE_SOURCES.md','Source registry'),('docs/knowledge/current/LEGACY_MAP.md','Historical / Legacy map'),('docs/PRODUCT_GOAL_LOCK.md','現行mainの製品目的')]: story.append(p(link(label,original(path))))
    story.append(p('本文の非性的な例と図は説明用に作成した例であり、controlled generationの実験結果ではありません。SD1.5時代の方法の比較を埋める十分なClaimもありません。'))
    page(); story.append(p('残る知識不足','h'))
    story.append(p('モデル別の最適weight、NoobAIのbinding/count限界、Animaのhybrid差、LoRAの相互作用、Negative効果などはHOLDです。詳細は同梱KNOWLEDGE_GAPS.mdへ記録しました。'))
    story.append(p('成人向け章は臨床的な用語と構造監査を収録し、露骨な画像生成の具体的Promptや最適化手順は収録しません。この点では元タスクの全詳細範囲を満たしません。','box'))
    story.append(p('Android/iPhone実機のviewerでの閲覧・タップ確認は未実施です。1080×2400相当の画像と全ページ解析によるQAを、実機確認の代わりに実機PASSとは表示しません。'))
    def furniture(c,doc):
        c.saveState(); c.setStrokeColor(colors.HexColor('#cad9dc')); c.line(M,39,W-M,39)
        c.setFont('JA',11); c.setFillColor(ACCENT); c.drawString(M,23,'目次へ戻る'); c.linkRect('', 'toc',(M,18,M+100,35),relative=0,thickness=0)
        c.setFont('JA',11.5); c.setFillColor(INK); c.drawRightString(W-M,23,str(doc.page))
        c.restoreState()
    outfile=ROOT/'IMAGE_GENERATION_TEXTBOOK_JA.pdf'
    doc=Book(str(outfile),pagesize=A5,leftMargin=M,rightMargin=M,topMargin=33,bottomMargin=53,title='画像生成を構造から理解する',author='DanbooruTagTool / #44 textbook view',pageCompression=1)
    doc.locations={}
    doc.build(story,onFirstPage=furniture,onLaterPages=furniture)
    coverage={'corpus_sha':SHA,'main_sha':MAIN,'registry_claims':len(claims),'narrative_claim_count':len(used),'narrative_claims':sorted(used),'appendix_only':sorted(ids-set(used)),'status_counts':dict(status),'chapters':len(chapters),'sections':len(sections),'all_claims_retained_in_index':True,'locations':doc.locations,'font':str(normal),'font_sha256':hashlib.sha256(normal.read_bytes()).hexdigest()}
    (ROOT/'references/COVERAGE.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in coverage.items() if k not in ['locations','narrative_claims','appendix_only']},ensure_ascii=False))
    print('PDF:',outfile)

if __name__=='__main__': main()
