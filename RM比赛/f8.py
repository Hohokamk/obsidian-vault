import urllib.request,json,io,sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='ignore')
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0','Referer':'https://bbs.robomaster.com/'}
cands=[
'https://bbs.robomaster.com/api/wiki/1969149',
'https://bbs.robomaster.com/api/wiki/posts/1969149',
'https://bbs.robomaster.com/api/wiki/detail?postsId=1969149',
'https://bbs.robomaster.com/api/v1/wiki/1969149',
'https://bbs.robomaster.com/api/posts/1969149',
'https://bbs.robomaster.com/api/article/1969149',
'https://bbs.robomaster.com/api/search?keyword=%E9%87%8D%E8%A3%85',
'https://bbs.robomaster.com/api/search/posts?keyword=%E9%87%8D%E8%A3%85',
]
for u in cands:
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=15)
        b=r.read()[:300]
        print(r.status,u,b[:200])
    except Exception as e: print('ERR',u,e)
