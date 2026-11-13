import urllib.request,json,io,sys,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='ignore')
UA={'User-Agent':'Mozilla/5.0','Content-Type':'application/json','Referer':'https://bbs.robomaster.com/'}
def post(u,obj):
    req=urllib.request.Request(u,data=json.dumps(obj).encode(),headers=UA,method='POST')
    return json.loads(urllib.request.urlopen(req,timeout=30).read().decode('utf-8','ignore'))
for q in ['第二十六届 ROBOMASTER 通知','2027 赛程','2027 区域赛 时间']:
    d=post('https://bbs.robomaster.com/developers-server/rest/search/page-posts-es-search-v2',{"pageSize":8,"pageNo":1,"filter":{"query":q,"sort":"relevance","category":"ALL"}})
    print('===',q)
    for x in (d['data']['list'] or [])[:6]:
        print('-',re.sub(r'</?highlight>','',x['title']),'|',x['id'])
