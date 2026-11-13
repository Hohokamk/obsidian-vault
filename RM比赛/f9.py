import re,urllib.request,io,sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='ignore')
h=open('wiki.html',encoding='utf-8',errors='ignore').read()
srcs=re.findall(r'src="([^"]+\.js)"',h)
print(len(srcs))
for s in srcs[:5]: print(s)
UA={'User-Agent':'Mozilla/5.0'}
for s in srcs:
    if 'entry' in s or 'app' in s or 'pages' in s.lower():
        try:
            b=urllib.request.urlopen(urllib.request.Request(s if s.startswith('http') else 'https://bbs.robomaster.com'+s,headers=UA),timeout=30).read().decode('utf-8','ignore')
            hits=set(re.findall(r'["\'](/[a-zA-Z0-9_\-/]*(?:api|wiki|posts)[a-zA-Z0-9_\-/]*)["\']',b))
            if hits:
                print('==',s,len(b)); 
                for x in sorted(hits)[:40]: print('  ',x)
        except Exception as e: print('ERR',s,e)
