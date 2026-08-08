# 07 KiCad、EDA自动化与生产文件

## 1. 官方资源

### KiCad 10入门

<https://docs.kicad.org/10.0/en/getting_started_in_kicad/getting_started_in_kicad.html>

### KiCad命令行

<https://docs.kicad.org/10.0/en/cli/cli.html>

官方CLI可以执行：

- 原理图ERC；
- PCB DRC；
- 原理图PDF；
- BOM；
- Gerber；
- 钻孔；
- SVG、DXF、STEP等导出。

### KiBot

文档：

<https://kibot.readthedocs.io/en/latest/>

仓库：

<https://github.com/INTI-CMNB/KiBot>

KiBot适合：

- 多种产物统一配置；
- CI；
- BOM；
- 装配图；
- 网页报告；
- 打包；
- 可选3D渲染。

本项目硬基线是`kicad-cli`。KiBot是上层工具，不因KiBot配置失败而阻塞基本生产文件。

---

## 2. KiCad工程目录

```text
hardware/driver_64ch/
├── driver_64ch.kicad_pro
├── driver_64ch.kicad_sch
├── driver_64ch.kicad_pcb
├── symbols/
├── footprints/
├── 3dmodels/
├── production/
├── reports/
└── README.md
```

自定义库放在项目内，避免只存在某一台电脑的全局库。

---

## 3. 原理图工作顺序

1. 建项目；
2. 建电源网络；
3. 放一颗TLC6C598；
4. 接逻辑信号；
5. 放去耦；
6. 放8路输出；
7. ERC；
8. 完成单颗通道审查；
9. 再复制8颗；
10. 级联SER；
11. 加连接器和测试点；
12. 加模块ID、保险和阻尼；
13. 分层次网标；
14. 完整ERC；
15. 导出PDF交叉评审。

不要先复制8颗再找单颗错误。

---

## 4. 重复电路怎样减少人工错误

### 方法A：层次化原理图

建立`driver_8ch`层次页，实例化8次。优点：

- 电路结构一致；
- 修改一处同步；
- 阅读清楚。

但级联输入输出和参考标号仍需检查。

### 方法B：复制后脚本核对

用Python导出或读取BOM/网表，检查：

- U1～U8；
- 每颗一个0.1 μF；
- SER链连续；
- 每颗8路输出；
- 无重复通道；
- 64路完整。

### 方法C：SKiDL探索

<https://github.com/devbisme/skidl>

用途：

- 用Python描述规则化电路；
- 生成网表；
- 学习“电路即代码”。

限制：

- 不作为首版唯一设计源；
- 最终可读原理图和PCB仍需人工评审；
- 软件版本变化可能影响输出；
- 不用它自动决定电气设计。

---

## 5. 封装与3D检查

每个新封装：

1. 数据手册封装图；
2. KiCad封装尺寸；
3. 1脚；
4. 焊盘间距；
5. 丝印；
6. Courtyard；
7. 3D方向；
8. 打印1:1纸张；
9. 将实物芯片放在打印图上；
10. 再允许进入正式PCB。

连接器必须核对“从上看”和“插接面看”的区别。

---

## 6. kicad-cli命令

先执行：

```bash
kicad-cli version
kicad-cli --help
kicad-cli sch --help
kicad-cli pcb --help
```

### ERC

```bash
kicad-cli sch erc \
  --exit-code-violations \
  --output reports/erc.rpt \
  hardware/driver_64ch/driver_64ch.kicad_sch
```

### DRC

```bash
kicad-cli pcb drc \
  --exit-code-violations \
  --schematic-parity \
  --output reports/drc.rpt \
  hardware/driver_64ch/driver_64ch.kicad_pcb
```

### 原理图PDF

```bash
kicad-cli sch export pdf \
  --output production/driver_64ch_schematic.pdf \
  hardware/driver_64ch/driver_64ch.kicad_sch
```

### Gerber

```bash
kicad-cli pcb export gerbers \
  --output production/gerber/ \
  --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts \
  hardware/driver_64ch/driver_64ch.kicad_pcb
```

具体层名和参数以安装版本`--help`为准。

### 钻孔

```bash
kicad-cli pcb export drill \
  --output production/drill/ \
  --generate-map \
  --generate-report \
  hardware/driver_64ch/driver_64ch.kicad_pcb
```

### STEP

```bash
kicad-cli pcb export step \
  --output production/driver_64ch.step \
  hardware/driver_64ch/driver_64ch.kicad_pcb
```

KiCad 10 的导出命令位于 `pcb export ...` 或 `sch export ...` 子命令下。不同10.0小版本的可选参数可能变化，仍需以本机 `--help` 为准。

---

## 7. starter_code自动化脚本

```text
starter_code/code/automation/
├── generate_mapping.py
├── run_kicad_checks.sh
└── kibot.yaml
```

