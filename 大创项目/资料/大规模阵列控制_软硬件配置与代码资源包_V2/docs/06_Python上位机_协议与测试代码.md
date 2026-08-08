# 06 Python上位机、协议与测试代码

## 1. 官方与成熟资源

### Python虚拟环境

<https://docs.python.org/3.12/library/venv.html>

用途：

- 为项目建立隔离依赖；
- 避免三人的全局Python包互相冲突；
- 能够通过`requirements.txt`重建。

### pySerial

<https://pyserial.readthedocs.io/en/latest/>

用途：

- 串口发现；
- 打开ST-LINK虚拟串口；
- 设置波特率和超时；
- 发送二进制帧；
- 读取ACK；
- 在Windows和Linux保持相同API。

### pytest

<https://docs.pytest.org/en/stable/>

用途：

- CRC；
- 帧协议；
- 流式解析；
- 映射；
- 图案；
- 阵列因子；
- 未来视觉算法。

### NumPy

<https://numpy.org/doc/stable/>

用途：

- 16×16状态矩阵；
- 固定种子随机图案；
- 打包、保存和比较；
- 阵列数值计算。

### PyYAML

<https://pyyaml.org/wiki/PyYAMLDocumentation>

用途：

- 读取唯一配置源；
- 不把通道数、模块数和位序硬编码在多个文件中。

---

## 2. 安装和首次验证

在资源包根目录：

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r starter_code\requirements.txt
pytest starter_code\code\tests -q
```

### Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r starter_code/requirements.txt
pytest starter_code/code/tests -q
```

预期：

```text
11 passed
```

若测试不通过，不连接硬件，先排除环境和代码问题。

---

## 3. starter_code结构

```text
starter_code/code/
├── config/
│   └── array_config.yaml
├── host/
│   ├── protocol.py
│   ├── patterns.py
│   ├── device.py
│   ├── arrayctl.py
│   └── stress_test.py
├── tests/
│   ├── test_protocol.py
│   ├── test_patterns.py
│   └── test_array_factor.py
└── simulation/
```

### 文件职责

- `protocol.py`：只负责字节协议，不知道LED和阵列；
- `patterns.py`：只负责二维状态、映射和位打包；
- `device.py`：只负责串口事务、超时和ACK；
- `arrayctl.py`：命令行入口；
- `stress_test.py`：大量随机帧；
- `array_config.yaml`：规模和映射；
- `tests/`：修改代码后防止旧功能被破坏。

这种分层能避免把“串口、图案、映射和用户界面”写在一个脚本里。

---

## 4. 二进制协议原理

帧格式：

```text
A5 5A
version:u8
command:u8
sequence:u16 little-endian
length:u16 little-endian
payload:length bytes
crc16:u16 little-endian
```

CRC覆盖：

```text
version → payload最后一个字节
```

不覆盖SOF和CRC本身。

### 为什么需要SOF

串口是连续字节流，没有天然“消息边界”。若中间丢了一个字节，接收端需要重新寻找`A5 5A`。

### 为什么需要长度

接收端知道还要等待多少字节，支持：

- 0字节PING；
- 32字节256路帧；
- 128字节1024路帧；
- 未来状态表和日志。

### 为什么需要序列号

压力测试时必须知道ACK属于哪一个命令。序列号循环0～65535。

### 为什么需要CRC

CRC检测：

- 传输噪声；
- 丢字节；
- 错位；
- 软件打包错误。

CRC不能检测LED是否接反，也不能证明驱动链正确，因此还需要SER_OUT和物理输出测试。

---

## 5. `protocol.py`逐段解释

### `crc16_ccitt`

```python
crc16_ccitt(b"123456789") == 0x29B1
```

这是标准CRC-16/CCITT-FALSE测试向量。Python与C必须得到相同值。

### `encode_frame`

它依次完成：

1. 把payload转为不可变`bytes`；
2. 检查最大长度；
3. 检查序列号；
4. 按小端打包头；
5. 计算CRC；
6. 拼接完整帧。

### `decode_frame`

它验证：

- 最小长度；
- SOF；
- payload长度；
- 总长度；
- CRC；
- 再返回结构化Frame。

### `StreamParser`

真实串口一次`read()`可能得到：

- 半个帧；
- 多个帧；
- 帧前噪声；
- 损坏帧；
- `A5`和`5A`分两次到达。

增量解析器把新字节加入缓存，找到SOF后按长度等待完整帧。CRC失败时丢弃一个字节并继续搜索，避免永远失步。

---

## 6. 协议离线实验

```powershell
cd starter_code\code\host
python arrayctl.py --dry-run ping
python arrayctl.py --dry-run off
python arrayctl.py --dry-run one --row 3 --col 5
python arrayctl.py --dry-run checker
python arrayctl.py --dry-run random --seed 2026 --density 0.25
```

`--dry-run`不需要串口，会显示：

- 命令；
- payload字节数；
- 完整十六进制帧。

学生应手工检查一次：

- 256路payload是否32 B；
- `one`是否只有一个bit；
- CRC是否随payload变化；
- 同一seed是否生成相同字节。

---

## 7. `patterns.py`原理

## 7.1 逻辑矩阵

上位机将图案表示成：

```python
pattern.shape == (16, 16)
pattern.dtype == uint8
pattern取值只能0或1
```

这样适合教师和学生理解二维坐标。

