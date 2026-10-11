# 达妙电机缓冲区索引口径不一致

## 一、问题概述

| 项 | 内容 |
|---|---|
| 模块 | 达妙（DM）电机 CAN 通信链路 |
| 涉及文件 | `can.h` / `can.cpp` / `HTmotor.h` / `HTmotor.cpp` / `taskslist.cpp` |
| 问题类型 | 索引口径不一致 —— 收发两端对"槽位"的编号规则不统一 |
| 严重程度 | 高。会导致电机拿别的电机的反馈做闭环，**且不报错、不崩溃** |
| 当前状态 | 收（反馈）支路已修；发（控制）支路待修 |

## 二、背景

达妙电机 2 台，均挂在 can 2：

| 对象 | 电机 | CAN_ID | 工作模式 | `function` |
|---|---|---|---|---|
| `DMmotor[0]` | Pitch | `0x09` | 位置速度 | `P_S` |
| `DMmotor[1]` | Yaw | `0x06` | 速度 | `SPEED` |

`CAN` 类里有两个 8 字节缓冲区（`can.h:44–45`）：

```cpp
uint8_t jointpdata[6][8]{};   // 发送缓冲：要发给电机的指令
uint8_t jointidata[6][8];     // 接收缓冲：电机反馈的原始字节
```

两者都是 6 行 × 8 字节，**每行 = 一台电机的一个"槽"**。

## 三、问题定义

"索引口径" = **决定"第几个槽给哪台电机"的规则**。

| 口径 | 规则 | 例子 |
|---|---|---|
| 按位置 | 在 `DMmotor` 数组里排第几，就用第几号槽 | Pitch 排 0 → 槽 0 |
| 按 ID | 槽号由 CAN_ID 换算 | Pitch `0x09` → 槽 9 |

`jointidata` 和 `jointpdata` 是两个独立数组，**同一台电机在两者中的槽号必须相同**，否则"读自己反馈"和"发自己指令"就对不上。

## 四、根因

### 4.1 收（反馈）支路 —— 按位置，正确

`can.cpp:145–150`：

```cpp
for (uint8_t i = 0; i < sizeof(DMmotor) / sizeof(DMmotor[0]); i++)
    if ((hcan->pRxMsg->Data[0] & 0x0F) == (DMmotor[i].ID & 0x0F))
    { memcpy(can2.jointidata[i], hcan->pRxMsg->Data, 8); break; }
```

槽号 = 循环下标 `i` = 数组位置。✔

### 4.2 发（控制）支路 —— 按外部传入的数字，错误

`HTmotor.cpp:45`（修改前）：

```cpp
can2.Transmit(id + 0x100, can2.jointpdata[id - 1], 8);
//                          ^^^^^^^^^^^^^^^^^ 槽号来自函数参数 id
```

槽号 = `id - 1`，`id` 由调用点传入。**槽号的来源与"电机在数组中的位置"没有任何绑定关系**，只是调用点碰巧传了能凑对的值。

### 4.3 叠加后果：串台

`taskslist.cpp:86–89`：

```cpp
DMmotor[0].State_Decode(can2.jointidata)
    .DMmotor_Ontimer(DMmotor[0].Kp, DMmotor[0].Kd, can2.jointpdata[0]);
```

这两行**一个字都没提 CAN_ID**，它靠"下标 0"把读和写绑成同一台电机。正确性完全依赖一个隐含前提：两条路写/读 `[0]` 时装的是同一台电机的数据。

一旦两条路口径不同（例如有人把回调改成按 ID 排序）：

| | 槽 0 装的是 | 槽 1 装的是 |
|---|---|---|
| 收（按 ID） | Yaw 的反馈 | Pitch 的反馈 |
| 发（按位置） | 发给 Pitch | 发给 Yaw |

结果：Pitch 从 `jointidata[0]` 读到的是 **Yaw 的转速**，用它做闭环。两台电机互相把对方的数据当自己的用。

**故障特征**：无编译错误、无运行时报错、无崩溃，只是行为诡异。定位成本极高。

## 五、修复方案

**原则：两条路的槽号统一为"数组位置"，且都由对象自身（`this`）推导，不从外部传入。**

`can.cpp` 收侧不动。只需改 `HTmotor.cpp` 的 `DMmotor_transmit`：

