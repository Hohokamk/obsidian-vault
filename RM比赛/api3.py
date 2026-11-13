import urllib.request,json,io,sys,re,html
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='ignore')
UA={'User-Agent':'Mozilla/5.0','Content-Type':'application/json','Referer':'https://bbs.robomaster.com/'}
def info(pid):
    req=urllib.request.Request(f'https://bbs.robomaster.com/developers-server/rest/posts/info/{pid}',data=b'{}',headers=UA,method='POST')
    return json.loads(urllib.request.urlopen(req,timeout=30).read().decode('utf-8','ignore'))['data']
def clean(h):
    h=re.sub(r'(?s)<(script|style).*?</\1>','',h or '')
    h=re.sub(r'<br\s*/?>|</p>|</li>|</h\d>','\n',h)
    t=re.sub(r'<[^>]+>','',h)
    return html.unescape(re.sub(r'\n{3,}','\n\n',t)).strip()
for pid in ['1970686','1973386','1970708','1972789']:
    d=info(pid)
    print('\n\n===== %s | %s | %s ====='%(d['id'],d['title'],d.get('authorNickname')))
    print('attachments:',[(a.get('name'),a.get('url')) for a in (d.get('attachments') or [])][:5])
    print('files:',[(a.get('name'),a.get('url')) for a in (d.get('fileItems') or [])][:5])
    print(clean(d.get('htmlContent'))[:6000])
