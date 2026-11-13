import urllib.request,json,io,sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='ignore')
UA={'User-Agent':'Mozilla/5.0','Content-Type':'application/json','Referer':'https://bbs.robomaster.com/'}
def post(u,obj):
    req=urllib.request.Request(u,data=json.dumps(obj).encode(),headers=UA,method='POST')
    return json.loads(urllib.request.urlopen(req,timeout=30).read().decode('utf-8','ignore'))
for q in ['重装机器人','重装']:
    d=post('https://bbs.robomaster.com/developers-server/rest/search/page-posts-es-search-v2',{"pageSize":20,"pageNo":1,"filter":{"query":q,"sort":"relevance","category":"ALL"}})
    data=d.get('data') or {}
    print('====',q,'keys',list(data.keys())[:8])
    recs=data.get('records') or data.get('list') or []
    print('count',data.get('total'),len(recs))
    for r in recs[:15]:
        print('-',r.get('title'),'|',r.get('id'),'|',(r.get('summary') or r.get('content') or '')[:120])
