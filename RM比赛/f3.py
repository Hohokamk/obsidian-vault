import urllib.request, re, io, sys, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36','Accept-Language':'zh-CN,zh;q=0.9'}
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read().decode('utf-8','ignore')
def sogou(q,page=1):
    u='https://www.sogou.com/web?query='+urllib.parse.quote(q)+'&page=%d'%page
    h=get(u)
    blocks=re.findall(r'(?s)<div class="vrwrap">.*?</div>\s*</div>',h)
    if not blocks: blocks=re.findall(r'(?s)<div class="rb">.*?</div>\s*</div>',h)
    out=[f'### {q} p{page} blocks={len(blocks)}']
    for b in blocks[:12]:
        m=re.search(r'(?s)<h3[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',b)
        if not m: continue
        t=re.sub(r'<[^>]+>','',m.group(2)).strip()
        txt=re.sub(r'(?s)<[^>]+>',' ',b); txt=re.sub(r'\s+',' ',txt).strip()
        out.append(f'- {t}\n  {m.group(1)}\n  {txt[:260]}')
    return '\n'.join(out)
qs=['RMUC 2027 重装机器人','2027 重装机器人 能量单元 装配','机甲大师 2027 重装 规则 解读','RoboMaster 2027 重装 工程 英雄']
all=[]
for q in qs: all.append(sogou(q))
open('res2.txt','w',encoding='utf-8').write('\n\n'.join(all))
print('ok')
