import urllib.request,json,io,sys,re,datetime
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='ignore')
UA={'User-Agent':'Mozilla/5.0','Content-Type':'application/json','Referer':'https://bbs.robomaster.com/'}
def post(u,obj):
    req=urllib.request.Request(u,data=json.dumps(obj).encode(),headers=UA,method='POST')
    return json.loads(urllib.request.urlopen(req,timeout=30).read().decode('utf-8','ignore'))
for q in ['重装 装配','重装 机械臂','能量单元','42mm 重装','重装 越障','重装 云台']:
    d=post('https://bbs.robomaster.com/developers-server/rest/search/page-posts-es-search-v2',{"pageSize":10,"pageNo":1,"filter":{"query":q,"sort":"relevance","category":"ALL"}})
    data=d.get('data') or {}
    print('\n====',q,'total',data.get('total'))
    for r in (data.get('list') or [])[:8]:
        t=re.sub(r'</?highlight>','',r.get('title') or '')
        ts=r.get('createAt') or 0
        ds=datetime.datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d') if isinstance(ts,(int,float)) and ts>1e12 else str(ts)[:10]
        print('-',t,'|',r.get('id'),'|',ds)
