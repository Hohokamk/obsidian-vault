import urllib.request,json,io,sys,re,html
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='ignore')
UA={'User-Agent':'Mozilla/5.0','Content-Type':'application/json','Referer':'https://bbs.robomaster.com/'}
def info(pid):
    req=urllib.request.Request(f'https://bbs.robomaster.com/developers-server/rest/posts/info/{pid}',data=b'{}',headers=UA,method='POST')
    return json.loads(urllib.request.urlopen(req,timeout=30).read().decode('utf-8','ignore'))['data']
for pid in ['1973311','1973321']:
    j=info(pid)
    print('====',pid,j['title'],j.get('createAt'))
    print('attachments',[(a.get('name'),a.get('url')) for a in (j.get('attachments') or [])])
    print('files',[(a.get('name'),a.get('url')) for a in (j.get('fileItems') or [])])
    print('refs',j.get('references'))
    print('html',len(j.get('htmlContent') or ''))
    print((j.get('htmlContent') or '')[:300])
