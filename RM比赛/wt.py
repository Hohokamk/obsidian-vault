import urllib.request,json,io,sys,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='ignore')
UA={'User-Agent':'Mozilla/5.0','Content-Type':'application/json','Referer':'https://bbs.robomaster.com/'}
def post(u,obj):
    req=urllib.request.Request(u,data=json.dumps(obj).encode(),headers=UA,method='POST')
    return json.loads(urllib.request.urlopen(req,timeout=30).read().decode('utf-8','ignore'))
for ep,payload in [
  ('https://bbs.robomaster.com/developers-server/rest/wiki/category/all',{'wikiId':77882607}),
  ('https://bbs.robomaster.com/developers-server/rest/wiki/list',{'wikiId':77882607}),
]:
    try:
        d=post(ep,payload)
        s=json.dumps(d,ensure_ascii=False)
        print('====',ep,len(s))
        print(s[:4000])
    except Exception as e: print('ERR',ep,e)
