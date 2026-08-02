# FreeRTOS 教学方案

> 适用对象：已掌握基础 C 语言（变量、函数、指针、结构体），未接触过操作系统 / RTOS 

---

# 第一部分：学习 FreeRTOS 的好处

## 1.1 为什么要在大学阶段学 FreeRTOS？

| 维度 | 说明 |
|------|------|
| **工程价值** | 90%+ 的嵌入式产品（汽车、无人机、IoT、机器人）使用 RTOS，FreeRTOS 市场份额第一 |
| **思维跃迁** | 从「单线程裸机思维」升级到「多任务并发思维」——这是计算机科学的核心素养 |
| **就业加分** | 大疆、华为、特斯拉、博世等企业的嵌入式岗位面试必问 RTOS 概念 |
| **学习成本低** | FreeRTOS 内核极小（3 个核心文件），源码可读性极强，适合作为 RTOS 入门 |
| **开源免费** | MIT 许可证，商业可用，学习资料极其丰富 |

## 1.2 学了 FreeRTOS 你能做什么？

- 写一个能**同时**处理按键、显示、传感器、通信的嵌入式程序（而不是 super loop 排队）

      while (1) {
          read_sensor();      // 1. 读传感器//HAL_Delay(200);
          update_display();   // 2. 更新屏幕（500）
          check_keypress();   // 3. 检测按键（300）
          control_motor();    // 4. 控制电机（600）
          // 然后回到开头，再来一遍
      }//排队

- 理解「操作系统是怎么调度任务的」——这是理解 Linux / RTOS / 任何 OS 的通用基础

- 写出**结构清晰、可维护**的嵌入式代码——每个功能一个独立任务，而不是一团 spaghetti

  // 这是一个 spaghetti corner 

  ```
  void handle_system(void) {
      if (sensor_ready) {
          if (display_mode == 0) {
          } else if (display_mode == 1 && button_hold > 5) {
              // 做别的事
              while (uart_busy) {
                  if (timeout_flag) {
                      goto error_handle;  // ← goto 飞走
                  }
              }
          }
      }
      if (!sensor_ready && old_data_valid) {
      }
  }
  ```

  

- 掌握实时系统思维：知道什么必须在中断做、什么可以在任务做、什么绝对不能做

---

# 第二部分：FreeRTOS 内核架构全览

## 2.1 架构总图

```
┌─────────────────────────────────────────────────────────────┐
│                       Application Tasks                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Task_A   │  │ Task_B   │  │ Task_C   │  │ Timer    │   │
│  │ (Sensor) │  │ (Display)│  │ (Control)│  │ Service │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │              │              │        │
├───────┴──────────────┴──────────────┴──────────────┴────────┤
│                  FreeRTOS Kernel (核心)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Task       │  │   Queue      │  │   Semaphore     │   │
│  │   Scheduler  │  │   Manager    │  │   / Mutex       │   │
│  ├──────────────┤  ├──────────────┤  ├─────────────────┤   │
│  │   Memory     │  │   Timer      │  │   Event Groups  │   │
│  │   Manager    │  │   Service    │  │                 │   │
│  ├──────────────┤  ├──────────────┤  ├─────────────────┤   │
│  │   Port Layer (移植层: ARM / RISC-V / Xtensa / ...)     │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                     Hardware (MCU)                          │
│        ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│        │  Cortex  │  │  Timers  │  │  NVIC    │           │
│        │  Core    │  │          │  │ (中断)   │           │
│        └──────────┘  └──────────┘  └──────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## 2.2 核心组件一览

| 组件 | 作用 | 实际 |
|------|------|-----------|
| **Task（任务）** | 最小调度单位，每个任务是一个永不返回的独立循环 | **任务 = 独立的事** |
| **Scheduler（调度器）** | 决定下一瞬间 CPU 执行哪个任务 | **调度 = 谁来干活** |
| **Queue（队列）** | 任务间安全传递数据 | **队列 = 传送带** |
| **Semaphore（信号量）** | 同步/通知/资源计数 | **信号量 = 旗子** |
| **Mutex（互斥量）** | 保护共享资源（有优先级继承） | **互斥量 = 钥匙** |
| **Timer（软定时器）** | 周期性回调，在守护任务中执行 | **定时器 = 闹钟** |
| **Event Group（事件组）** | 多事件 OR/AND 等待 | **事件组 = 信号灯组合** |
| **Heap（堆管理）** | 5 种策略，为内核对象分配内存 | **堆 = 仓库** |

## 2.3 任务状态机（核心中的核心）

```
                    ┌─────────────────────┐
                    │                     │
        创建任务 ──→│   Ready（就绪）     │←──────────────┐
                    │   等待 CPU          │               │
                    └──────────┬──────────┘               │
                               │                          │
                   调度器选中  │   被抢占 / 时间片用完     │
                               │                          │
                    ┌──────────▼──────────┐               │
                    │                     │               │
                    │   Running（运行）   │───────────────┘
                    │   CPU 正在执行它    │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┼──────────────┐
                 │             │              │
          vTaskDelay()   等待队列/信号量   vTaskSuspend()
                 │             │              │
    ┌────────────▼──┐  ┌──────▼──────┐  ┌────▼─────┐
    │  Blocked      │  │  Blocked    │  │Suspended │
    │  (时间阻塞)   │  │ (事件阻塞)  │  │ (手动)   │
    │  时间到→Ready │  │ 事件到→Ready│  │ Resume→R │
    └───────────────┘  └─────────────┘  └──────────┘
