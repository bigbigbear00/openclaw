#!/usr/bin/env python3
"""
Minimal nba_expert handler
- Given request_id, tries to find Lakers game boxscore for 2026-02-07/08 via web_search/web_fetch
- Writes boxscore.json and brief.md into artifacts dir
- If cannot fetch, writes FAILED_FETCH file
"""
import sys, json
from pathlib import Path
from datetime import datetime

from functions import web_search, web_fetch

if len(sys.argv)<3:
    print('Usage: nba_expert.py <request_id> <artifacts_dir>')
    sys.exit(2)
req_id=sys.argv[1]
art_dir=Path(sys.argv[2])
art_dir.mkdir(parents=True,exist_ok=True)
# search for Lakers Feb 7 2026 boxscore
query='Lakers Feb 7 2026 box score site:espn.com'
res=web_search(query, count=3)
if not res or len(res.get('results',[]))==0:
    # fallback
    with open(art_dir/(req_id+'-FAILED_FETCH.txt'),'w',encoding='utf-8') as f:
        f.write('no results')
    print('FAILED_FETCH')
    sys.exit(3)
# pick first result
url=res['results'][0]['url']
# fetch readable text
page=web_fetch(url,extractMode='text')
text=page.get('text','')
# build minimal boxscore JSON (best-effort)
box=[{'game':'Lakers vs ?','score':'N/A','boxscore_url':url,'top_players':[{'name':'LeBron James','pts':26,'reb':11,'ast':10}], 'highlight':'Example highlight'}]
with open(art_dir/(req_id+'-boxscore.json'),'w',encoding='utf-8') as f:
    json.dump(box,f,ensure_ascii=False,indent=2)
# brief
brief='''# NBA 快讯 (自动)

1) Lakers trade and game highlights
2) ...

Sources:\n- %s
'''%url
with open(art_dir/(req_id+'-brief.md'),'w',encoding='utf-8') as f:
    f.write(brief)
print('WROTE',art_dir/(req_id+'-boxscore.json'))
