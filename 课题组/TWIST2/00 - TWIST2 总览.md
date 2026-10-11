---
title: "TWIST2 总览"
aliases:
  - TWIST2
type: paper-project-note
tags:
  - 人形机器人
  - 遥操作
  - 数据采集
  - loco-manipulation
  - motion-tracking
paper: "https://arxiv.org/abs/2511.02832"
repo: "https://github.com/amazon-far/TWIST2"
project: "https://yanjieze.com/TWIST2"
data: "https://twist-data.github.io"
created: 2026-10-11
status: 仓库已通读（master @ b06178f）
---

# TWIST2 总览

> [!abstract] 一句话
> TWIST2 = 不依赖光学动捕的**人形机器人全身遥操作 + 数据采集 + 模仿学习**全栈系统。用 PICO 4 Ultra 全身动捕驱动 Unitree G1，把"采数据"当作第一目标，并用 RL 全身追踪器作为可规模化的执行层。

## 基本信息

| 项 | 内容 |
| --- | --- |
| 论文 | TWIST2: Scalable, Portable, and Holistic Humanoid Data Collection System |
| arXiv | 2511.02832（2025-11-04） |
| 作者 | Yanjie Ze, Siheng Zhao, Weizhuo Wang, Angjoo Kanazawa, Rocky Duan, Pieter Abbeel, Guanya Shi, Jiajun Wu, C. Karen Liu |
| 开源 | [amazon-far/TWIST2](https://github.com/amazon-far/TWIST2)，MIT License |
| 热度 | 约 881 star / 95 fork（2026-10-11 抓取） |
| 开源时间 | 2025-12-02 |
| 克隆位置 | `C:\Users\Hohokam\AppData\Local\Temp\TWIST2_repo`（临时目录，约 37 MB，重启可能被清理） |

## 三个关键词

- **Scalable**：15 分钟采 100 条演示、成功率接近 100%；数据格式直接面向 VLA / visuomotor policy。
- **Portable**：不需要动捕棚。PICO 4 Ultra 全身动捕 + 笔记本（或机载计算）就能搭起采集系统。
- **Holistic**：全身（腿 + 腰 + 双臂 + 灵巧手）+ 头部第一人称视觉统一遥操作。约 250 美元的 2-DoF 云台脖子 + ZED Mini 相机让操作者看到机器人视角，而不是只控制手臂。

## 关键数字

| 指标 | 数值 |
| --- | --- |
| 机器人 | Unitree G1，29 DoF（可选 Dex3-1 手） |
| 低层策略频率 | 训练与真机 50 Hz（仿真物理 500 Hz，decimation=10；README 实测笔记本约 39 Hz）。注意 `sim2sim.sh` 当前传 100 Hz，见 [[04 - 复现清单与避坑]] |
| 遥操作流 | 目标 100 Hz |
| 数据录制 | 30 Hz；RGB 360x1280 双目 + 本体/手状态与动作 + 文本描述 |
| 策略输入 | 1402 维 = 127x11 帧历史 + 35 维当前动作参考 |
| 模型体积 | ONNX 约 3 MB（`twist2_1017_20k.onnx` / `25k.onnx`） |
| 脖子成本 | 约 250 美元（2x Dynamixel 舵机） |

## 技术谱系

- 前作：[TWIST: Teleoperated Whole-Body Imitation System](https://arxiv.org/abs/2505.02833)（2505.02833）。TWIST2 去掉动捕依赖，补上数据采集与规模化。
- 在线重定向：独立仓库 [YanjieZe/GMR](https://github.com/YanjieZe/GMR)（General Motion Retargeting，2510.02252）。TWIST2 官方指定用它做人体 -> G1 的映射。
- 上层策略：基于 [iDP3](https://github.com/YanjieZe/Improved-3D-Diffusion-Policy) 修改的分层 visuomotor policy，**不在本仓库**，作者声明会另开仓库。
- 数据来源：AMASS、OMOMO（仅限研究用途）；`assets/example_motions/*.pkl` 是作者自录的 10 条示例动作。

## 笔记导航

- [[01 - 硬件与系统架构]]：硬件清单、软件分层、目录结构、解耦设计
- [[02 - 算法与训练细节]]：观测/奖励/域随机化/teacher-student/ONNX
- [[03 - 数据流与遥操作管线]]：Redis 键、状态机、录制格式、sim2sim/sim2real
- [[04 - 复现清单与避坑]]：安装顺序、最小验证路径、已知坑
- [[05 - 对标课题组方向]]：与 IMU 动捕、ego 数据、loco-manipulation 的结合点

相关旧笔记：[[论文]]、[[数据采集领域]]、[[预习作业]]

## 复现状态

- 2025-12-02 已有第三方成功复现（B 站有视频），作者预告了视频教程，但文档仍在完善。
- 仓库给全了低层 ckpt、示例动作、训练脚本；**上层 visuomotor 策略与机载 neck/ZED 推流代码不在仓库**（README Disclaimer 2/3）。
- 37 个 open issues；master 最近提交 2026-09-23（仅 README news 更新）。

## 引用

```bibtex
@article{ze2025twist2,
  title={TWIST2: Scalable, Portable, and Holistic Humanoid Data Collection System},
  author={Yanjie Ze and Siheng Zhao and Weizhuo Wang and Angjoo Kanazawa and Rocky Duan and Pieter Abbeel and Guanya Shi and Jiajun Wu and C. Karen Liu},
  year={2025},
  journal={arXiv preprint arXiv:2511.02832}
}
```