```

### 问题：

1. **这个任务现在是什么状态？（Running / Ready / Blocked / Suspended）**
2. **它为什么被阻塞？（等时间 / 等队列 / 等信号量 / 被人挂起）**
3. **谁能让它变成 Ready？（定时器中断 / 另一个任务给信号量 / 中断给信号量）**

## 2.4 调度策略

| 策略 | 行为 | 适用场景 |
|------|------|---------|
| **抢占式（Preemptive）** | 高优先级就绪 → 立即抢占低优先级 | **默认**，多数场景 |
| **合作式（Cooperative）** | 任务主动让出 CPU 才切换 | 确定性要求极高，无中断嵌套 |
| **时间片轮转（Time Slicing）** | 同优先级任务轮流运行（每个一个 Tick） | 多个同等重要的任务 |

> FreeRTOS 默认使用**抢占式 + 时间片轮转**。

---

# 第三部分：讲解内容

---

## 第 1 课：从裸机到操作系统的思维跳变

### 1.1 意识流

#### 1.1.1 裸机编程的困境

```
void main() {
    while(1) {
        read_sensor();      // 读完传感器 → 100ms
        update_display();   // 更新屏幕   → 50ms
        check_key();        // 检测按键   → 30ms
        control_motor();    // 控制电机   → 80ms
    }
}
```

**问：** 如果在 `read_sensor()` 执行到第 50ms 时，按键被按下——它要等到下一个循环才能被检测到。从按下到响应，最多可能等多久？

如果控制电机的时候存在这种情况，会发生什么事？

#### 1.1.2 操作系统的幻觉

**比喻一下：「大脑」**

> 你只有一颗大脑（一个 CPU/MCU）。你无法同时背单词和做数学题，但你可以背 10 秒单词，切过去做 5 秒数学，再切回来。只要切得够快——每秒切几百次——旁人看你就像在「同时」做两件事。
>

**三个理解**

1. **并发（Concurrency）≠ 并行（Parallelism）**
   - 并发：看起来同时做多件事（单核，靠快速切换）
   - 并行：真的同时做多件事（多核）
   - FreeRTOS 在单核 MCU 上做的是**并发**，不是并行

2. **上下文切换（Context Switch）**——FreeRTOS 在做切换时：
   - 保存当前任务的 CPU 寄存器 + 栈指针 → 存入该任务的 TCB（Task Control Block）
   - 从下一个任务的 TCB 恢复寄存器 + 栈指针 → 开始执行
   - 整个过程只需**几十到几百个 CPU 周期**（微秒级）

3. **任务（Task）** = 一个有独立 `while(1)` 且永不返回的 C 函数

#### 1.1.3 实时系统 vs 非实时系统

| | 非实时（Linux/Windows） | 硬实时（FreeRTOS） |
|------|------------------------|-------------------|
| 调度延迟 | 不确定（几 ms~几百 ms） | 确定（μs 级可预测） |
| 错过 Deadline | 浏览器卡一下 | 系统失效 |
| 适用 | 桌面、服务器 | 汽车、航空、医疗、工业 |

**FreeRTOS 是硬实时操作系统**——它的调度延迟是**确定性的（Deterministic）**。

### 1.2 第一个 Demo

**STM32 + CubeMX：**

**第一个程序：「世界，你好，FreeRTOS」**

```c
/* CMSIS-RTOS v2 头文件 */
#include "cmsis_os.h"

/* 任务函数 1 */
void Task1(void *argument) {
    for (;;) {
        printf("Task 1: Hello from FreeRTOS!\n");
        osDelay(1000);  /* 延迟 1000ms */
    }
}

/* 任务函数 2 */
void Task2(void *argument) {
    for (;;) {
        printf("Task 2: I am alive!\n");
        osDelay(500);   /* 延迟 500ms */
    }
}

