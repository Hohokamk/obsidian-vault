# 09 阵列因子、PIN二极管与天线拓展

## 1. 本部分在项目中的位置

核心硬件完成前，本部分只需要建立可运行的理论基线。不要让阵列算法抢占64/256路硬件主线。

三层关系：

```text
硬件控制码 s_mn
        ↓ 状态映射
单元复响应 c_mn(s)
        ↓ 阵列叠加
阵列因子/方向图
```

LED只显示`s_mn`，不显示真实复响应。

---

## 2. 代表性论文

### 16×16编码超表面与控制板

*A Novel Coding Metasurface for Wireless Power Transfer Applications*

<https://www.mdpi.com/1996-1073/12/23/4488>

可学习内容：

- 16×16，256个单元；
- 每个PIN二极管独立控制；
- FPGA配合移位寄存器和锁存；
- 控制板输出与PIN状态对应；
- LED并联用于显示状态；
- 证明“LED作为控制状态指示”在原型中有实际先例。

不可照搬：

- 它的频段、PIN偏置、电路和FPGA架构；
- 它的LED连接；
- 它的单元状态与本项目天线不一定相同。

### RIS功耗模型

*Reconfigurable Intelligent Surface: Power Consumption Modeling and Practical Measurement Validation*

<https://arxiv.org/abs/2211.00323>

重点：

- 控制器；
- 驱动电路；
- 单元；
- 静态/动态功耗；
- PIN二极管电流；
- 更新过程。

用途：

- 将本项目LED控制板功耗研究延伸到真实RIS；
- 不只统计MCU功耗；
- 说明单元数量和状态会影响总功耗。

### 256单元、2 bit RIS原型

*Reconfigurable Intelligent Surface-Based Wireless Communications: Antenna Design, Prototyping, and Experimental Results*

检索入口：

<https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=Reconfigurable%20Intelligent%20Surface-Based%20Wireless%20Communications%20Antenna%20Design%20Prototyping%20Experimental%20Results>

重点：

- 256单元；
- 2 bit状态；
- 硬件和控制；
- 真实状态不是简单LED亮灭；
- 波束和链路实验。

### 可扩展RIS设计与原型

IEEE Open Journal of the Communications Society相关文章：

<https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=Scalable%20RIS%20Design%20Prototyping%20and%20Field%20Trials>

可学习：

- 模块化tile；
- 控制与供电；
- 扩展；
- 更新速度；
- 现场测试。

---

## 3. 理想平面阵列模型

设阵列为`rows × cols`，单元间距为波长的比例：

```text
dx = 0.5 λ
dy = 0.5 λ
```

第`m,n`个单元位置：

\[
\mathbf r_{mn}=
[n d_x,\ m d_y,\ 0]
\]

观察方向单位向量：

\[
\mathbf u(\theta,\phi)=
[\sin\theta\cos\phi,\ \sin\theta\sin\phi,\ \cos\theta]
\]

阵列因子：

\[
AF(\theta,\phi)=
\sum_m\sum_n
w_{mn}
e^{j2\pi\mathbf r_{mn}\cdot\mathbf u}
\]

其中位置以波长归一化，故波数写为`2π`。

---

## 4. 三种状态模型

## 4.1 连续相位

目标方向\((\theta_0,\phi_0)\)：

\[
w_{mn}=
e^{-j2\pi\mathbf r_{mn}\cdot\mathbf u_0}
\]

这是理想基线，不对应本项目二值LED硬件。

## 4.2 理想1 bit相位

将连续权重量化为：

\[
w_{mn}\in\{+1,-1\}
\]

代表两个相差180°的理想状态。

限制：

- 实际两个状态可能不正好180°；
- 幅度不同；
- 可能产生对称波束；
- 单元方向图和互耦未考虑。

## 4.3 二值幅度掩膜

\[
w_{mn}\in\{0,1\}
\]

表示关闭或启用单元、子阵选择或稀疏阵列。

它一般不能仅靠开关在任意方向形成相控主瓣。它更适合研究：

- 稀疏度；
- 旁瓣；
- 零陷；
- 功耗；
- 子阵选择。

---

## 5. starter_code仿真

```text
starter_code/code/simulation/
├── array_factor.py
├── demo.py
└── optimize_binary.py
```

安装依赖后：

```bash
cd starter_code/code/simulation
python demo.py
```

输出：

```text
simulation_results/
├── continuous.csv
├── one_bit.csv
├── amplitude_mask.csv
└── cuts.png
```

### `array_factor.py`

主要函数：

- `PlanarArray`：阵列几何；
- `positions_lambda()`：以波长为单位的位置；
- `steering_weights()`：连续相位；
- `quantize_one_bit()`：量化到`+1/-1`；
- `amplitude_mask()`：0/1幅度；
- `array_factor()`：复场叠加；
- `normalized_power_db()`：归一化功率dB；
- `cut()`：主平面切面；
- `beamwidth_3db()`；
- `peak_sidelobe_level()`。

### 验证

```bash
pytest starter_code/code/tests/test_array_factor.py -q
```

测试应覆盖：

- 2×2或小阵列；
- 广侧均匀权重主瓣在0°；
- 连续相位主瓣接近目标；
- dB归一化；
- 1 bit输出只有±1。

---

## 6. 为什么1 bit可能出现对称波束

