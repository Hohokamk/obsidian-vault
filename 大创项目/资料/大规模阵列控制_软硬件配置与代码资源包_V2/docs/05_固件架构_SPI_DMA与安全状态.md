# 05 固件架构、SPI/DMA与安全状态

## 1. 固件分层

```text
App
├── pattern_player
├── safety_manager
└── status_report

Protocol
├── stream_parser
├── command_dispatch
├── CRC16
└── ACK/error

Array
├── logical_mapping
├── frame_buffers
└── module_config

Driver
├── spi_dma_tx
├── latch
├── output_enable
├── clear
└── serial_readback

HAL
├── STM32 HAL/LL
└── board pins
```

不要把协议解析、SPI发送、映射和应用逻辑全部写在`main.c`。

## 2. 状态机

```text
SAFE_OFF
  ↓ 初始化完成
IDLE
  ↓ 新完整帧
TX_DMA
  ↓ DMA回调
WAIT_SPI_END
  ↓ EOT/TXC/BSY确认
LATCH
  ↓
IDLE
```

异常：

```text
任何状态
  ↓ 超时/SPI错误/看门狗/协议错误阈值
ERROR_SAFE
  ↓ OE关闭
```

## 3. 双缓冲

```c
uint8_t frame_a[FRAME_BYTES];
uint8_t frame_b[FRAME_BYTES];

uint8_t *front = frame_a;
uint8_t *back  = frame_b;
```

协议将完整数据写入`back`。CRC、长度和序列号均通过后：

```c
swap(front, back);
request_send = true;
```

不要在DMA读取`front`时修改它。

## 4. 32 B为什么是256路

```c
#define CHANNELS 256
#define FRAME_BYTES ((CHANNELS + 7) / 8)
```

置位：

```c
void bit_set(uint8_t *frame, uint16_t index, bool on)
{
    uint16_t byte = index / 8;
    uint8_t bit = index % 8;

    if (on) {
        frame[byte] |= (uint8_t)(1u << bit);
    } else {
        frame[byte] &= (uint8_t)~(1u << bit);
    }
}
```

物理位序由映射层决定，不要在驱动层到处反转。

## 5. SPI DMA发送

建议接口：

```c
typedef enum {
    ARRAY_OK = 0,
    ARRAY_BUSY,
    ARRAY_BAD_LENGTH,
    ARRAY_HAL_ERROR,
    ARRAY_TIMEOUT
} array_status_t;

array_status_t array_submit_frame(const uint8_t *data, size_t len);
void array_poll(void);
void array_on_spi_tx_complete(SPI_HandleTypeDef *hspi);
void array_on_spi_error(SPI_HandleTypeDef *hspi);
```

提交函数：

1. 检查长度；
2. 检查当前状态；
3. 复制或交换稳定缓冲；
4. 保持当前输出；
5. 启动DMA；
6. 设置超时计时；
7. 返回，不阻塞。

## 6. DMA回调

回调只做短操作：

```c
void array_on_spi_tx_complete(SPI_HandleTypeDef *hspi)
{
    if (hspi != &hspi1) return;
    dma_complete_flag = true;
}
```

不要在中断里：

- `printf`大量内容；
- 等待BSY；
- 延时；
- 解析下一帧；
- 操作GUI；
- 做复杂映射。

## 7. 等待SPI真正结束

伪代码：

```c
static bool spi_shift_finished(void)
{
    /* 根据G474所用SPI实例、HAL版本和AN5543实现。
       可能检查EOT/TXC，老版本可能涉及BSY。 */
    return __HAL_SPI_GET_FLAG(&hspi1, SPI_FLAG_TXC);
}
```

实际宏名需查当前HAL。不要把这段伪代码直接复制后不编译核对。

## 8. 锁存

```c
static inline void latch_pulse(void)
{
    HAL_GPIO_WritePin(LATCH_GPIO_Port, LATCH_Pin, GPIO_PIN_SET);
    __NOP();
    __NOP();
    HAL_GPIO_WritePin(LATCH_GPIO_Port, LATCH_Pin, GPIO_PIN_RESET);
}
```

