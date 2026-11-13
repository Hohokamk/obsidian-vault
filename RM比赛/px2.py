import urllib.request,re,io,sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='ignore')
UA={'User-Agent':'Mozilla/5.0'}
h=urllib.request.urlopen(urllib.request.Request('https://bbs.robomaster.com/wiki/77882607',headers=UA),timeout=30).read().decode('utf-8','ignore')
open('plan.html','w',encoding='utf-8').write(h)
print('len',len(h),'count 3.2.3.1',h.count('3.2.3.1'),'count 战术定位',h.count('战术定位'))
for m in re.finditer('3\\.2\\.3\\.1',h):
    s=h[max(0,m.start()-400):m.start()+600]
    print('---'); print(re.sub(r'\s+',' ',s)[:900])
