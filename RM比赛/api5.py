import urllib.request,json,io,sys,re,datetime
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='ignore')
UA={'User-Agent':'Mozilla/5.0','Content-Type':'application/json','Referer':'https://bbs.robomaster.com/'}
def post(u,obj):
    req=urllib.request.Request(u,data=json.dumps(obj).encode(),headers=UA,method='POST')
    return json.loads(urllib.request.urlopen(req,timeout=30).read().decode('utf-8','ignore'))
d=post('https://bbs.robomaster.com/developers-server/rest/posts/info/1973386',{} if False else {}) if False else None
req=urllib.request.Request('https://bbs.robomaster.com/developers-server/rest/posts/info/1973386',data=b'{}',headers=UA,method='POST')
j=json.loads(urllib.request.urlopen(req,timeout=30).read().decode('utf-8','ignore'))['data']
for k,v in j.items():
    s=json.dumps(v,ensure_ascii=False) if not isinstance(v,str) else v
    print(k,'=',s[:300])
print('\n--- sorted by time ---')
for sort in ['time','latest','createAt']:
    try:
        r=post('https://bbs.robomaster.com/developers-server/rest/search/page-posts-es-search-v2',{"pageSize":15,"pageNo":1,"filter":{"query":"重装","sort":sort,"category":"ALL"}})
        lst=(r.get('data') or {}).get('list') or []
        print('sort',sort,[re.sub(r'</?highlight>','',x.get('title',''))[:60] for x in lst[:8]])
    except Exception as e: print('ERR',sort,e)