int main(void) {
    /* CubeMX HAL 初始化（根据芯片调整） */
    HAL_Init();
    SystemClock_Config();

    /* 定义任务属性 */
    osThreadAttr_t task1_attr = {
        .name = "Task1",
        .priority = (osPriority_t) osPriorityNormal,
        .stack_size = 1024
    };
    osThreadAttr_t task2_attr = {
        .name = "Task2",
        .priority = (osPriority_t) osPriorityNormal,
        .stack_size = 1024
    };

    /* 创建任务 */
    osThreadNew(Task1, NULL, &task1_attr);
    osThreadNew(Task2, NULL, &task2_attr);

    /* 启动调度器——从此不再返回 */
    osKernelStart();

    /* 永远不会执行到这里 */
    while (1) {}
}
```

**观察现象：**

- `Task 1` 每隔 1 秒打印一次
- `Task 2` 每隔 0.5 秒打印一次
- **两个任务看起来是「同时」在运行的**
- 注意，只是看起来

### 1.3 本节练习

1. **修改优先级**：把 vTask2 的优先级改成 2（高于 vTask1），观察打印顺序变化
2. **增加第三个任务**：vTask3，每 2 秒打印一次 "Task 3 is running"
3. **回答问题**：为什么 vTask2 比 vTask1 打印得更频繁？

---

## 第 2 课：任务深入 + 任务状态机

### 2.1 意识流

**任务状态机的生活比喻：**

> - **Ready**：你在食堂窗口前排队，等轮到你打饭 —— 「我想吃，但还没轮到我」
> - **Running**：轮到你打饭了，大师傅（CPU）正在给你盛菜 —— 「我在吃」
> - **Blocked**：你让大师傅等一下，因为你还没想好要什么菜 —— 「我等个事（想好菜 / 汤做好）」
> - **Suspended**：你被辅导员叫走了，今天不吃了 —— 「我不参与了」

### 2.2 核心 API 

| API | 作用 | 阻塞 |
|-----|------|--------|
| `osDelay(xTicks)` | 延迟指定 Tick 数 | 进入 Blocked |
| `osDelayUntil(pxLastWakeTime, xTicks)` | 固定频率延迟（无累积误差） | 进入 Blocked |
| `osThreadSuspend(xTask)` | 挂起一个任务 | 其他人调用 |
| `osThreadResume(xTask)` | 恢复一个被挂起的任务 | 其他人调用 |
| `osThreadGetPriority(NULL)` | 获取当前任务优先级 |  |
| `osThreadSetPriority(xTask, uxNewPriority)` | 动态修改优先级 |  |

### 2.3 实战：LED 呼吸灯 + 串口打印

```c
#include "cmsis_os.h"

osThreadId_t LEDTaskHandle = NULL;

/* LED 闪烁任务 */
void LEDTask(void *argument) {
    for (;;) {
        //控制电平
        osDelay(50);
    }
}

/* 监控任务：读取串口指令控制 LED 任务 */
void MonitorTask(void *argument) {
    char cmd;
    for (;;) {
        scanf("%c", &cmd);
        if (cmd == 's') {
            osThreadSuspend(LEDTaskHandle);
            printf("LED Task Suspended\n");
        } else if (cmd == 'r') {
            osThreadResume(LEDTaskHandle);
            printf("LED Task Resumed\n");
        }
        osDelay(100);
    }
}

int main(void) {
    HAL_Init();
    SystemClock_Config();

    osThreadAttr_t led_attr = {
        .name = "LED",
        .priority = (osPriority_t) osPriorityLow,
        .stack_size = 128
    };
    osThreadAttr_t mon_attr = {
        .name = "Monitor",
        .priority = (osPriority_t) osPriorityBelowNormal,
        .stack_size = 256
    };

    LEDTaskHandle = osThreadNew(LEDTask, NULL, &led_attr);
    osThreadNew(MonitorTask, NULL, &mon_attr);

    osKernelStart();
    while (1) {}
}
```

### 2.4 本节练习

1. **观察 Blocked**：使用 `uxTaskGetNumberOfTasks()` 打印当前任务数量和各状态统计
2. **实验 Suspend/Resume**：用串口输入 's' 挂起 LED 任务，输入 'r' 恢复——观察 LED 是否停在当前状态

---

## 第 3 课：优先级与抢占式调度

### 3.1 意识流

**核心规则：**

1. **高优先级任务永远先运行** —— 只要高优先级就绪，CPU 立刻给它
2. **同优先级任务轮转运行** —— 每个任务一个时间片（一个 Tick，通常是 1ms）
3. **低优先级任务「不知道」自己被抢占了** —— FreeRTOS 自动保存/恢复上下文，对抢占无感

### 3.2 抢占演示实验

```c
void HighPriorityTask(void *argument) {
    uint32_t start, end;
    for (;;) {
        start = osKernelGetTickCount();
        /* 故意做大量计算：占据 CPU */
        for (volatile uint32_t i = 0; i < 1000000; i++);
        end = osKernelGetTickCount();
        printf("HIGH: ran for %lu ticks\n", end - start);
        osDelay(100);
    }
}