### `generate_mapping.py`

输入：

```text
array_config.yaml
```

输出：

```text
logical_to_physical.csv
array_mapping_generated.h
source_sha256.txt
```

运行：

```bash
python starter_code/code/automation/generate_mapping.py \
  starter_code/code/config/array_config.yaml \
  --out generated
```

意义：

- Python、固件、PCB丝印和测试使用同一映射；
- 头文件含源配置SHA256；
- 不允许手工改生成文件；
- 修改配置后重新生成。

---

## 8. KiBot快速开始

安装方式应按官方文档和项目系统选择。验证：

```bash
kibot --version
kibot --help
```

官方快速生成配置：

```bash
kibot --quick-start
```

先使用：

```bash
kibot --dry
```

确认配置和输入，再真实输出。

建议输出：

- ERC；
- DRC；
- Gerber；
- drill；
- BOM；
- schematic PDF；
- PCB PDF；
- 3D截图；
- 制造ZIP；
- HTML导航页。

---

## 9. 持续集成

GitHub Actions示意：

```yaml
name: hardware-ci
on:
  push:
    paths:
      - "hardware/**"
      - "automation/**"
  pull_request:
    paths:
      - "hardware/**"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run KiBot
        uses: INTI-CMNB/KiBot@v2_k10
        with:
          config: automation/kibot.yaml
          dir: hardware/driver_64ch
          schema: hardware/driver_64ch/driver_64ch.kicad_sch
          board: hardware/driver_64ch/driver_64ch.kicad_pcb
      - uses: actions/upload-artifact@v4
        with:
          name: fabrication
          path: hardware/driver_64ch/out
```

注意：

- Action标签必须按KiBot当前文档核对并固定；
- 不用`latest`；
- CI成功不等于电气正确；
- 下单前人工检查Gerber；
- native variant在KiCad 10环境仍需谨慎。

---

## 10. 自动检查内容

王同学编写脚本检查：

- 驱动器数量等于8；
- 0.1 μF数量不少于8；
- 输出标号0～63无缺失；
- 模块连接器引脚完整；
- 测试点存在；
- BOM无未知料号；
- 所有自定义封装存在；
- 生产包包含要求文件；
- 配置通道数与硬件文档一致。

脚本不能验证：

- 电容是否真的靠近芯片；
- 时钟走线是否合理；
- 电源铜皮是否足够；
- 接插件方向是否适合装配；
- RF偏置是否正确。

这些仍需人看PCB。

---

## 11. PCB审查会议

### 第一轮：原理图

主持：杨  
检查：林、王

- 电气逻辑；
- 安全状态；
- 电源；
- 级联；
- 测试点；
- 输出接口；
- 元件可采购。

### 第二轮：PCB

主持：林

- 封装；
- 焊接；
- 连接器方向；
- 测试可达性；
- 丝印；
- 电源和地；
- 时钟回流；
- 机械装配。

### 第三轮：自动化与生产

主持：王

- ERC/DRC；
- BOM；
- Gerber；
- 钻孔；
- 配置SHA；
- 文件版本；
- ZIP；
- 新电脑能否生成。

最后教师签字或在问题单中确认后再下单。

---

## 12. 制板包目录

```text
production/HW-A0_2026xxxx/
├── README.txt
├── schematic.pdf
├── gerber/
├── drill/
├── bom.csv
├── positions.csv
├── stackup.txt
├── board.png
├── 3d_front.png
├── 3d_back.png
├── erc.rpt
├── drc.rpt
├── source_commit.txt
├── config_sha256.txt
└── fabrication.zip
```

README写：

- 板版本；
- KiCad版本；
- Git提交；
- 层数；
- 板厚；
- 铜厚；
- 阻焊；
- 表面处理；
- 特殊说明；
- 已知问题。

---

## 13. EDA拓展研究

核心完成后可探索：

1. 自动生成输出丝印；
2. 自动放置规则阵列；
3. 从YAML生成连接器针脚表；
4. BOM价格和库存检查；
5. PCB版本差异报告；
6. 使用KiCad IPC API；
7. 用SKiDL生成候选网表；
8. AI辅助阅读ERC/DRC和数据手册。

不把“全自动布线”作为验收目标，因为：

- 自动布线不理解本项目供电与回流优先级；
- 结果仍需工程判断；
- 可能耗费大量时间调工具而不是完成硬件。

---

## 14. 王同学EDA验收

- [ ] 统一KiCad版本；
- [ ] 运行ERC/DRC；
- [ ] 严重错误使脚本退出非0；
- [ ] 自动生成生产文件；
- [ ] 映射头文件和CSV；
- [ ] 制板包包含提交号；
- [ ] 在另一台电脑复现；
- [ ] 人工Gerber检查记录；
- [ ] 不依赖个人全局库；
- [ ] 所有自动化限制写入README。
