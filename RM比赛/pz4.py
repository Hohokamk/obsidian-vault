import sys
sys.stdout.reconfigure(encoding='utf-8')
t=open('kaohe.txt',encoding='utf-8').read()
i=t.find('重装机器人展示细则')
j=t.find('步兵机器人展示细则')
print(t[i:j])
