import re
h=open('wiki.html',encoding='utf-8',errors='ignore').read()
for m in re.finditer(r'["\']([^"\']*api[^"\']{0,80})["\']',h):
    s=m.group(1)
    if len(s)<100: print(s)