若权重全为实数`+1/-1`，阵列因子可能具有共轭/对称性质，出现两个等强方向。这不是代码一定错误，而是简单理想模型的限制。

学生应：

1. 画完整-90°～90°切面；
2. 不只报告“期望方向附近峰值”；
3. 找全局最大；
4. 报告所有强峰；
5. 讨论单元方向图、馈源照明和非理想状态是否打破对称。

---

## 7. 二值幅度随机搜索

运行：

```bash
python starter_code/code/simulation/optimize_binary.py \
  --rows 16 \
  --cols 16 \
  --target-theta 0 \
  --null-theta 30 \
  --density 0.5 \
  --trials 10000 \
  --seed 2026 \
  --out best_mask.npy
```

它不是AI最优，只是可解释基线：

\[
score=
P_{\mathrm{target}}
-2P_{\mathrm{null}}
-\lambda\rho_{\mathrm{on}}
\]

其中：

- 目标方向功率越高越好；
- 零陷方向功率越低越好；
- 开启比例带惩罚。

问题：

- 只评估少数方向；
- 可能把能量推到未检查方向；
- 随机搜索效率低；
- 不考虑单元方向图；
- 不保证全局最优。

必须画完整切面后再解释结果。

---

## 8. DEAP和pymoo拓展

### DEAP

<https://github.com/DEAP/deap>

<https://deap.readthedocs.io/>

适合：

- 二进制染色体；
- 自定义交叉和变异；
- 记录种群和最优值；
- 教学清楚。

### pymoo

<https://github.com/anyoptimization/pymoo>

<https://pymoo.org/customization/binary.html>

<https://pymoo.org/constraints/index.html>

适合多目标：

- 主瓣；
- 旁瓣；
- 开启数量；
- 功耗；
- 状态切换数；
- 零陷；
- 鲁棒性。

### 正确推进顺序

```text
解析基线
→ 小阵列穷举
→ 固定种子随机搜索
→ 遗传算法
→ 多目标
→ 实测复响应
→ 数据驱动代理模型
```

不要一开始使用强化学习或神经网络。

---

## 9. 从控制码到真实响应

建立CSV：

```text
unit_id,state,amplitude,phase_deg,frequency_hz
0,0,0.82,15.3,3500000000
0,1,0.76,191.0,3500000000
...
```

仿真读取：

```python
c = amplitude * exp(1j * deg2rad(phase))
```

数据来源：

- CST/HFSS单元仿真；
- VNA/S参数反演；
- 暗室方向图；
- 文献中的近似值；
- 初期理想假设。

必须标记来源和频率，不能把理想值冒充实测值。

---

## 10. PIN二极管偏置基础

PIN二极管在RF中常用作开关：

- 正向偏置：呈较低RF阻抗；
- 反向/零偏：呈较高RF阻抗；
- 实际由串联电阻、结电容、封装和频率决定。

偏置网络常包括：

```text
控制电压
→ 限流电阻
→ RF choke/高阻线
→ PIN二极管
→ RF结构

RF路径
→ 隔直电容
```

项目边界：

- MCU/驱动板提供数字状态；
- 天线转接板产生合适偏置；
- RF choke、隔直、地和射频布局由天线设计决定；
- LED驱动输出不能未经评估直接接天线。

## 11. 天线接口需求表

林同学向天线组收集：

| 参数 | 必须明确 |
|---|---|
| 单元数 |  |
| 每单元二极管数 |  |
| 状态数 |  |
| 正向电流 |  |
| 正向电压 |  |
| 截止需要0 V还是负压 |  |
| 高侧/低侧 |  |
| 控制保持方式 |  |
| 最大切换率 |  |
| 公共阳极/阴极 |  |
| RF choke |  |
| 隔直 |  |
| 地关系 |  |
| 接口连接器 |  |
| 允许线长 |  |
| 状态到幅相响应 |  |

没有这张表，不制作真实天线转接板。

---

## 12. 拓展实验

### 实验A：LED控制码和阵列模型一致

1. 上位机生成16×16状态；
2. LED显示；
3. 保存同一`.npy`；
4. 仿真读取；
5. 生成方向图；
6. 报告“这是幅度掩膜模型”。

### 实验B：理想1 bit相位

1. 生成目标方向连续相位；
2. 量化±1；
3. LED显示0/1码；
4. 仿真把0/1映射为+1/-1；
5. 比较连续与1 bit；
6. 说明LED亮灭只是状态码。

### 实验C：实测复响应

1. 导入两状态幅相；
2. 重新计算；
3. 比较主瓣、旁瓣和损失；
4. 分析状态误差。

### 实验D：控制功耗约束

优化目标加入：

\[
P_{\mathrm{control}}
=
P_{\mathrm{MCU}}+
P_{\mathrm{driver}}+
N_{\mathrm{on}}P_{\mathrm{unit}}
\]

比较不同导通率或状态码的控制功耗。

---

## 13. 王、林共同验收

- [ ] 能区分0/1幅度和±1相位；
- [ ] 能解释控制码到复响应；
- [ ] 2×2基线正确；
- [ ] 16×16连续相位和1 bit结果；
- [ ] 报告全局主瓣而非局部峰；
- [ ] 随机搜索固定种子；
- [ ] LED与仿真共用同一状态文件；
- [ ] 不把阵列因子称为真实增益；
- [ ] 天线接口表完成；
- [ ] 真实响应有来源和频率。