void LowPriorityTask(void *argument) {
    for (;;) {
        printf("LOW: I'm trying to run...\n");
        osDelay(1000);
    }
}

/* 在 main() 中：*/
osThreadAttr_t high_attr = {
    .name = "High",
    .priority = (osPriority_t) osPriorityAboveNormal,
    .stack_size = 256
};
osThreadAttr_t low_attr = {
    .name = "Low",
    .priority = (osPriority_t) osPriorityNormal,
    .stack_size = 256
};
osThreadNew(HighPriorityTask, NULL, &high_attr);
osThreadNew(LowPriorityTask, NULL, &low_attr);
```

**观察现象：** `vLowPriorityTask` 几乎**永远不会有输出**——高优先级任务只要就绪就抢占它。

**修正：** 把 `vLowPriorityTask` 优先级提到 3，观察反转；或用 `vTaskPrioritySet()` 动态调整。

### 3.3 时间片轮转实验

让两个同优先级任务（都设为 1），都不调用 `vTaskDelay()`，但做有限次计算后主动 `taskYIELD()`：

```c
void TaskA(void *argument) {
    for (;;) {
        printf("A");
        osThreadYield();  /* 主动让出 CPU */
    }
}

void TaskB(void *argument) {
    for (;;) {
        printf("B");
        osThreadYield();
    }
}
```

**输出模式：** `ABABABABAB...`（无延迟，仅仅靠时间片或主动让出）

### 3.4 本节练习

1. **构造「任务饥饿」**：创建 3 个任务，优先级 3、2、1，全部无限循环无延迟——观察哪些任务能运行
2. **固定频率 vs 非固定频率**：对比 `vTaskDelay()` 和 `vTaskDelayUntil()` 的时间误差
3. **计算最大调度延迟**：在任务中关闭中断后测量调度延迟（理解临界区对实时性的影响）

---

## 第 4 课：任务间通信——队列（Queue）

### 4.1 意识流

**全局变量的痛：**

```c
int sensor_value;  // 全局变量

void Task_Sensor(void *argument) {  // 优先级 2
    for (;;) {
        sensor_value = read_adc();   // ← 写到一半可能被抢占！
        osDelay(100);
    }
}

void Task_Display(void *argument) {  // 优先级 1
    for (;;) {
        display(sensor_value);  // ← 可能读到写一半的值！
        osDelay(50);
    }
}
```

**队列的比喻：**

> 「队列就像两个工位之间的传送带。A 把零件放在传送带上就回去干自己的活。B 从传送带另一端取走零件。传送带一次只传一个零件——A 放的时候 B 不能取，B 取的时候 A 不能放。这就安全了。」

### 4.2 队列 API

```c
/* 1. 创建消息队列：可存放 10 个 int */
osMessageQueueId_t myQueue = osMessageQueueNew(10, sizeof(int), NULL);

/* 2. 发送（任务中）—— 队列满则阻塞 */
osMessageQueuePut(myQueue, &data, 0, osWaitForever);        /* 永远等 */
char buff[20];
sprintf(buff,osMessageQueuePut(myQueue, &data, 0, 100),20);                /* 最多等 100ms */

/* 3. 发送（中断中）—— CMSIS v2 自动处理 ISR 上下文 */
osMessageQueuePut(myQueue, &data, 0, 0);                    /* 不阻塞 */

/* 4. 接收 —— 队列空则阻塞 */
osMessageQueueGet(myQueue, &received, NULL, osWaitForever);

/* 5. 查询队列中有多少元素 */
uint32_t count = osMessageQueueGetCount(myQueue);
```

### 4.3 实战：传感器数据流水线

```c
osMessageQueueId_t TempQueue;

void SensorTask(void *argument) {
    int32_t temperature;
    for (;;) {
        temperature = read_temperature();          /* 读传感器 */
        osMessageQueuePut(TempQueue, &temperature, 0, osWaitForever);  /* 入队 */
        osDelay(500);                              /* 每 500ms 读一次 */
    }
}

void SensorTask1(void *argument) {
    int32_t temperature;
    for (;;) {
        temperature1 = read_temperature();          /* 读传感器 */
        osMessageQueuePut(TempQueue1, &temperature1, 0, osWaitForever);  /* 入队 */
        osDelay(500);                              /* 每 500ms 读一次 */
    }
}

void DisplayTask(void *argument) {
    int32_t temp;
    for (;;) {
        osMessageQueueGet(TempQueue, &temp, NULL, osWaitForever);  /* 阻塞等数据 */
        printf("Temp: %ld°C\n", temp);
        update_lcd(temp);
    }
}