## 7.2 映射

```python
physical[mapping[logical_index]] = logical[logical_index]
```

例如：

```text
逻辑(0,0) → physical 63
逻辑(0,1) → physical 62
```

当PCB翻转、模块旋转或芯片级联顺序变化时，只修改映射。

## 7.3 位打包

8个通道压成1字节：

```text
physical 0..7 → byte 0
physical 8..15 → byte 1
...
```

`bit_order_within_byte`决定physical 0对应bit0还是bit7。

注意：

- “字节内MSB first”；
- “SPI在导线上先发哪个字节”；
- “第一颗芯片还是最后一颗获得第一个字节”；

是三个不同层次。必须通过16路实验确认。

---

## 8. 配置文件

`array_config.yaml`：

```yaml
array:
  rows: 16
  cols: 16
  channels: 256

hardware:
  channels_per_driver: 8
  drivers_per_module: 8
  channels_per_module: 64
  modules: 4
  chains: 1
  driver: TLC6C598

serialization:
  bit_order_within_byte: lsb_first
  byte_order_on_wire: physical_ascending
  active_high_logical: true

mapping:
  type: identity
```

### 从8路开始

实验初期改为：

```yaml
array:
  rows: 1
  cols: 8
  channels: 8
hardware:
  channels_per_module: 8
  modules: 1
```

16路：

```yaml
array:
  rows: 2
  cols: 8
  channels: 16
```

不要一开始就用256路配置调8路硬件，否则很难区分长度、映射和硬件问题。

---

## 9. 串口设备类

`device.py`实现一次事务：

```text
生成序列号
→ 编码帧
→ 清输入缓存
→ 写串口
→ 等ACK
→ 检查序列号
→ 检查状态
→ 返回往返时间
```

### 为什么有重试

串口刚打开、MCU复位或偶发噪声可能导致超时。默认有限次重试，但不能无限重试掩盖硬件问题。

### 为什么每次清输入缓存

早期调试时可能残留旧日志。正式协议稳定后，若设备持续主动上报，不能粗暴清空，需要改为统一接收线程和消息分发。

---

## 10. 硬件命令

列串口：

```powershell
python starter_code\code\host\arrayctl.py ports
```

PING：

```powershell
python starter_code\code\host\arrayctl.py --port COM5 ping
```

全关：

```powershell
python starter_code\code\host\arrayctl.py --port COM5 off
```

单点：

```powershell
python starter_code\code\host\arrayctl.py --port COM5 one --row 3 --col 5
```

随机：

```powershell
python starter_code\code\host\arrayctl.py --port COM5 random --seed 2026 --density 0.5
```

Linux改端口：

```bash
--port /dev/ttyACM0
```

---

## 11. 压力测试

示例：

```powershell
python starter_code\code\host\stress_test.py `
  --port COM5 `
  --frames 100000 `
  --seed 2026 `
  --density 0.5 `
  --csv measurements\stress_100k.csv
```

建议先做：

```text
100帧
1000帧
10000帧
100000帧
```

每级确认：

- ACK数量；
- 超时；
-设备错误；
- 平均/最大往返；
- 实际帧率；
- MCU错误计数；
- SER_OUT错误；
- 视觉或电气输出错误。

### 固定种子

固定种子使失败可复现。日志要记录：

```text
seed=2026
frame_index=38472
```

发生错误后可以重新生成同一帧。

---

## 12. 端到端速率

串口921600 bit/s，考虑起止位，实际每字节约10 bit。

256路SET_FRAME大致：

```text
2 SOF + 6 header + 32 payload + 2 CRC = 42 B
```

理论串口发送时间约：

\[
42\times10 / 921600\approx456\ \mu s
\]

再加ACK、操作系统调度和MCU处理，端到端1000帧/s可能接近串口上限。因而要区分：

- SPI板级1000帧/s；
- PC持续流；
- GUI交互。

高帧率拓展可采用：

- 板载模式表；
- 批量上传后定时播放；
- USB CDC高效读写；
- 更高波特率；
- 二进制ACK精简；
- 批量ACK。

---

## 13. 建议新增命令

### `UPLOAD_PATTERN_TABLE`

一次上传多帧：

```text
pattern_count
frame_bytes
frame0
frame1
...
```

### `PLAY`

参数：

```text
start_index
count
period_us
repeat
```

优点：

- MCU定时器确定播放；
- 避免PC操作系统抖动；
- 可以真正测板级1000帧/s。

### `GET_COUNTERS`

返回：

- valid_frames；
- bad_crc；
- bad_length；
- SPI DMA errors；
- timeouts；
- serial readback errors；
- watchdog resets。

---

## 14. Python代码改动规则

每次改动必须：

```bash
pytest starter_code/code/tests -q
```

新增功能同时新增测试。

例：

- 支持蛇形映射 → 加映射测试；
- 支持1024路 → 加128 B长度测试；
- 改CRC → Python和C共同测试；
- 改字节顺序 → pack/unpack回环测试；
- 加新命令 → 编码/解码测试。

---

## 15. 王同学前六周输出

1. Python环境说明；
2. 11项测试通过截图/日志；
3. `--dry-run`命令演示；
4. 8路配置；
5. 16路配置和映射；
6. 串口PING；
7. 单点与棋盘格；
8. 1000帧压力测试；
9. CSV日志；
10. README由林同学独立复现。
