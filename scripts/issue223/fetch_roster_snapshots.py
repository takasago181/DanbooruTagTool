"""Explicit research operation; never called by runtime or asset reproduction."""
import json
import urllib.parse
import urllib.request
from pathlib import Path

titles = ['mobile_suit_gundam', 'zeta_gundam', 'gundam_zz', 'gundam_0080', 'gundam_0083',
          'gundam_unicorn', 'gundam_seed', 'gundam_seed_destiny', 'gundam_00',
          'gundam_suisei_no_majo', 'list_of_pokemon']
out = Path(__file__).resolve().parents[2] / 'docs/issue223/snapshots'
out.mkdir(parents=True, exist_ok=True)
for title in titles:
    path = out / (title + '.json')
    if path.exists():
        continue
    url = 'https://danbooru.donmai.us/wiki_pages.json?' + urllib.parse.urlencode({'search[title]': title})
    request = urllib.request.Request(url, headers={'User-Agent': 'DanbooruTagTool-Issue223-research'})
    pages = json.load(urllib.request.urlopen(request, timeout=30))
    page = next(p for p in pages if p['title'] == title and not p.get('is_deleted'))
    path.write_text(json.dumps(page, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(title, len(page['body']))
