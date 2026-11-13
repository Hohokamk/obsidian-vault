import re, urllib.parse, urllib.request, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
UA = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
out=[]
def bing(q, n=10):
    u = 'https://www.bing.com/search?q=' + urllib.parse.quote(q) + '&setlang=zh-CN&count=30'
    html = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read().decode('utf-8','ignore')
    items = re.findall(r'(?s)<li class="b_algo".*?</li>', html)
    out.append(f'### {q}  (hits {len(items)})')
    for i, it in enumerate(items[:n],1):
        m = re.search(r'(?s)<h2>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', it)
        if not m: continue
        title = re.sub(r'<[^>]+>','',m.group(2)).strip()
        sn = re.search(r'(?s)<p[^>]*>(.*?)</p>', it)
        snippet = re.sub(r'<[^>]+>','',sn.group(1)).strip() if sn else ''
        out.append(f'{i}. {title}\n   {m.group(1)}\n   {snippet}')
    out.append('')
qs = [
 '"重装机器人" RMUC 2027',
 'site:bbs.robomaster.com 重装机器人',
 'RMUC2027 新规则 解读',
 '2027 机甲大师 重装 能量单元 装配',
 'RoboMaster 2027 规则 变化 英雄 工程 合并',
 '重装机器人 42mm 发射机构 2027',
]
for q in qs: 
    try: bing(q)
    except Exception as e: out.append(f'ERR {q}: {e}')
open('res.txt','w',encoding='utf-8').write('\n'.join(out))
print('done')
