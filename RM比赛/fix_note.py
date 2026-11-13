import io
p='重装机器人全解_RMUC2027.md'
s=open(p,encoding='utf-8').read()
old1="作为对比，步兵 10 级功率优先是 100 W / 400 kg？不，是 100 W 对应 300–400 血量的车；重装的“吨功率”明显偏低。"
new1="作为对比，步兵 10 级“功率优先”底盘是 100 W、400 血；重装用 50 W 驱动 41 kg，功率/重量比明显更低。"
assert old1 in s
s=s.replace(old1,new1)
old2="相当于 160–200 发 17 mm 或 170–200 发 42 mm 的兑换能力（按远程价）。"
new2="按远程兑换价（42 mm 为 150 金币/10 发）约等于 180 发 42 mm 的购买力。"
assert old2 in s
s=s.replace(old2,new2)
open(p,'w',encoding='utf-8').write(s)
print('ok', len(s))
