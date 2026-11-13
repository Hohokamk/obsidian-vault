import urllib.request,re,io,sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='ignore')
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0'}
h=urllib.request.urlopen(urllib.request.Request('https://bbs.robomaster.com/wiki/20204847',headers=UA),timeout=30).read().decode('utf-8','ignore')
open('wiki.html','w',encoding='utf-8').write(h)
for kw in ['2027','答疑','规则手册']:
    print('---',kw, h.count(kw))
idx=[m.start() for m in re.finditer('2027',h)][:8]
for i in idx:
    print(repr(h[max(0,i-200):i+200]).replace('\\n',' ')[:420])