void ControlTask(void *argument) {
    int32_t temp;
    for (;;) {
        osMessageQueueGet(TempQueue1, &temp, NULL, osWaitForever);
        if (temp > 30) {
            fan_on();
        } else {
            fan_off();
        }
    }
}

int main(void) {
    HAL_Init();
    SystemClock_Config();

    TempQueue = osMessageQueueNew(5, sizeof(int32_t), NULL);

    osThreadAttr_t sensor_attr = { .name = "Sensor",  .priority = (osPriority_t) osPriorityHigh,      .stack_size = 256 };
    osThreadAttr_t disp_attr  = { .name = "Display",  .priority = (osPriority_t) osPriorityAboveNormal, .stack_size = 256 };
    osThreadAttr_t ctrl_attr  = { .name = "Control",  .priority = (osPriority_t) osPriorityAboveNormal, .stack_size = 256 };

    osThreadNew(SensorTask,  NULL, &sensor_attr);
    osThreadNew(DisplayTask, NULL, &disp_attr);
    osThreadNew(ControlTask, NULL, &ctrl_attr);

    osKernelStart();
    while (1) {}
}
```

### 4.4 本节练习

1. **多消费者问题**：上面代码中 Display 和 Control 谁先拿到数据？如何保证它们都能拿到？
2. **队列超时**：修改接收为 `pdMS_TO_TICKS(2000)`，观察 2 秒无数据时接收任务的行为
3. **队列溢出**：发送方速度 > 接收方速度时，队列满了会怎样？修改代码验证

---

## 第 5 课：信号量与互斥量

### 5.1 意识流

#### 二元信号量（Binary Semaphore）

> **比喻：停车场入口的闸杆**
>
> - 初始状态：闸杆放下（0）——没有车能进
> - `xSemaphoreGive()` → 闸杆抬起（1）——一辆车可以进
> - `xSemaphoreTake()` → 闸杆放下（0）——车进去了，下一个等

**典型应用：中断通知任务**

```c
osSemaphoreId_t ButtonSem;

/* 中断服务函数 */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    osSemaphoreRelease(ButtonSem);  /* CMSIS v2 自动处理 ISR 上下文 */
}

/* 等待按键的任务 */
void ButtonTask(void *argument) {
    for (;;) {
        osSemaphoreAcquire(ButtonSem, osWaitForever);  /* 阻塞：等按键 */
        printf("Button pressed!\n");
    }
}

/* 在 main() 中创建：值为 0 的通知信号量 */
ButtonSem = osSemaphoreNew(1, 0, NULL);
```

#### 计数信号量（Counting Semaphore）

> **比喻：停车场剩余车位**
> - 初始：总车位 10
> - 每进一辆：`Take()` → 剩余减 1
> - 每出一辆：`Give()` → 剩余加 1
> - 剩余为 0 时：新来的车必须等

#### 互斥量（Mutex）—— 带优先级继承的二元信号量

> **比喻：会议室钥匙**
> - 谁拿钥匙谁用会议室
> - 别人想用必须等
> - **优先级继承**：如果 CEO（高优先级）在外面等，拿着钥匙的实习生（低优先级）会被临时提拔成 CEO 优先级，快速开完会还钥匙

**为什么不能用二元信号量代替互斥量？**

```c
// ❌ 用二元信号量保护共享资源
osSemaphoreAcquire(xSerialSem, osWaitForever);
uart_send(data);     // 使用串口
osSemaphoreRelease(xSerialSem);
```

如果低优先级任务持有信号量时被中优先级抢占，高优先级任务在等信号量——这就是**优先级反转**。互斥量的**优先级继承**机制自动解决这个问题。

### 5.2 实战：生产者-消费者模型

```c
osSemaphoreId_t DataSem;
osMessageQueueId_t DataQueue;

void ProducerTask(void *argument) {
    int32_t data = 0;
    for (;;) {
        data++;
        osMessageQueuePut(DataQueue, &data, 0, osWaitForever);
        osSemaphoreRelease(DataSem);              /* 通知消费者有数据 */
        osDelay(300);
    }
}

void ConsumerTask(void *argument) {
    int32_t data;
    for (;;) {
        osSemaphoreAcquire(DataSem, osWaitForever);  /* 等信号量 */
        osMessageQueueGet(DataQueue, &data, NULL, 0); /* 不阻塞 */
        printf("Consumed: %ld\n", data);
    }
}
```

### 5.3 优先级反转演示

```c
void LowTask(void *argument) {
    for (;;) {
        osMutexAcquire(Mutex, osWaitForever);
        printf("LOW: got mutex, working...\n");
        osDelay(5000);  /* 持锁 5 秒！ */
        osMutexRelease(Mutex);
        osDelay(1000);
    }
}

