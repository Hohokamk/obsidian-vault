# 基于单片机的可扩展大规模阵列控制电路设计与实现

> 大创项目主入口。本仓库把申报材料、技术文档、软硬件代码、参考资料和 AI 协作记录放在同一个 Obsidian 目录里，README 负责回答三个问题：项目在做什么、材料在哪里、代码怎么跑。

## 1. 项目定位

本项目不是一块会显示图案的 LED 屏，而是一套面向大规模离散阵列单元的、可扩展、可测量的控制平台。

- 硬件主线：NUCLEO-G474RE 的 STM32G474RE 通过 SPI TX DMA 驱动 TLC6C598 低侧级联驱动芯片。
- 扩展路径：8 路芯片级联成 64 通道模块，4 个模块组成 256 路，驱动 16×16 LED 负载；架构预留向 1024 路、多链结构扩展。
- 软件主线：Python 上位机、二进制串口协议、随机压力测试、KiCad EDA 自动化和单一配置源 `array_config.yaml`。
- 拓展方向：将 LED 通断状态接入阵列因子模型，为实验室智能可调天线阵列预留偏置/开关控制接口。真实天线不列为硬性验收。

核心技术闭环：

```text
NUCLEO-G474RE
→ STM32G474RE SPI TX DMA
→ TLC6C598 8路低侧级联驱动
→ 8颗组成64通道模块
→ 4模块组成256路
→ 16×16 LED负载
→ Python CLI、自动测试、KiCad自动构建、阵列因子仿真
```

## 2. 团队成员

| 成员 | 专业 | 主要职责 |
| --- | --- | --- |
| 杨 | 电子信息工程 | 队长，硬件与系统集成，MCU、驱动器件、PCB、底层固件 |
| 林 | 通信工程 | 制作与测量，LED 装配、时序/电流/热测试、天线接口调研 |
| 王 | 计算机科学 | 软件、EDA 与算法，上位机、协议、自动测试、KiCad 自动化、阵列因子仿真 |

## 3. 目录导航

| 目录/文件 | 内容 |
| --- | --- |
| [申报/撰写思路与大纲.md](申报/撰写思路与大纲.md) | 申请书撰写思路、详细大纲、量化指标、答辩口径 |
| [资料/软硬件配置与代码资源总索引.md](资料/软硬件配置与代码资源总索引.md) | 全项目资源和代码入口的按问题索引 |
| [资料/相关资料.md](资料/相关资料.md) | 项目任务剖析、总体架构、测试方案与资料索引 |
| [资料/大规模阵列控制_软硬件配置与代码资源包_V2/README.md](资料/大规模阵列控制_软硬件配置与代码资源包_V2/README.md) | V2 资源包总说明和最短复现路径 |
| [starter_code_v2](starter_code_v2) | 轻量代码工作副本，含 `host`、`config` 和协议/图案生成代码 |
| [面试文件](面试文件) | 论文 `2508.06956v2.pdf`、名词解释和神经波束场论文汇报 PPT |
| [ai对话](ai对话) | 与 AI 的项目分层、学习计划和整体分析记录 |

最常用的三个入口：

- 想快速搞清楚整个项目：[资料/软硬件配置与代码资源总索引.md](资料/软硬件配置与代码资源总索引.md)
- 想写申请书：[申报/撰写思路与大纲.md](申报/撰写思路与大纲.md)
- 想直接跑代码：[资料/大规模阵列控制_软硬件配置与代码资源包_V2](资料/大规模阵列控制_软硬件配置与代码资源包_V2)

## 4. 代码快速开始

完整可运行代码在资源包内：

```text
资料/大规模阵列控制_软硬件配置与代码资源包_V2/starter_code/
├── code/
│   ├── host/            Python 上位机、协议、图案与压力测试
│   ├── firmware/        STM32 HAL 接入骨架（需接入 CubeMX 工程）
│   ├── automation/      映射生成、KiCad 检查脚本
│   ├── simulation/      阵列因子、方向图与二值优化
│   ├── tests/           pytest 回归测试
│   └── config/          array_config.yaml 单一配置源
├── requirements.txt
└── VALIDATION.md
```

离线测试（先建立 Python 3.12 虚拟环境）：

```powershell
cd "资料\大规模阵列控制_软硬件配置与代码资源包_V2\starter_code"
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest code\tests -q
```

协议 dry-run 示例：

```powershell
cd code\host
python arrayctl.py --dry-run ping
python arrayctl.py --dry-run one --row 3 --col 5
```

生成 256 通道映射：

```powershell
python code\automation\generate_mapping.py code\config\array_config.yaml --out generated
```

阵列因子仿真：

```powershell
cd code\simulation
python demo.py
```

根目录的 `starter_code_v2` 是一个轻量工作副本，主要保留 `host/arrayctl.py`、`host/protocol.py`、`host/patterns.py` 和 `config/array_config.yaml`，适合快速查看协议和图案生成逻辑；完整版本以资源包内的 `starter_code` 为准。

## 5. 当前状态

- 已验证：Python 代码可编译；11 项 pytest 通过；协议 dry-run 能生成 PING 和 256 路单点帧；映射能生成 256 项 CSV 与 C 头文件；阵列因子仿真可运行。
- 待实物验证：STM32CubeIDE 编译与下载；TLC6C598 8/16/64/256 路实物；KiCad 10 真实工程 ERC/DRC 与生产文件；逻辑分析仪和示波器波形；温升与 10 万帧压力测试。
- 固件注意：`array_driver.c` 是 HAL 接入骨架，不是可直接烧录的完整工程；SPI 真正结束标志需按 RM0440 和所选 CubeG4 版本核对。

## 6. 项目边界与原则

- LED 是可视化验收负载，不是项目目的本身；智能天线是拓展方向，不是结题前提。
- 基础目标 256 路独立输出，挑战目标 1024 路；不承诺 AI 全自动 PCB 设计。
- 以 `array_config.yaml` 作为唯一配置源，统一硬件编号、固件映射、上位机和仿真坐标。
- 外部代码分四级使用：官方数据手册/文档优先，第三方示例只能对照，电气指标必须以实物测量为准。
- 不得跳过的实物验证清单见 [软硬件配置与代码资源总索引.md](资料/软硬件配置与代码资源总索引.md) 第 7 节。
