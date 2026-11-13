p='RMUC2027_重装机器人_赛季规划.md'
s=open(p,encoding='utf-8').read()
anchor="【建议】建立两张射表："
table='''【推算】不同仰角的理想弹道（无阻力，仅作射表起点）：

| 仰角 | 理想射程 | 飞行时间 | 适用 |
|---:|---:|---:|---|
| 30° | 24.0 m | 1.68 s | 低伸吊射，飞行时间短 |
| 45° | 27.7 m | 2.38 s | 最大射程 |
| 60° | 24.0 m | 2.91 s | 高抛越障，飞行时间长 |

实际有空气阻力，射程会低于表中值；6 轮若产生后旋，射程可能增加但弹道更弯。以实测射表为准。

'''
assert anchor in s
s=s.replace(anchor, table+anchor,1)
open(p,'w',encoding='utf-8').write(s)
print('ok')
