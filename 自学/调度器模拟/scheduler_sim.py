#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FreeRTOS 调度器模拟（教学版）
===================================================
把你电控培训里调了一个暑假的 FreeRTOS，用纯 Python 重写一遍调度内核。
跑完这一遍，「链表、优先队列(堆)、有序链表、状态机」这些下学期数据结构课的
概念，就长在你自己最熟悉的世界里了。

数据结构对照表
--------------
| 本程序里                       | 数据结构课概念      | 真实 FreeRTOS          |
|--------------------------------|--------------------|------------------------|
| DList（双向链表 + 哨兵头）      | 链表               | List_t / xLIST         |
| ready_lists[优先级] 数组        | 链表的数组 = 索引表  | pxReadyTasksLists      |
| delayed_list（按唤醒时刻排序）  | 有序链表            | pxDelayedTaskList      |
| MinHeap 调度器（对照实验）      | 优先队列 / 堆       | ——（教学对照用）        |
| task.state 状态机             | 状态机 / 图         | eTaskState             |

跑法：
    python scheduler_sim.py

会打印：事件日志 → 每个 tick 的时序图 → 堆调度器对照 → 自检断言。
"""

import sys

# Windows 终端默认 GBK 编码打不出 █░ 这些块字符，强制切成 UTF-8 输出。
# （git bash / Windows Terminal 都按 UTF-8 显示；老式 cmd 窗口请换字体。）
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------------------------------------------------------------------------
# 1. 双向链表（带哨兵头）—— 数据结构课概念：【链表】
#    FreeRTOS 的 List_t 就是这东西：环形、带一个哨兵头，头尾插入删除都是 O(1)。
# ---------------------------------------------------------------------------

class DNode:
    """链表节点。__slots__ 省内存，也给 C 语言的"结构体字段"的感觉。"""
    __slots__ = ("prev", "next", "item")

    def __init__(self, item=None):
        self.prev = None
        self.next = None
        self.item = item


class DList:
    """环形双向链表。哨兵头不存数据，让"空表"和"非空表"的代码长得一模一样。"""

    def __init__(self):
        self.sentinel = DNode()
        self.sentinel.prev = self.sentinel
        self.sentinel.next = self.sentinel
        self.length = 0

    def is_empty(self):
        return self.length == 0

    def insert_tail(self, node):
        """尾部插入 O(1) —— 对应 FreeRTOS vListInsertEnd"""
        last = self.sentinel.prev
        last.next = node
        node.prev = last
        node.next = self.sentinel
        self.sentinel.prev = node
        self.length += 1

    def insert_sorted(self, node, key):
        """按 key 升序插入 O(n) —— 对应 FreeRTOS vListInsert。
        延时链表用它：唤醒时刻早的任务排在前面，调度器只需看表头。
        注意：这里假设节点里挂的是 Task（有 wake_time 字段）。"""
        cur = self.sentinel.next
        while cur is not self.sentinel and cur.item.wake_time <= key:
            cur = cur.next
        prev = cur.prev
        prev.next = node
        node.prev = prev
        node.next = cur
        cur.prev = node
        self.length += 1

    def pop_head(self):
        """弹出头节点 O(1) —— 对应 FreeRTOS listGET_HEAD_ENTRY"""
        if self.is_empty():
            return None
        node = self.sentinel.next
        self.remove(node)
        return node

    def head_item(self):
        return self.sentinel.next.item if not self.is_empty() else None

    def remove(self, node):
        """摘除任意节点 O(1) —— 对应 FreeRTOS uxListRemove"""
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = node.next = None
        self.length -= 1


# ---------------------------------------------------------------------------
# 2. 小顶堆（优先队列）—— 数据结构课概念：【堆 / 优先队列】
#    对照实验的"教科书版调度器"用：挑最高优先级任务时，堆每次 O(log n)。
#    元组 (key, seq, task)：key 小的先出；seq 是入堆序号，保证同优先级先进先出。
# ---------------------------------------------------------------------------

class MinHeap:
    """数组实现的二叉堆。下标 i 的左右孩子是 2i+1 / 2i+2。"""

    def __init__(self):
        self.a = []

    def __len__(self):
        return len(self.a)

    def push(self, key, seq, task):
        self.a.append((key, seq, task))
        self._up(len(self.a) - 1)   # 新元素一路往上冒泡

    def pop(self):
        top = self.a[0]
        last = self.a.pop()
        if self.a:
            self.a[0] = last
            self._down(0)           # 末尾元素当新根，一路往下沉
        return top

    def peek(self):
        return self.a[0]

    def _up(self, i):
        a = self.a
        while i > 0:
            p = (i - 1) // 2
            if a[i] < a[p]:
                a[i], a[p] = a[p], a[i]
                i = p
            else:
                break

    def _down(self, i):
        a, n = self.a, len(self.a)
        while True:
            l, r = 2 * i + 1, 2 * i + 2
            m = i
            if l < n and a[l] < a[m]:
                m = l
            if r < n and a[r] < a[m]:
                m = r
            if m == i:
                break
            a[i], a[m] = a[m], a[i]
            i = m


# ---------------------------------------------------------------------------
# 3. 任务 —— 每个任务是一段「跑 n 个 tick / 延时 m 个 tick」的行为脚本。
#    task.state 就是一张小的状态机：READY → RUNNING → DELAYED → READY → DONE
#    这个状态转移图，正是离散数学里"图 / 关系"的活例子。
# ---------------------------------------------------------------------------

class Task:
    __slots__ = ("name", "priority", "schedule", "step", "work_left",
                 "state", "wake_time", "ready_node", "delayed_node",
                 "slice_used", "hist", "t_run", "t_ready", "t_blocked")

    def __init__(self, name, priority, schedule):
        self.name = name
        self.priority = priority      # FreeRTOS 惯例：数值越大优先级越高
        self.schedule = schedule      # [("run", n), ("delay", m), ...]
        self.step = 0                 # 当前执行到 schedule 第几步
        self.work_left = 0            # 当前 run 阶段还差几个 CPU tick
        self.state = "READY"          # READY / RUNNING / DELAYED / DONE
        self.wake_time = -1           # DELAYED 时的唤醒时刻
        self.ready_node = None        # 就绪链表里的节点
        self.delayed_node = None      # 延时链表里的节点
        self.slice_used = 0           # 本次时间片已用掉的 tick
        self.hist = []                # 每个 tick 的状态字符（用来画时序图）
        self.t_run = self.t_ready = self.t_blocked = 0

    def _arm(self, now):
        """任务刚开始跑（work_left 还没装备好）时，从脚本里取出下一段。
        正常是 ('run', n)；若下一段是延时，则直接进入延时状态。"""
        if self.step >= len(self.schedule):
            self.state = "DONE"
            return
        kind, n = self.schedule[self.step]
        self.step += 1
        if kind == "run":
            self.work_left = n
        else:  # delay
            self.state = "DELAYED"
            self.wake_time = now + n

    def consume_tick(self, now):
        """被分配 1 个 tick 的 CPU。返回 True 表示下一步还要继续跑。"""
        if self.work_left <= 0:
            self._arm(now)                  # 首 tick / 唤醒后首个 tick：先上膛
        if self.state != "RUNNING":
            return False                    # 上膛时发现是延时/完成
        self.work_left -= 1
        if self.work_left > 0:
            return True
        self._arm(now)                      # 本次 run 用完，取脚本下一步
        return self.state == "RUNNING"

    def expected_run_ticks(self):
        """脚本里所有 run 的总时长，自检时用来对账。"""
        return sum(n for kind, n in self.schedule if kind == "run")


def build_scenario():
    """这个场景照着你电控培训里最眼熟的活儿来：
    高优先级的按键扫描爱睡；两个同优先级任务轮着抢 CPU；低优先级的串口上报总被抢。"""
    return [
        Task("按键扫描", 3, [("run", 2), ("delay", 5)] * 4),   # 优先级最高，爱睡
        Task("LED流水灯", 2, [("run", 4), ("delay", 6)] * 3),  # 中优先级
        Task("舵机控制", 2, [("run", 3), ("delay", 7)] * 3),   # 和上面同优先级 → 时间片轮转
        Task("串口上报", 1, [("run", 5), ("delay", 3)] * 2),   # 低优先级，总被抢占
    ]


MAX_PRIO = 3    # 优先级范围 0..3（0 留给 FreeRTOS 的空闲任务，这里不用）
QUANTUM = 3     # 时间片长度（FreeRTOS 默认 1 tick，这里拉长 3 tick 方便看清轮转）


# ---------------------------------------------------------------------------
# 4. FreeRTOS 风格调度器 —— 这是主角。
#    就绪队列 = 链表的数组（按下标=优先级），抢占式 + 时间片轮转。
# ---------------------------------------------------------------------------

class ListScheduler:
    def __init__(self, tasks):
        self.tasks = tasks
        self.ready = [DList() for _ in range(MAX_PRIO + 1)]   # 下标 = 优先级
        self.delayed = DList()                                # 按唤醒时刻升序
        self.running = None
        self.events = []
        self.tick = 0

    def _add_ready(self, t):
        t.ready_node = DNode(t)
        self.ready[t.priority].insert_tail(t.ready_node)

    def highest_ready_prio(self):
        """从高往低扫，找第一个非空的就绪链表。
        真实 FreeRTOS 用 uxTopReadyPriority 记住最高的那个，免得每次扫。"""
        for p in range(MAX_PRIO, -1, -1):
            if not self.ready[p].is_empty():
                return p
        return None

    def _pick_next(self):
        p = self.highest_ready_prio()
        if p is None:
            return None
        node = self.ready[p].pop_head()
        t = node.item
        t.ready_node = None
        t.slice_used = 0
        t.state = "RUNNING"
        return t

    def _preempt(self, reason):
        """把当前运行任务放回就绪队列尾部（被抢占 或 时间片用完）。"""
        cur = self.running
        cur.state = "READY"
        self._add_ready(cur)
        self.running = None
        if reason == "preempt":
            self.events.append((self.tick, f"{cur.name} 被更高优先级抢占 → 回到就绪"))
        else:
            self.events.append((self.tick, f"{cur.name} 时间片用完 → 轮转"))

    def run(self, max_ticks=200):
        for t in self.tasks:
            self._add_ready(t)
            self.events.append((0, f"{t.name}（优先级{t.priority}）创建，进入就绪"))

        while self.tick < max_ticks and not all(t.state == "DONE" for t in self.tasks):
            # ① 唤醒延时到期的任务（延时链表按唤醒时刻排序，只看表头即可）
            while not self.delayed.is_empty():
                head_t = self.delayed.head_item()
                if head_t.wake_time > self.tick:
                    break
                self.delayed.pop_head()
                head_t.delayed_node = None
                if head_t.step >= len(head_t.schedule):
                    # 脚本已经耗尽：最后一段正是延时，唤醒即完成，不再占 CPU
                    head_t.state = "DONE"
                    self.events.append((self.tick, f"{head_t.name} 全部任务完成"))
                else:
                    head_t.state = "READY"
                    self._add_ready(head_t)
                    self.events.append((self.tick, f"{head_t.name} 延时结束，回到就绪"))

            # ② 抢占判断：有更高优先级就绪 → 抢；时间片用完 → 轮转
            if self.running is not None and self.running.state == "RUNNING":
                hp = self.highest_ready_prio()
                if hp is not None and hp > self.running.priority:
                    self._preempt("preempt")
                elif self.running.slice_used >= QUANTUM:
                    self._preempt("slice")

            # ③ 没任务在跑，就挑一个最高优先级的
            if self.running is None:
                self.running = self._pick_next()
                if self.running is not None:
                    self.events.append((self.tick, f"{self.running.name} 开始运行"))

            # ④ 记录本 tick 每个任务的状态（用于画时序图）
            for t in self.tasks:
                t.hist.append(self._char(t))

            # ⑤ 消耗 1 个 tick
            if self.running is not None:
                self.running.t_run += 1
                self.running.slice_used += 1
                keep = self.running.consume_tick(self.tick)
                if not keep:
                    cur = self.running
                    self.running = None
                    if cur.state == "DELAYED":
                        cur.delayed_node = DNode(cur)
                        self.delayed.insert_sorted(cur.delayed_node, cur.wake_time)
                        self.events.append((self.tick,
                            f"{cur.name} 延时 {cur.wake_time - self.tick} tick → 唤醒时刻 {cur.wake_time}"))
                    else:
                        self.events.append((self.tick, f"{cur.name} 全部任务完成"))

            self.tick += 1

    def _char(self, t):
        """每个 tick 的状态字符：█运行 ░就绪·被抢占 空格=阻塞 ·=完成"""
        if t.state == "RUNNING":
            return "█"
        if t.state == "READY":
            t.t_ready += 1
            return "░"
        if t.state == "DELAYED":
            t.t_blocked += 1
            return " "
        return "·"


# ---------------------------------------------------------------------------
# 5. 教科书对照版：小顶堆调度器。
#    就绪任务都扔进堆，每次 O(log n) 拿到最高优先级；但没有时间片轮转。
#    —— 为什么要给你看两个版本？因为"选哪个结构"就是数据结构课的核心问题。
# ---------------------------------------------------------------------------

class HeapScheduler:
    def __init__(self, tasks):
        self.tasks = tasks
        self.heap = MinHeap()
        self.seq = 0
        self.delayed = DList()
        self.running = None
        self.tick = 0

    def _ready_push(self, t):
        self.heap.push(-t.priority, self.seq, t)   # 负数：优先级越大 key 越小，越先出
        self.seq += 1

    def run(self, max_ticks=200):
        for t in self.tasks:
            self._ready_push(t)

        while self.tick < max_ticks and not all(t.state == "DONE" for t in self.tasks):
            # 唤醒延时到期的任务
            while not self.delayed.is_empty():
                head_t = self.delayed.head_item()
                if head_t.wake_time > self.tick:
                    break
                self.delayed.pop_head()
                if head_t.step >= len(head_t.schedule):
                    head_t.state = "DONE"     # 脚本耗尽，唤醒即完成
                else:
                    head_t.state = "READY"
                    self._ready_push(head_t)

            # 堆顶是严格更高优先级 → 切换；否则继续跑（无时间片轮转）
            if self.running is not None and len(self.heap) and \
               self.heap.peek()[0] < -self.running.priority:
                self._ready_push(self.running)
                self.running.state = "READY"
                self.running = None
            if self.running is None and len(self.heap):
                _, _, t = self.heap.pop()
                t.state = "RUNNING"
                self.running = t

            for t in self.tasks:
                t.hist.append(self._char(t))

            if self.running is not None:
                self.running.t_run += 1
                keep = self.running.consume_tick(self.tick)
                if not keep:
                    cur = self.running
                    self.running = None
                    if cur.state == "DELAYED":
                        cur.delayed_node = DNode(cur)
                        self.delayed.insert_sorted(cur.delayed_node, cur.wake_time)
            self.tick += 1

    def _char(self, t):
        if t.state == "RUNNING":
            return "█"
        if t.state == "READY":
            t.t_ready += 1
            return "░"
        if t.state == "DELAYED":
            t.t_blocked += 1
            return " "
        return "·"


# ---------------------------------------------------------------------------
# 6. 输出：事件日志 + 时序图 + 任务小结 + 自检断言
# ---------------------------------------------------------------------------

TABLE = """
┌──────────────────────────────────────────────────────────────────────────┐
│ 数据结构对照表：你刚亲手写的东西，正是下学期课程里的概念                        │
├───────────────────────────────┬──────────────────────┬────────────────────┤
│ 本程序里                      │ 数据结构课概念        │ 真实 FreeRTOS        │
├───────────────────────────────┼──────────────────────┼────────────────────┤
│ DList（双向链表+哨兵头）       │ 链表                 │ List_t / xLIST      │
│ ready_lists[优先级] 数组       │ 链表的数组=索引表     │ pxReadyTasksLists   │
│ delayed_list（按唤醒时刻排序） │ 有序链表             │ pxDelayedTaskList   │
│ MinHeap 调度器（对照实验）     │ 优先队列 / 堆        │ ——（教学对照用）     │
│ task.state 状态机             │ 状态机 / 图          │ eTaskState          │
└───────────────────────────────┴──────────────────────┴────────────────────┘
"""


def render(tasks, title):
    n = max(len(t.hist) for t in tasks)
    print(f"\n{title}")
    print("tick  " + "".join(str(i % 10) for i in range(n)))
    for t in tasks:
        name = f"{t.name}({t.priority})"
        print(f"{name:<12} {''.join(t.hist)}")
    print("图例：█ 运行 | ░ 就绪·被抢占 | 空格 阻塞/延时 | · 已完成")


def print_summary(tasks):
    total = max(len(t.hist) for t in tasks)
    print("\n任务小结（全程 %d tick）：" % total)
    for t in tasks:
        print(f"  {t.name:<8} 运行{t.t_run:>3} tick  就绪等CPU{t.t_ready:>3}  阻塞{t.t_blocked:>3}"
              f"   利用率{t.t_run * 100 // total:>3}%")


def self_check(tasks):
    """不变量断言 —— 这也是离散数学"程序正确性"的入门姿势。"""
    ok = True
    n = len(tasks[0].hist)
    for t in tasks:
        exp = t.expected_run_ticks()
        if t.t_run != exp:
            ok = False
            print(f"  ✗ {t.name}: 实际运行 {t.t_run} tick，脚本里承诺 {exp}")
        if t.hist.count("█") != t.t_run:
            ok = False
            print(f"  ✗ {t.name}: 时序图里运行块数 {t.hist.count('█')} ≠ t_run {t.t_run}")
    for i in range(n):
        runners = [t.name for t in tasks if t.hist[i] == "█"]
        if len(runners) > 1:
            ok = False
            print(f"  ✗ tick {i} 同时有多个任务在跑：{runners}")
    print("  自检：" + ("全部通过 ✅" if ok else "发现不一致 ✗"))
    return ok


def main():
    print(TABLE)

    print("=" * 60)
    print("主角：FreeRTOS 风格调度器（就绪=链表的数组，抢占+时间片轮转）")
    print("=" * 60)
    tasks = build_scenario()
    sched = ListScheduler(tasks)
    sched.run()
    print("\n【事件日志】")
    for tick, msg in sched.events:
        print(f"  t={tick:<3} {msg}")
    render(tasks, "【时序图】")
    print_summary(tasks)
    self_check(tasks)

    print("\n" + "=" * 60)
    print("对照实验：小顶堆调度器（纯优先级抢占，无时间片轮转）")
    print("=" * 60)
    tasks2 = build_scenario()
    hs = HeapScheduler(tasks2)
    hs.run()
    render(tasks2, "【时序图】")
    print_summary(tasks2)
    self_check(tasks2)

    print("\n思考题：")
    print("  ① 两个调度器输出的时序图哪里不一样？为什么？")
    print("  ② 谁更适合时间片轮转？堆能做到同优先级轮转吗？要付出什么代价？")
    print("  ③ 真实 FreeRTOS 用链表数组：最高优先级 O(1) 可得。堆是 O(log n)。")
    print("     但 FreeRTOS 的任务数量通常 < 几十个，二者差距大吗？")


if __name__ == "__main__":
    main()