void MidTask(void *argument) {
    for (;;) {
        printf("MID: running (not touching mutex)\n");
        /* 死循环——永远不阻塞，长期抢 CPU */
    }
}

void HighTask(void *argument) {
    for (;;) {
        osDelay(100);  /* 给 Low 先拿到锁的机会 */
        printf("HIGH: waiting for mutex...\n");
        osMutexAcquire(Mutex, osWaitForever);
        printf("HIGH: got mutex!\n");
        osMutexRelease(Mutex);
    }
}
```

**现象：** Low 拿着锁 → Mid 抢占 Low（Mid 不阻塞）→ High 等锁 → 但 Low 被 Mid 压制着无法运行 → **High 被 Mid 间接饿死**。

**解决方案：** 用 `xSemaphoreCreateMutex()` 而不是 `xSemaphoreCreateBinary()`。

### 5.4 本节练习

1. **用信号量实现「三任务同步」**：Task_A 准备数据 → 给信号量 → Task_B 处理 → 给信号量 → Task_C 输出
2. **复现优先级反转**：去掉互斥量的优先级继承（改用二元信号量），观察现象差异
3. **死锁实验**：构造两个任务互相等待对方持有的两个互斥量，验证死锁

---

## 第 6 课：中断管理与软定时器

### 6.1 意识流

#### 中断的黄金法则

```
┌──────────────────────────────────────────────────┐
│          中断服务函数（ISR）必须：                   │
│  1️⃣  快！快！快！（极短，只做必要的事）              │
│  2️⃣  不能调用阻塞型 API（没有 FromISR 后缀的）      │
│  3️⃣  需要通知任务时，用 FromISR 版 API             │
│  4️⃣  如果唤醒了更高优先级的任务，在 ISR 结束时      │
│      调用 portYIELD_FROM_ISR() 立即切换             │
└──────────────────────────────────────────────────┘
```

**为什么不能在中断中 `printf()`？**
- `printf()` 可能依赖信号量（串口互斥）
- 信号量在中断中不能 `Take`（会阻塞）
- 即使不阻塞，`printf()` 的执行时间不可预测（几十 μs ~ 几 ms）
- 中断应该是**确定的**和**极短的**

#### 临界区（Critical Section）

```c
/* 方法 1：锁内核（CMSIS v2 方式，类似关闭调度器） */
osKernelLock();
/* 这里：不会发生任务切换，中断仍可响应 */
safe_register_write(REG, val);
osKernelUnlock();

/* 方法 2：互斥量（只保护共享资源，最轻量） */
osMutexAcquire(Mutex, osWaitForever);
/* 这里：只有竞争同一互斥量的任务会被阻塞 */
osMutexRelease(Mutex);
```

### 6.2 软定时器

**软定时器不是硬件定时器**——它是 FreeRTOS 的一个**守护任务**（Timer Service Task），到时间了就执行回调。

```c
osTimerId_t MyTimer;

void TimerCallback(void *argument) {
    printf("Timer fired! Tick: %lu\n", osKernelGetTickCount());
}

int main(void) {
    HAL_Init();
    SystemClock_Config();

    MyTimer = osTimerNew(TimerCallback, osTimerPeriodic, NULL, NULL);

    if (MyTimer != NULL) {
        osTimerStart(MyTimer, 1000);      /* 启动定时器，周期 1000ms */
    }

    osKernelStart();
    while (1) {}
}
```

**需要注意：**
- 定时器回调在**守护任务**中执行，不是在中断中
- 回调中可以调用**任何** FreeRTOS API（不需要 FromISR 版本）
- 如果回调执行时间过长，会影响其他定时器的精度
- 可以通过 `configTIMER_TASK_PRIORITY` 调整守护任务的优先级

### 6.3 实战：按键中断 + 队列通知任务

```c
osMessageQueueId_t KeyQueue;

/* 中断服务函数 */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    uint8_t key_code = 1;  /* 假设 KEY1 被按下 */
    osMessageQueuePut(KeyQueue, &key_code, 0, 0);  /* CMSIS v2 自动处理 ISR */
}

/* 任务：处理按键事件 */
void KeyProcessTask(void *argument) {
    uint8_t code;
    for (;;) {
        osMessageQueueGet(KeyQueue, &code, NULL, osWaitForever);
        switch (code) {
            case 1: printf("KEY1 pressed\n"); break;
            case 2: printf("KEY2 pressed\n"); break;
            default: printf("Unknown key\n");
        }
    }
}

