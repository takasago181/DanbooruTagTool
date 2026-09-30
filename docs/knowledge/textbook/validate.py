"""Structural checks plus full-page smartphone rendering. Scratch images are not committed."""
import argparse, json, subprocess, hashlib
from pathlib import Path
import pdfplumber
from pypdf import PdfReader
from PIL import Image, ImageOps, ImageDraw

ROOT=Path(__file__).resolve().parent
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--render',action='store_true'); args=parser.parse_args()
    pdf=ROOT/'IMAGE_GENERATION_TEXTBOOK_JA.pdf'
    reader=PdfReader(pdf)
    problems=[]; sizes=[]; blank=[]; links=0; internal=0; external=0; body_pages=[]
    destinations=set(reader.named_destinations)
    def visit(outline):
        for node in outline:
            if isinstance(node,list): visit(node)
            else:
                if reader.get_destination_page_number(node) is None: problems.append('Unresolved outline')
    visit(reader.outline)
    with pdfplumber.open(pdf) as doc:
        for n,page in enumerate(doc.pages,1):
            if abs(page.width-419.5276)>.1 or abs(page.height-595.2756)>.1: problems.append(f'Page {n}: not A5')
            text=page.extract_text() or ''
            content=[c for c in page.chars if c['top']<550]
            if len(content)<12: blank.append(n)
            if '\ufffd' in text or '\u25a0' in text: problems.append(f'Page {n}: replacement/square glyph')
            for c in page.chars:
                sizes.append(round(c['size'],2))
                if c['x0']<24 or c['x1']>page.width-24 or c['top']<20 or c['bottom']>page.height-12:
                    problems.append(f'Page {n}: out-of-bounds glyph {c["text"]!r}')
            if any(13.4<=c['size']<=13.6 for c in content): body_pages.append(n)
            annots=reader.pages[n-1].get('/Annots',[])
            for ref in annots:
                a=ref.get_object()
                if a.get('/Subtype')!='/Link': continue
                links+=1
                rect=a.get('/Rect',[])
                if len(rect)!=4 or rect[0]<0 or rect[2]>page.width+1 or rect[1]<0 or rect[3]>page.height+1: problems.append(f'Page {n}: link outside page')
                if '/Dest' in a:
                    internal+=1; dest=a['/Dest']
                    if isinstance(dest,list):
                        try:
                            if reader.get_page_number(dest[0].get_object())<0: problems.append(f'Page {n}: invalid destination')
                        except Exception as e: problems.append(f'Page {n}: invalid destination {e}')
                    elif str(dest) not in destinations: problems.append(f'Page {n}: unknown named link {dest}')
                elif a.get('/A',{}).get('/URI'): external+=1
        alltext='\n'.join(p.extract_text() or '' for p in doc.pages)
    coverage=json.loads((ROOT/'references/COVERAGE.json').read_text(encoding='utf-8'))
    for cid in coverage['narrative_claims']+coverage['appendix_only']:
        if cid not in alltext: problems.append('Missing Claim '+cid)
    for word in ['fellatio','paizuri','cum_on_body','penis','pussy','nipple']:
        if word not in alltext: problems.append('Missing clinical term '+word)
    if min(sizes)<10.99: problems.append('Font smaller than 11 pt')
    if blank: problems.append('Blank/near-blank pages '+str(blank))
    digest=hashlib.sha256(pdf.read_bytes()).hexdigest()
    out=Path('tmp/pdfs/issue44-smartphone',digest[:12]).resolve(); out.mkdir(parents=True,exist_ok=True)
    if args.render:
        subprocess.run(['pdftoppm','-scale-to-x','1080','-scale-to-y','-1','-png',str(pdf),str(out/'page')],check=True)
        paths=sorted(out.glob('page-*.png'))
        if len(paths)!=len(reader.pages): problems.append('Rendered page count mismatch')
        phone=out/'phone'; phone.mkdir(exist_ok=True)
        sheets=out/'contact'; sheets.mkdir(exist_ok=True)
        thumbs=[]
        for i,path in enumerate(paths,1):
            img=Image.open(path).convert('RGB')
            screen=Image.new('RGB',(1080,2400),'#dce2e5')
            screen.paste(img,((1080-img.width)//2,(2400-img.height)//2))
            screen.save(phone/path.name)
            thumb=screen.resize((216,480),Image.Resampling.LANCZOS)
            ImageDraw.Draw(thumb).text((5,4),str(i),fill='black')
            thumbs.append(thumb)
        for offset in range(0,len(thumbs),20):
            sheet=Image.new('RGB',(216*5,480*4),'white')
            for i,im in enumerate(thumbs[offset:offset+20]): sheet.paste(im,((i%5)*216,(i//5)*480))
            sheet.save(sheets/f'contact-{offset//20+1:02d}.jpg')
    report={'pages':len(reader.pages),'pdf_sha256':digest,'page_size':'A5 148 × 210 mm','font_min_pt':min(sizes),'body_pt':13.5,'leading':19.6,'diagram_pt':12,'links':links,'internal_links':internal,'external_links':external,'claim_count':coverage['registry_claims'],'chapters':coverage['chapters'],'status_counts':coverage['status_counts'],'blank_pages':blank,'problems':sorted(set(problems)),'rendered_all_pages':args.render,'phone_canvas':[1080,2400],'render_path':str(out),'real_android_iphone_test':False,'automated_result':'PASS' if not problems else 'FAIL'}
    (ROOT/'references/PDF_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if problems: raise SystemExit(1)
if __name__=='__main__': main()
