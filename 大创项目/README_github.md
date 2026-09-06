# 大规模阵列控制

用单片机和少量串行引脚，稳定控制 256 路独立输出，并预留扩展到 1024 路的能力。LED 阵列用来直观地验收硬件链路，同一套控制状态还可以接入阵列因子模型，向智能可调天线阵列拓展。

## 这个项目解决什么问题

要同时控制几百个独立的开关或负载时，单片机 GPIO 数量不够，直接逐个引脚控制行不通。本项目的思路是：

1. MCU 通过 SPI 和 DMA 把数据快速串行推出去；
2. TLC6C598 这类移位寄存器把串行数据展开成多路输出；
3. 多个芯片级联组成 64 通道模块；
4. 4 个模块拼成 256 路，驱动一块 16×16 LED 阵列；
5. 用统一锁存让所有通道在同一时刻更新，避免逐个翻转产生的中间状态。

## 代码能做什么

- 用 `array_config.yaml` 统一描述阵列规模、通道映射和硬件参数；
- 生成全亮、全灭、单点、行列、棋盘格、随机等测试图案；
- 把图案编码成带 CRC 校验的二进制串口帧；
- 通过 `arrayctl.py` 命令行走通完整链路（当前支持 dry-run 调试）；
- 自动生成逻辑坐标到物理通道的映射 CSV 和 C 头文件；
- 计算阵列因子和方向图，演示二值状态优化；
- 用 pytest 对协议、图案和阵列因子做回归测试。

## 环境准备

建议使用 Python 3.12：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

核心依赖：`numpy`、`matplotlib`、`PyYAML`。串口通信需要 `pyserial`，视觉核验需要 `opencv-python`，测试需要 `pytest`。

## 快速开始

跑一遍测试：

```powershell
pytest code\tests -q
```

不接硬件，先看协议帧：

```powershell
cd code\host
python arrayctl.py --dry-run ping
python arrayctl.py --dry-run one --row 3 --col 5
```

生成 256 路映射文件：

```powershell
python code\automation\generate_mapping.py code\config\array_config.yaml --out generated
```

运行阵列因子仿真：

```powershell
cd code\simulation
python demo.py
```

## 目录结构

```text
.
├── code/
│   ├── host/          Python 上位机、协议、图案生成与压力测试
│   ├── firmware/      STM32 HAL 接入骨架（需放进 CubeMX 工程）
│   ├── automation/    映射生成与 KiCad 自动化脚本
│   ├── simulation/    阵列因子、方向图与二值优化
│   ├── tests/         pytest 回归测试
│   └── config/        单一配置源 array_config.yaml
├── requirements.txt
└── README.md
```

## 当前状态

已经可以离线验证的部分：

- 协议编码/解码和 CRC 校验通过测试；
- 256 路图案能正确打包成 32 字节帧；
- 映射脚本能生成 CSV 和 C 头文件；
- 阵列因子仿真可以运行。

还需要在真实硬件上完成的部分：

- STM32CubeIDE 编译和下载到 NUCLEO-G474RE；
- TLC6C598 从 8 路到 256 路的实物联调；
- 逻辑分析仪和示波器时序验证；
- 电流一致性、温升和长时间压力测试；
- KiCad 真实工程的 ERC/DRC 与生产文件导出。

## 注意

`code/firmware/array_driver.c` 是需要接入 CubeMX 生成工程的 HAL 骨架，不是可以直接烧录的完整工程。SPI 传输真正结束的标志，要按 STM32G474 的参考手册 RM0440 和实际使用的 CubeG4 版本确认。