int main(void) {
    HAL_Init();
    SystemClock_Config();

    KeyQueue = osMessageQueueNew(10, sizeof(uint8_t), NULL);

    osThreadAttr_t key_attr = {
        .name = "KeyProc",
        .priority = (osPriority_t) osPriorityHigh,
        .stack_size = 256
    };
    osThreadNew(KeyProcessTask, NULL, &key_attr);
    /* 中断硬件初始化省略（CubeMX 或手动配置 GPIO EXTI） */

    osKernelStart();
    while (1) {}
}
```

### 6.4 本节练习

1. **测量临界区开销**：用 `xTaskGetTickCount()` 测量 `taskENTER_CRITICAL()` 到 `taskEXIT_CRITICAL()` 的时间
2. **软定时器累积误差**：创建 3 个不同周期的定时器，观察它们的时间漂移
3. **中断延迟测试**：在 GPIO 中断中翻转另一个 GPIO，用示波器测量从中断触发到 ISR 开始执行的延迟

## 4.1 随堂选择题

### 第 1 课：基础概念

1. FreeRTOS 是一个：
   A. 文件系统  B. 实时操作系统  C. 编译器  D. 数据库
   
2. 以下哪个是任务的状态？
   A. Running  B. Sleeping  C. Eating  D. Waiting
   
3. `vTaskStartScheduler()` 返回吗？
   A. 返回 0  B. 永远不返回  C. 返回错误码  D. 取决于堆大小

### 第 2 课：任务状态

4. 一个任务调用了 `vTaskDelay(1000)` 后进入什么状态？
   A. Ready  B. Running  C. Blocked  D. Suspended
   
5. 怎样让一个 Blocked 状态的任务回到 Ready？
   A. 调用 vTaskSuspend  B. 等待的事件发生  C. 重启 MCU  D. 调用 xTaskCreate

### 第 3 课：优先级

6. 高优先级任务就绪时，低优先级任务会怎样？
   A. 继续运行  B. 被抢占（暂停）  C. 自动升优先级  D. 被删除
   
7. 两个同优先级的任务都不调用 vTaskDelay，它们会怎么运行？
   A. 只有第一个运行  B. 轮流运行（时间片轮转）  C. 第二个永远不运行  D. 系统崩溃

### 第 4 课：队列

8. 队列中数据发送到接收是：
   A. 引用传递  B. 指针传递  C. 值拷贝  D. 不传递
   
9. 队列为空时，`xQueueReceive(xQueue, &data, portMAX_DELAY)` 会：
   A. 立即返回失败  B. 阻塞直到有数据  C. 返回随机值  D. 创建新数据

### 第 5 课：信号量

10. 互斥量和二元信号量的核心区别是：
    A. 互斥量更快  B. 互斥量有优先级继承  C. 信号量可以计数  D. 没有区别
    
11. 优先级反转是指：
    A. 高优先级任务抢占低优先级  B. 中优先级任务间接阻塞高优先级任务
    C. 任务优先级自动升高  D. 所有任务优先级变为 0

## 4.2 编程作业

### 作业 1：多任务流水灯（第 2 课后）
> 3 个任务各控制一个 LED，频率分别为 200ms、500ms、1000ms，用 `vTaskDelayUntil()` 实现精确周期。

### 作业 2：按键事件分发器（第 5 课后）
> 一个中断采集按键，一个任务接收并将按键值分发给另外两个任务（一个记录日志，一个控制 LED）。

### 作业 3：双缓冲区生产者（第 5 课后）
> Producer 每 100ms 产生一个数据，Consumer 每 200ms 消费一个数据。演示队列满时的阻塞行为。

### 作业 4：简易调度器监控器（第 6 课后）
> 创建一个任务，每隔 1 秒打印所有任务的状态（`uxTaskGetSystemState()`），以及 CPU 空闲率（`vTaskGetRunTimeStats()`）。

## 5.1 栈溢出

```c
// 方法 1：开启 FreeRTOS 内置检测
// 在 FreeRTOSConfig.h 中：
#define configCHECK_FOR_STACK_OVERFLOW 2

// 实现钩子函数
void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName) {
    printf("!!! STACK OVERFLOW: %s\n", pcTaskName);
    taskDISABLE_INTERRUPTS();
    while (1);
}

// 方法 2：查看任务剩余栈空间
UBaseType_t uxHighWaterMark = uxTaskGetStackHighWaterMark(xTaskHandle);
printf("Task %s stack left: %u words\n", "TaskName", uxHighWaterMark);
```

## 5.2 死锁

```c
// 用非阻塞 Acquire 检测死锁
if (osMutexAcquire(Mutex, 0) == osOK) {
    // 成功拿到锁
    osMutexRelease(Mutex);
} else {
    printf("WARNING: Someone is holding the mutex too long!\n");
}
```

## 5.3 优先级反转检测

```c
// 在 vApplicationTickHook() 中记录
static osThreadId_t LastRunning = NULL;
void vApplicationTickHook(void) {
    osThreadId_t Current = osThreadGetId();
    if (LastRunning != NULL && LastRunning != Current) {
        // 发生了任务切换
    }
    LastRunning = Current;
}
```

## 5.4 内存不足

```c
// 检查剩余堆空间
printf("Free heap: %u bytes\n", xPortGetFreeHeapSize());