脉冲宽度需满足数据手册。若GPIO和CPU很快，两个NOP是否足够必须通过逻辑分析仪确认；也可用定时器或更明确的微秒延迟。

## 9. OE安全策略

### 上电

硬件10 kΩ上拉使OE关闭。

固件初始化：

```c
OE_OFF();
LATCH_LOW();
CLR_ASSERT();
delay_us(1);
CLR_RELEASE();
```

只在以下条件全部满足后：

- GPIO初始化；
- SPI初始化；
- 输出寄存器已锁存全0；
- 系统无错误；

才执行`OE_ON()`。

### 通信中断

建议默认：

- 超过设定时间无有效命令；
- 输出关闭；
- 状态记录`COMM_TIMEOUT`；
- 收到显式恢复命令后重新启用。

若未来天线要求保持最后状态，可增加配置，但LED核心验收采用安全关闭。

## 10. 协议

建议帧：

```text
SOF0 0xA5
SOF1 0x5A
VERSION
COMMAND
SEQUENCE_L
SEQUENCE_H
LENGTH_L
LENGTH_H
PAYLOAD
CRC16_H
CRC16_L
```

命令：

```text
PING
GET_STATUS
SET_FRAME
ALL_OFF
SET_CHANNEL
PLAY_PATTERN
STOP
CLEAR_ERRORS
ENTER_SAFE
```

CRC16-CCITT测试向量：

```text
"123456789" → 0x29B1
```

starter_code中已有Python和C骨架。

## 11. ACK

ACK payload建议：

```text
status
active_channels
error_flags
last_sequence
spi_error_count
readback_error_count
supply_mv（可选）
temperature（可选）
```

压力测试必须根据序列号匹配ACK，不能只看到“有回复”。

## 12. 串行回读

如果SER_OUT接MISO：

```c
HAL_SPI_TransmitReceive_DMA(&hspi1, tx, rx, FRAME_BYTES);
```

链中输出的是旧移位内容。流程：

1. 已知当前链内容A；
2. 发送B，同时接收；
3. 理论接收A；
4. 比较；
5. 锁存B；
6. 更新期望旧内容；
7. 统计位错误。

注意芯片级联和字节顺序可能使接收数据需要重新排列。

## 13. 超时

理论移位时间：

\[
T=\frac{N}{f_{\mathrm{SCLK}}}
\]

实际超时可设：

```text
timeout = 理论时间 × 5 + 固定裕量
```

例：256 bit、1 MHz约256 μs，可先设2 ms。超时后：

- OE关闭；
- 中止SPI/DMA；
- 错误计数；
- 不锁存半帧；
- 等待恢复。

## 14. 看门狗

核心功能稳定后启用IWDG：

- 主循环和关键任务正常才喂狗；
- DMA中断卡死不能持续喂狗；
- 复位后OE硬件仍关闭；
- 复位原因写入状态；
- 不要在所有中断里随意喂狗。

## 15. 测试

### PC侧单元测试

- CRC；
- 编解码；
- 映射；
- 固定随机种子；
- 长度错误；
- 噪声流解析。

### MCU侧

- CRC测试向量；
- 非法长度；
- 重复序列号；
- DMA忙；
- 超时；
- SPI错误；
- 通信中断；
- 上电安全。

### 硬件在环

- SET_FRAME；
- SER_OUT旧帧回读；
- LED/视觉输出；
- ACK；
- 10万帧统计。

## 16. starter_code接入

目录：

```text
starter_code/code/firmware/
├── array_driver.c
├── array_driver.h
├── protocol.c
└── protocol.h
```

接入步骤：

1. CubeMX创建工程；
2. 复制文件到`App`或`Drivers`；
3. 修改HAL include；
4. 注入`hspi`、GPIO端口和引脚；
5. 将HAL回调转发给驱动；
6. 初始`FRAME_BYTES=1`；
7. 8路成功后改2、8、32；
8. 每次扩展都跑回归测试；
9. 不一次直接改到256路。
