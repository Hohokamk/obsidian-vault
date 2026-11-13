import re
t=open('qianzhan.txt',encoding='utf-8').read()
m=re.search(r'===== PAGE 7 =====(.*?)===== PAGE 11 =====',t,re.S)
print(m.group(1) if m else t[:200])