// 检查历史上最小剩余堆
printf("Min ever free: %u bytes\n", xPortGetMinimumEverFreeHeapSize());
```

---

# 第六部分：FreeRTOSConfig.h 关键配置

```c
/* FreeRTOSConfig.h —— 学生需要理解每个宏的含义 */

#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H

/* 基础配置 */
#define configUSE_PREEMPTION            1       /* 抢占式调度 */
#define configUSE_IDLE_HOOK             0       /* 空闲任务钩子 */
#define configUSE_TICK_HOOK             0       /* Tick 钩子 */
#define configCPU_CLOCK_HZ              ((uint32_t)168000000)  /* 根据 MCU 修改 */
#define configTICK_RATE_HZ              ((TickType_t)1000)     /* 1ms 一个 Tick */
#define configMAX_PRIORITIES            (5)     /* 优先级数量 (0~4) */
#define configMINIMAL_STACK_SIZE        ((uint16_t)128)
#define configTOTAL_HEAP_SIZE           ((size_t)(20 * 1024))  /* 20KB 堆 */
#define configMAX_TASK_NAME_LEN         (16)

/* 功能开关 */
#define configUSE_16_BIT_TICKS          0       /* 32-bit Tick */
#define configUSE_MUTEXES               1       /* 使能互斥量 */
#define configUSE_QUEUE_SETS            1       /* 使能队列集 */
#define configUSE_COUNTING_SEMAPHORES   1       /* 使能计数信号量 */
#define configUSE_TRACE_FACILITY        1       /* 使能调试统计 */
#define configUSE_STATS_FORMATTING_FUNCTIONS 1  /* 使能统计格式化函数 */

/* 协程（FreeRTOS 旧特性，新项目不用） */
#define configUSE_CO_ROUTINES           0

/* 软定时器 */
#define configUSE_TIMERS                1
#define configTIMER_TASK_PRIORITY       (2)
#define configTIMER_QUEUE_LENGTH        10
#define configTIMER_TASK_STACK_DEPTH    configMINIMAL_STACK_SIZE

/* 可选函数 */
#define INCLUDE_vTaskPrioritySet        1
#define INCLUDE_uxTaskPriorityGet       1
#define INCLUDE_vTaskDelete             1
#define INCLUDE_vTaskSuspend            1
#define INCLUDE_xTaskResumeFromISR      1
#define INCLUDE_vTaskDelayUntil         1
#define INCLUDE_vTaskDelay              1
#define INCLUDE_xTaskGetCurrentTaskHandle 1
#define INCLUDE_uxTaskGetStackHighWaterMark 1

/* 栈溢出检测 */
#define configCHECK_FOR_STACK_OVERFLOW  2

/* 中断优先级配置（ARM Cortex-M 特有） */
#define configLIBRARY_LOWEST_INTERRUPT_PRIORITY    15
#define configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY 5

#endif /* FREERTOS_CONFIG_H */
```

---

# 第七部分：推荐学习资源

## 官方资源

| 资源 | 链接 |
|------|------|
| FreeRTOS 官方文档 | https://www.freertos.org/Documentation/RTOS_book.html |
| Mastering the FreeRTOS Real Time Kernel（免费 PDF） | https://www.freertos.org/Documentation/00-README |
| 官方 API 参考 | https://www.freertos.org/a00106.html |
| FreeRTOS GitHub | https://github.com/FreeRTOS/FreeRTOS |

## 书籍

- **《FreeRTOS 源码详解与应用开发》**——基于 ARM Cortex-M，逐行分析内核源码
- **《嵌入式实时操作系统 μC/OS-III 应用开发》**——概念相通，可以作为对照学习
- **《ARM Cortex-M3/M4 权威指南》**——理解底层的异常处理和 PendSV 机制

## 视频教程

- **YouTube: FreeRTOS Tutorial Series** by Shawn Hymel / DigiKey
- **B 站：FreeRTOS 从入门到精通**（搜索关键词）
- **Mastering RTOS** by Andrej Karpathy（概念讲解非常透彻）**最后送给各位同学的的话：**

> FreeRTOS 的核心只有 3 个层次：
>1. **任务**——把大问题拆成独立的小循环
> 2. **通信**——让任务之间安全地交换数据
> 3. **同步**——让任务在正确的时间做正确的事
> 
> 掌握这三个层次，你就能用 FreeRTOS 写出清晰、健壮、可维护的嵌入式系统。
>剩下的，只是看源码和踩坑的积累。
> 
> 学长也只是浅尝辄止，不能带你们走得更远，只希望你们能在我的入门教学下，能快速上手实时操作系统，具备工程能力......
