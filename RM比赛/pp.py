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
for pid in ['1973254','1973321']:
    j=post(f'https://bbs.robomaster.com/developers-server/rest/posts/info/{pid}',{})['data']
    print('=====',j['id'],j['title'],j.get('authorNickname'),j.get('createAt'))
    print('attachments:',[(a.get('name'),a.get('url')) for a in (j.get('attachments') or [])])
    print('files:',[(a.get('name'),a.get('url')) for a in (j.get('fileItems') or [])])
    txt=clean(j.get('htmlContent'))
    open(f'plan_{pid}.txt','w',encoding='utf-8').write(txt)
    print(txt[:6000])
