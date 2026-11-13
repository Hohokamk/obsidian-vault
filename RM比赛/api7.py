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
j=post('https://bbs.robomaster.com/developers-server/rest/posts/info/1971755',{})['data']
print(j['title'],j.get('authorNickname'),j.get('createAt'))
print([(a.get('name'),a.get('url')) for a in (j.get('fileItems') or [])])
txt=clean(j.get('htmlContent'))
open('kaohe.txt','w',encoding='utf-8').write(txt)
print('len',len(txt))
i=txt.find('重装机器人展示细则')
print(txt[max(0,i-2500):i+2500])
