import re, urllib.parse, urllib.request

UA = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
def bing(q, n=12):
    u = 'https://www.bing.com/search?q=' + urllib.parse.quote(q) + '&setlang=zh-CN&count=20'
    req = urllib.request.Request(u, headers=UA)
    html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'ignore')
    items = re.findall(r'(?s)<li class="b_algo".*?</li>', html)
    print('###', q, 'hits:', len(items))
    for i, it in enumerate(items[:n], 1):
        m = re.search(r'(?s)<h2>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', it)
        if not m: continue
        title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        sn = re.search(r'(?s)<p[^>]*>(.*?)</p>', it)
        snippet = re.sub(r'<[^>]+>', '', sn.group(1)).strip() if sn else ''
        print(f'{i}. {title}\n   {m.group(1)}\n   {snippet}')

for q in ['RMUC 2027 重装机器人', 'RoboMaster 2027 重装机器人 规则解析', 'RoboMaster 2027 规则 重装 42mm 发射机构', '机甲大师 2027 工程 英雄 合并 重装']:
    bing(q)
    print()
