import urllib.request,json,io,sys,re,html
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='ignore')
UA={'User-Agent':'Mozilla/5.0','Content-Type':'application/json','Referer':'https://bbs.robomaster.com/'}
def post(u,obj):
    req=urllib.request.Request(u,data=json.dumps(obj).encode(),headers=UA,method='POST')
    return json.loads(urllib.request.urlopen(req,timeout=30).read().decode('utf-8','ignore'))
def clean(h):
    h=re.sub(r'(?s)<(script|style).*?</\1>','',h or '')
    h=re.sub(r'<br\s*/?>|</p>|</li>|</h\d>|</tr>','\n',h)
    h=re.sub(r'</td>',' | ',h)
    t=re.sub(r'<[^>]+>','',h)
    return html.unescape(re.sub(r'\n{3,}','\n\n',t)).strip()
r=post('https://bbs.robomaster.com/developers-server/rest/search/page-posts-es-search-v2',{"pageSize":10,"pageNo":1,"filter":{"query":"完整形态考核","sort":"relevance","category":"ALL"}})
for x in (r['data']['list'] or [])[:8]:
    print(re.sub(r'</?highlight>','',x['title']),'|',x['id'])
print('\n--- fetch ---')
for pid in [x['id'] for x in (r['data']['list'] or [])[:2]]:
    j=post(f'https://bbs.robomaster.com/developers-server/rest/posts/info/{pid}',{})['data']
    print('=====',j['title'],j.get('authorNickname'))
    print([(a.get('name'),a.get('url')) for a in (j.get('fileItems') or [])][:6])
    print(clean(j.get('htmlContent'))[:5000])
