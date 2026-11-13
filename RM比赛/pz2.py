import re,sys
sys.stdout.reconfigure(encoding='utf-8')
t=open('qianzhan.txt',encoding='utf-8').read()
i=t.find('新赛季主要变更概述')
print(t[i:i+2500])
