import urllib.request,re,io,sys,html
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='ignore')
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0'}
for pid in ['1969149','1969150','1969147']:
    u=f'https://bbs.robomaster.com/wiki/20204847/{pid}'
    try:
        h=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read().decode('utf-8','ignore')
        open(f'w{pid}.html','w',encoding='utf-8').write(h)
        print('====',u,len(h))
        # find text around 重装
        for m in re.finditer('重装',h):
            s=h[max(0,m.start()-300):m.start()+300]
            s=re.sub(r'<[^>]+>',' ',s); s=re.sub(r'\s+',' ',s)
            print('  ...',s[:400])
    except Exception as e: print('ERR',u,e)
