import re,glob
for fn in glob.glob('page_*.html'):
    h=open(fn,encoding='utf-8',errors='ignore').read()
    print('====',fn)
    urls=set(re.findall(r'https?://[^"\\\s<>\']{10,120}',h))
    for u in sorted(urls):
        if any(k in u for k in ['api','bbs','wiki','rule','resource']):
            print(u[:160])
