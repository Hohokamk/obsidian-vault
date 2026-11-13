import urllib.request, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
for u in ['https://bbs.robomaster.com/wiki/20204847','https://www.robomaster.com/zh-CN/resource/announcement/competition']:
    try:
        h=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read().decode('utf-8','ignore')
        open('page_%s.html'%abs(hash(u)),'w',encoding='utf-8').write(h)
        txt=re.sub(r'(?s)<script.*?</script>|<style.*?</style>','',h)
        txt=re.sub(r'<[^>]+>',' ',txt)
        txt=re.sub(r'\s+',' ',txt)
        print('=====',u,len(h))
        print(txt[:3000])
    except Exception as e:
        print('ERR',u,e)