```cpp
// 修改前
void DMMOTOR::DMmotor_transmit(uint32_t id)
{
	can2.Transmit(id + 0x100, can2.jointpdata[id - 1], 8);
}

// 修改后
void DMMOTOR::DMmotor_transmit(CAN& hcan)
{
	uint8_t slot = 0xFF;
	for (uint8_t i = 0; i < sizeof(DMmotor) / sizeof(DMmotor[0]); i++)
		if (&DMmotor[i] == this) { slot = i; break; }//获取当前电机的索引
	if (slot == 0xFF) return;

	uint32_t offset;//协议规定的控制帧 ID 偏移
	switch (function)
	{
	case MIT:   offset = 0x000; break;//MIT：控制帧 ID = CAN_ID
	case P_S:   offset = 0x100; break;//位置速度模式
	case SPEED: offset = 0x200; break;//速度模式
	default:    return;
	}
	hcan.Transmit(ID + offset, hcan.jointpdata[slot], 8);
}
```

三个要点：

1. 槽号 `slot` 由 `this` 反查数组下标得到，与 `State_Decode`（`HTmotor.cpp:23–27`）**同一套写法**。
2. `slot` 初值 `0xFF` + 判空，防御"该对象不在 `DMmotor` 数组内"的调用。
3. 同一函数里的 ID 算式一并修正（见第六节）。

修复后的口径：

| 缓冲 | 写入 / 读取方 | 槽号来源 | 取值 |
|---|---|---|---|
| `jointidata[i]` | `can.cpp` 回调 | `for` 下标 | 0 / 1 |
| `jointpdata[slot]` | `DMmotor_transmit` | `this` 反查 | 0 / 1 |

两者都是"在 `DMmotor` 里排第几" —— 这才是链路能对的唯一依据。

## 六、附属问题（同批修复）

### 6.1 仲裁 ID 算式错在两处

`DMmotor_transmit` 内：

| | 修改前 | 修改后 | 期望值 |
|---|---|---|---|
| Pitch 控制帧 | `id + 0x100`（`id` =1 → `0x101`） | `ID + 0x100` | `0x109` |
| Yaw 控制帧 | 同上 → `0x101` | `ID + 0x200` | `0x206` |

依据达妙官方协议：

| 用途 | 仲裁 ID |
|---|---|
| 使能 / 失能 / 置零 / 清错 | `CAN_ID`（不加偏移） |
| MIT 控制帧 | `CAN_ID` |
| POS_VEL 控制帧 | `0x100 + CAN_ID` |
| VEL 控制帧 | `0x200 + CAN_ID` |
| 反馈帧 | `MST_ID`（默认 0） |

`0x101` 意味着"发给 CAN_ID 为 1 的电机的 POS_VEL 帧"，两台达妙都不认，**帧被丢弃，电机永远处于失能状态**（现象：上电后纹丝不动，无任何报错）。

### 6.2 签名不一致导致编译不过

`HTmotor.h`（已改为新签名）与 `HTmotor.cpp`（未改）三处对不上：

| 函数 | `.h` | `.cpp` |
|---|---|---|
| `CanComm_ControlCmd` | `(CAN& hcan, uint8_t cmd)` | `(CAN& hcan, uint8_t cmd, uint32_t id)` |
| `DMmotorinit` | `(CAN& hcan)` | `(uint32_t id)` |
| `DMmotor_transmit` | `(CAN& hcan)` | `(uint32_t id)` |

C++ 要求成员函数定义与类内声明完全一致，不一致即"no declaration matches"编译错误。

## 七、验证方法

1. **编译**：零错误、零 `undefined reference`。
2. **调试器**：观察 `can2.jointpdata[0]` / `[1]`，前 4 字节应分别为 Pitch 的 `setPos`、Yaw 的 `setSpeed` 的 IEEE 754 小端字节。
3. **CAN 分析仪**：应看到 `0x109`（Pitch）与 `0x206`（Yaw）交替出现，约每 3 ms 一轮；另有周期性 `0x009` / `0x006` 使能帧。
4. **交叉验证**：把 Pitch 的反馈值固定为常数，确认只有 `jointpdata[0]` 段变化，`jointpdata[1]` 不受影响。

## 八、经验规则（可复用）

> **凡是"关于本对象自身"的信息 —— CAN_ID、工作模式、在数组里的位置 —— 都从 `this` 取，不作为参数传入。参数只用于传递"对象自己不知道的外部信息"（走哪条总线、执行哪条命令）。**

理由：参数是"外部提供的说法"，可能被传错且编译器不检查；成员变量与 `this` 是"对象自身的事实"，不可能被传错。

**推论**：**槽号（数组位置）与 CAN_ID（硬件编号）是两件互不相关的事，不可用公式互相换算。** 原代码 `ID - 0x01` 就是把 ID 当槽号用的典型错误 —— Pitch `ID = 0x09` 算出槽 9，而数组只有 6 行，直接越界读。

---

需要的话我把它落成一个 `.md` 文件（放哪你定，我不往源码目录里塞）。另外文档里第六节 6.2 那段"编译不过"是**当下正在发生**的，你改 `HTmotor.cpp` 时一起处理掉就行。