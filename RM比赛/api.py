import urllib.request, json, io, sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='ignore')
UA={'User-Agent':'Mozilla/5.0','Content-Type':'application/json','Referer':'https://bbs.robomaster.com/'}
for pid in ['1970973','1969161']:
    u=f'https://bbs.robomaster.com/developers-server/rest/posts/info/{pid}'
    try:
        req=urllib.request.Request(u,data=b'{}',headers=UA,method='POST')
        b=urllib.request.urlopen(req,timeout=30).read().decode('utf-8','ignore')
        d=json.loads(b)
        print('====',pid, list(d.keys())[:10])
        s=json.dumps(d,ensure_ascii=False)
        print(s[:1500])
    except Exception as e: print('ERR',pid,e)
