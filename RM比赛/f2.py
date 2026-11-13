import urllib.request, re, io, sys, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36','Accept-Language':'zh-CN,zh;q=0.9'}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read().decode('utf-8','ignore')
for u in ['https://bbs.robomaster.com/search?keyword=%E9%87%8D%E8%A3%85',
          'https://www.baidu.com/s?wd='+urllib.parse.quote('RMUC 2027 重装机器人'),
          'https://www.sogou.com/web?query='+urllib.parse.quote('RMUC 2027 重装机器人')]:
    try:
        h=get(u); print('=====',u,len(h))
        t=re.sub(r'(?s)<script.*?</script>|<style.*?</style>','',h); t=re.sub(r'<[^>]+>',' ',t); t=re.sub(r'\s+',' ',t)
        print(t[:1500])
    except Exception as e: print('ERR',u,e)
