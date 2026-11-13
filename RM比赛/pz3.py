import sys
sys.stdout.reconfigure(encoding='utf-8')
t=open('kaohe.txt',encoding='utf-8').read()
i=t.find('11 | 模拟触发制高点')
print(t[i:i+900])
