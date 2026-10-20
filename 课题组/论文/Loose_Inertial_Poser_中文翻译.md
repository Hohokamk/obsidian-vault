# Loose Inertial Poser：基于 IMU 附着宽松夹克的运动捕获

> 原文：Chengxu Zuo¹, Yiming Wang¹, Lishuang Zhan¹, Shihui Guo¹\*, Xinyu Yi², Feng Xu², Yipeng Qin³
> ¹厦门大学信息学院　²清华大学软件学院与 BNRist　³英国卡迪夫大学计算机科学与信息学院
> 出处：CVPR 2024, pp. 2209–2219　DOI: 10.1109/CVPR52733.2024.00215
> 代码与数据：https://github.com/ZuoCX1996/Loose-Inertial-Poser
> 翻译说明：本文为完整中文译稿，公式编号与原刊一致；参考文献按原序保留。术语对照见文末。

---

## 摘要

现有的可穿戴运动捕获方法通常要求传感器紧贴身体固定（往往使用绑带）才能获得可靠测量，这限制了它们在日常生活中的应用。本文提出 **Loose Inertial Poser（LIP）**——一种通过将四个惯性测量单元（IMU）集成到一件宽松穿着的夹克中实现的、具有高穿着舒适度的新型动作捕捉方案。

具体而言，针对宽松穿着 IMU 训练数据匮乏这一挑战，我们提出 **二次运动自编码器（Secondary Motion AutoEncoder, SeMo-AE）**，用于学习建模并合成皮肤与宽松衣物之间的二次运动对 IMU 数据产生的效应。SeMo-AE 被用于生成多样化的宽松穿着 IMU 合成数据集，以扩充姿态估计网络的训练数据，并显著提升其精度。

为验证有效性，我们采集了一个包含多名被试、2 种穿着方式（拉链拉上 / 拉开）的数据集。实验结果表明，我们的方法即使在宽松穿着场景下，仍能维持高质量的实时姿态估计。

---

## 1. 引言

相较于基于视觉的方法，可穿戴动作捕获在便携性、隐私友好性以及对极端光照/遮挡的鲁棒性方面具有优势。近期工作已经能够用少量（3–6 个）IMU 实现姿态估计 [13, 16, 33, 54, 55]。然而，这些方法仍要求 IMU 传感器紧密附着于身体以获得稳定测量，这不可避免地带来了不舒适的穿着体验。

理想情况下，如果动作捕获可以直接用人们日常穿着的（大多是宽松的）衣服完成，用户的负担就能大幅降低，从而有利于慢性疾病监测、普适的以人体为中心的交互等应用。

使用宽松衣物会带来一个挑战：**衣物与人体之间的二次运动会降低 IMU 读数的质量**，使身体朝向与加速度的测量出现偏差。应对这种数据波动的直接做法，是用覆盖所有可能二次运动的大量数据来训练模型。天真地说，这类数据可以通过在已有的人体姿态数据集上模拟"带 IMU 的衣物"来采集。然而在宽松穿着的情形下，IMU 数据模拟应当涵盖各种体型与穿衣风格，这意味着数据模拟必须覆盖极广的场景范围。即使用了基于深度学习的衣物仿真 [37]（比物理仿真快约 1000 倍），在可接受的时间范围内穷举所有穿着条件仍然不可行。

本文提出 Loose Inertial Poser（LIP），通过固定在一件宽松夹克上的稀疏 IMU 实现实时且准确的姿态估计（图 1）。为应对上述数据稀缺问题，我们提出二次运动自编码器（SeMo-AE）来建模并合成皮肤与宽松衣物之间的二次运动对 IMU 数据的影响。SeMo-AE 由两项新技术构成：

**第一，噪声引导的隐空间学习（noise-guided latent space learning）。** 我们学习一个隐空间，其假设为：(i) IMU 信号与二次运动的效应在该隐空间中服从可加关系；(ii) 二次运动的隐表示（即噪声）服从高斯分布。本文方法的关键洞见是：仿真数据中有限的二次运动样本，难以为一个额外的生成器网络提供足够的约束。因此，利用一个已被重构损失充分约束的自编码器、再让它额外满足一个高斯先验，会更加有效，从而有效缓解模型对数据的饥饿问题。

**第二，时间一致性方案（temporal coherence scheme）。** 我们建模二次运动在相邻帧之间的依赖关系，从而得到抖动更小、结果更真实的效果。该方案基于一个关键观察：宽松穿着下的 IMU 信号随时间往往平滑形变，表现出局部时间一致性。

训练完成后，我们将 SeMo-AE 与姿态估计网络串联，为网络提供无限量的模拟即席数据（ad-hoc data），以训练其估计宽松衣物下姿态的能力。

为验证方法有效性，我们采集了一个覆盖不同用户与不同穿着方式的真实世界测试数据集。大量实验结果表明，我们的方法能够有效适应不同穿着条件，平均关节旋转误差低于 20 度。

**本文主要贡献：**

- 我们提出了一种利用内嵌少量 IMU 传感器的宽松衣物来实现实时、准确的人体动作捕获的方法，保证了用户穿着体验的舒适性。
- 我们提出了一个新颖的**二次运动自编码器（SeMo-AE）**网络，用于合成宽松穿着 IMU 数据。SeMo-AE 将二次运动建模为隐空间中的可加高斯噪声，从而仅凭非常有限的仿真数据集，通过对该高斯噪声分布采样就能生成具有新颖二次运动效果的合成 IMU 数据。
- 我们提出了一种**时间一致性方案**，用于建模二次运动的局部时间一致性，从而减少抖动、产生更真实的结果。

---

## 2. 相关工作

### 2.1 动作捕获

我们将动作捕获方法大致分为基于视觉与非基于视觉两类 [10, 30]。

**基于视觉的方法。** 传统光学动作捕获系统使用多相机与标记点 [5, 9, 22]，如 OptiTrack [39] 等商业系统。近年来深度学习的进展为无标记动作捕获开辟了新的可能 [41]。单目 2D/3D 姿态估计方法如 HRNet [45]、SMAP [59]、PARE [20]、ViTPose [51] 等 [23, 51, 52, 58] 在人体姿态估计上取得了显著进展。此外，使用 RGB-D 数据 [17, 56, 63] 或多视角图像 [49, 53, 57] 的方法，不仅提升了精度，也缓解了图像缺乏深度信息带来的挑战。

**非基于视觉的方法。** 这类方法通常使用可穿戴传感器捕获人体运动 [11]。惯性传感器（主要由加速度计与陀螺仪构成）为基于视觉的动作捕获系统提供了一种有效的替代方案 [21]。商业惯性动作捕获系统如 Xsens [38] 与 Noitom [35]，在身体各关节处固定多个 IMU 以实现准确的姿态估计。

当前研究的一个重点是探索稀疏 IMU 的配置方案，目标是降低成本与侵入性，同时保持动作捕获的精度。本文沿这一方向，使用 4 个 IMU 进行上半身动作捕获。

作为新兴方向，稀疏惯性动作捕获以有限的感知输入重建运动信息。研究者尝试用统计优化或深度学习两类方法来解决这一问题。Marcard 等人 [46] 利用 6 个 IMU 的数据重建人体运动，但由于其基于优化的本质，处理整段序列需要相当长的时间。相比之下，深度学习方法可以用少量过去帧学习预测当前运动状态，以更低的延迟换取近实时效果。例如，Huang 等人 [13] 通过双向 RNN 实现了稀疏 IMU 的实时人体动作捕获，但该方法仅限于估计人体姿态，忽略了身体位移。

另一项工作 TransPose [54] 通过整合多阶段姿态估计与混合的全局位移估计，进一步推进了稀疏 IMU 动捕，并在后续工作 [55] 中加入了物理动力学优化模块。Jiang 等人 [16] 将 Transformer 引入稀疏惯性动作捕获，同时考虑非平面场景中的人体运动。在此基础上，他们完成了动捕任务并为人体运动轨迹生成了地形高度图。在实际应用领域 [4, 15, 48]，Ponton 及其团队 [40] 使用 6 个六自由度 VR 追踪器，结合卷积自编码器与基于学习的逆运动学调整组件，实现了实时的全身姿态重建。此外，还有一些研究将稀疏 IMU 与其他形式的信息结合起来 [1, 7, 34, 47, 60]。例如 Pan 等人 [36] 融合了图像与稀疏 IMU 的信号输入，得到更鲁棒的动作捕获结果。

尽管使用了稀疏的传感器，当前方法仍主要用绑带把 IMU 固定在特定位置。这提供了相对准确的信息，但固定方式引入了明显的刚性贴身装置感，损害了用户体验。

### 2.2 服装上的动作捕获

另一种思路是不把可穿戴传感器当作"可贴附的器件"，而是把动作捕获能力集成进服装本身 [6]。主流做法是在紧身衣的关键关节位置固定标记点或惯性传感器，例如 TESLASUIT [44] 动捕服在其紧身衣上集成了 14 个 IMU。另一项工作 [2] 使用稀疏时空同步的红外深度相机与光学标记点，在紧身衣上实现了端到端的动作捕获。在智能服装领域，柔性织物传感器也受到关注 [12, 26, 42]。例如，Chen 等人 [3] 使用 6 个柔性可拉伸传感器置于护肘上预测关节弯曲角。Liang 及其团队 [24] 利用压敏织物材料制作服装，通过用户对衣物施加的压力分布来识别特定身体姿态。近期一项工作 [64] 提出了自适应动作跟踪模型，以应对柔性传感器在运动中因未知位移而产生的数据偏移问题。

上述研究主要用紧身衣以获取准确数据，但宽松衣物更符合消费者的偏好以及日常场景下的舒适性考虑。近期一些工作研究了基于宽松衣物的人体姿态估计 [8, 29, 50]。例如，Zhou 等人 [61] 将多通道电容传感器集成进夹克，利用深度回归器从 16 通道织物电容传感器预测上半身关节坐标。Lorenz 等人 [28] 探索了用多个 IMU 将宽松衣物上的动作数据映射到紧身衣，但泛化能力有限。虽然有部分研究将附着于衣物的 IMU 用于活动识别任务 [14, 25, 31, 43]，但**宽松衣物上的稀疏惯性感知这一挑战仍缺乏充分研究**。

---

## 3. 硬件

图 2 展示了用于上半身动作跟踪的宽松夹克原型。不失一般性地，我们选择上半身来验证方法的有效性；对设备与流程做适当修改后，本文方法同样可以有效应用于下半身场景。

衣物材质为 100% 聚酯纤维，采用标准 XL 码。衣物基于一款商业户外夹克的原始版型制作。典型围度参数为：肩宽 52 cm、胸围 106 cm、腰围 110 cm、袖口 28 cm，适合身高 170–185 cm、体重 60–85 kg 的被试。袖口位置的特写视图直观展示了其宽松穿着特征（图 2）。

对于上半身姿态估计，这件宽松夹克装备了 4 个 IMU 传感器，型号为 Xsens MTI-3。IMU 分别布置在左前臂、右前臂、后背（与传感读取板集成）、腰部。所有 IMU 通过柔性线缆连接到传感读取板，线缆经热压固定在衣物上，与衣物无缝集成。读取板以 30 Hz 采集各 IMU 数据，并通过蓝牙无线传输至计算机。整个电子系统由一块 1000 mAh 锂电池供电（一次充电约相当于 5 小时）。这一多 IMU 配置使我们能够通过融合全部 4 个传感器位置朝向测量来捕获上半身运动。

**挑战 1（硬件）。** 尽管显著提升了穿着舒适性，但衣物与皮肤之间的松散耦合会诱发二次运动，它对 IMU 测量构成一个复杂的扰动。这与以往聚焦紧身可穿戴器件的工作 [13, 16, 33, 54, 55] 形成对比——在那些工作中衣物与底层身体分段同步运动，因而得到的是更干净的 IMU 信号。

---

## 4. 背景与问题定义

**基于 IMU 的姿态估计。** 令 $\theta(t) \in \mathbb{R}^{J\times3}$ 表示时刻 $t$ 定义在 $J$ 个关节上的三维旋转角。衣物内的 IMU 传感网络由 $M$ 个 IMU 构成，位置记为 $s_m,\; m=1,\dots,M$。第 $m$ 个 IMU 测量加速度 $a_m(t)\in\mathbb{R}^3$ 与旋转 $R_m(t)\in\mathbb{R}^{3\times3}$。我们采用两阶段流水线来学习关节位置 $p(t)\in\mathbb{R}^{J\times3}$、$\theta(t)$ 与 IMU 信号 $\mathrm{IMU}(t)=(\{a_1(t),\dots,a_m(t)\},\{R_1(t),\dots,R_m(t)\})$ 之间的映射：

$$
\begin{aligned}
p(t) &= \mathrm{LSTM}(\mathrm{IMU}(t), H) \\
\theta(t) &= \mathrm{LSTM}(p(t), \mathrm{IMU}(t), H)
\end{aligned}
\tag{1}
$$

其中 $H$ 表示 LSTM 编码的运动历史，我们用 $J=10$ 表示上半身关节。注意，由于宽松穿着的特性，腰部 IMU 的旋转测量**不能**直接用作骨盆旋转。因此我们的模型引入了单独的骨盆旋转估计，这与紧身情形不同。

**基于宽松穿着 IMU 的姿态估计。** 如前所述，宽松穿着的 IMU 会诱发二次运动，它给理想的紧身 IMU 信号 $\mathrm{IMU}(t)$ 叠加了扰动 $\delta(t)$，即

$$
\widetilde{\mathrm{IMU}}(t) = f\big(\mathrm{IMU}(t),\, \delta(t)\big)
\tag{2}
$$

其中 $f$ 是未知函数；$\delta(t)$ 由用户姿态、体型、衣物合身度等多种因素决定，表现出复杂非线性的动力学特性并带有难以解析建模的随机成分。

尽管困难重重，$f$ 与 $\delta(t)$ 都可以通过式 (1) 以数据驱动的方式估计，前提是假设有从宽松 IMU 采集的充足运动数据。然而由于前述各种影响 $\delta(t)$ 的因素，这一假设难以满足。于是我们面临：

**挑战 2（软件）。** 深度学习为从宽松 IMU 估计姿态提供了可行方案，但它依赖充足训练数据的可获得性。然而跨用户姿态、体型、衣物合身度与随机性去采集多样化的真实动作捕获数据，会带来实际的数据稀缺难题。

因此，迫切需要一种合成数据生成方法，能够产生真实且多样的宽松穿着 IMU 信号以训练姿态估计模型，可形式化为：

$$
\widetilde{\mathrm{IMU}}(t, z) = G\big(\mathrm{IMU}(t), z\big)
\tag{3}
$$

其中 $G$ 表示一个深度生成模型，$z$ 表示 $G$ 中使用的噪声向量（通常从标准正态分布采样），用于刻画 $\delta(t)$ 中的随机性。

---

## 5. 二次运动自编码器（SeMo-AE）

### 5.1 噪声引导的隐空间学习

我们为二次运动建模与宽松 IMU 数据合成提出一个新的自编码器框架（图 3），记其编码器为 $E$、解码器为 $D$。我们的核心思想是利用深度神经网络的通用逼近能力，学习一个隐空间，使得：

- $\delta(t)$ 由 $E(\widetilde{\mathrm{IMU}}(t,z)) - E(\mathrm{IMU}(t)) = z$ 捕获；
- $z$ 服从正态分布，即 $z \sim \mathcal{N}(\mu, \sigma^2)$；

这样我们就可以把二次运动建模为隐空间中的高斯噪声。与"在给定隐空间中学习 $z$ 的分布"这一朴素做法不同，我们反过来——**学习一个使 $z$ 的分布预先确定的隐空间**，故称之为噪声引导的隐空间学习。

**训练。** 给定训练数据 $\mathrm{IMU}(t)$ 与 $\widetilde{\mathrm{IMU}}(t)$，我们将其送入编码器 $E$，并用重参数化方法 [19] 与最大均值差异（MMD）损失 $\mathcal{L}_{mmd}$ [27] 实现噪声引导的隐空间学习。该损失衡量批归一化后的 $E(\widetilde{\mathrm{IMU}}(t,z)) - E(\mathrm{IMU}(t))$ 与标准正态分布之间的分布距离：

$$
\mathcal{L}_{mmd} = \mathrm{MMD}\Big( \mathrm{BN}\big(E(\widetilde{\mathrm{IMU}}(t,z)) - E(\mathrm{IMU}(t))\big) \Big)
\tag{4}
$$

其中 BN 表示批归一化层。我们采用批归一化的动机与它在常规训练优化中的用途不同：在我们的场景中，若直接要求 $E(\widetilde{\mathrm{IMU}}(t,z)) - E(\mathrm{IMU}(t))$ 服从某个特定参数化的高斯分布（例如每一维 $\mu=0,\sigma=1$），可能会压缩解空间、阻碍模型收敛到潜在更优的解。因此我们把批归一化引入 $\mathcal{L}_{mmd}$，从而保证 $E(\widetilde{\mathrm{IMU}}(t,z)) - E(\mathrm{IMU}(t))$ 的**任意**参数化高斯分布都能最小化 $\mathcal{L}_{mmd}$。

配合自编码器中标准的 MSE 重构损失：

$$
\mathcal{L}_{recon} = \frac{1}{n}\sum_{t=1}^{n} \Big\| D(E(\mathrm{IMU}(t))) - \mathrm{IMU}(t) \Big\|_2^2 + \Big\| D(E(\widetilde{\mathrm{IMU}}(t))) - \widetilde{\mathrm{IMU}}(t) \Big\|_2^2
\tag{5}
$$

我们用总体损失函数训练模型：

$$
\mathcal{L} = \mathcal{L}_{recon} + \mathcal{L}_{mmd}
\tag{6}
$$

**推理。** 训练完成后，我们可通过下式生成多样化的宽松穿着 IMU 合成数据：

$$
\widetilde{\mathrm{IMU}}(t, z) = D\big(E(\mathrm{IMU}(t)) + z\big)
\tag{7}
$$

其中 $z \sim \mathcal{N}(\mu,\sigma^2)$，$\mu$ 与 $\sigma$ 由批归一化层获得。当不进行合成（$z$ 省略）时，即为训练数据本身。

**数据外推。** 为生成二次运动程度更高的合成数据，我们向 $z$（式 7）中引入一个可控的"松散度"参数 $\eta$（$\eta>1$）：

$$
z^* \sim \mathcal{N}\big(\mu, (\eta\sigma)^2\big)
\tag{8}
$$

在 SeMo-AE 的推理中我们取 $\eta = 2$。经验上我们发现，这类外推数据能改善姿态估计模型的训练效果（见补充材料）。

### 5.2 时间一致性方案

尽管式 (7) 很有效，但它忽略了运动序列中相邻帧之间二次运动的时间一致性。为解决该问题，我们提出**时间一致性方案**——一种把噪声 $z$ 线性插值为 $z(t)$ 的启发式做法：

$$
z(t) = \left(1 - \frac{t}{n}\right) z(1) + \frac{t}{n} z(n)
\tag{9}
$$

其中 $z(1), z(n) \sim \mathcal{N}\big(\mu, (\eta\sigma)^2\big)$，$n$ 是由用户指定的超参数，控制整个运动序列上插值的长度。直观地说，$n$ 越大，合成的 IMU 信号越平滑。于是有：

$$
\widetilde{\mathrm{IMU}}(t, z(t)) = D\big(E(\mathrm{IMU}(t)) + z(t)\big)
\tag{10}
$$

值得注意的是，当 $n=2$ 时，式 (10) 退化为式 (7)。基于噪声向量序列 $z$ 的自相关分析（见补充材料），我们在工作中取 $n=128$。

---

## 6. 实验

### 6.1 数据集与评价指标

**仿真数据集。** 该数据集由配对的宽松与紧身仿真 IMU 数据 $D_{Loose}^{sim}$ 与 $D_{Tight}^{sim}$ 组成，用于训练本文提出的 SeMo-AE：

- **$D_{Loose}^{sim}$**：首先我们用 TailorNet [37] 为 AMASS 数据集 [54]（超过 900 万帧）中的各种姿态仿真出对应的衣物模型。TailorNet 能在给定 SMPL 姿态与体型的情况下快速仿真拓扑一致的衣物，满足 IMU 数据仿真的需求。我们从作者提供的模型中选择了与其宽松夹克最相近的 Shirt 模型。此外，我们把 SMPL 模型的体型配置为 Tall Thin，以确保衣物与皮肤之间留有更大空间——这一配置能更准确地刻画宽松穿着的scenario。总体而言，仅这一次仿真在 NVIDIA RTX 4080 上耗时约 4 天。随后，为仿真一个 IMU，我们基于其在夹克中的位置选取仿真衣物上的 4 个邻近顶点，用以描述 2 个轴向方向，再通过叉积计算出第三个轴向以模拟朝向测量；同时用这 4 个顶点的几何中心作为 IMU 位置来仿真加速度。
- **$D_{Tight}^{sim}$**：我们用上述方法把虚拟 IMU 直接放置在 AMASS 数据集 [54] 的人体网格上，以仿真紧身佩戴的 IMU 信号。特别地，我们调整了关节与网格顶点设置，使之匹配我们上半身 IMU 的布置（左前臂、右前臂、后背、腰部）。

**合成数据集（按需生成）。** 我们用提出的 SeMo-AE 按需合成新的宽松穿着 IMU 数据，记为 $D_{Loose}^{gen}$，为姿态估计网络提供训练数据。

**测试数据集（真实）。** 我们招募了共 5 名体型各异的被试，使用集成了 4 个 IMU 的宽松夹克采集真实世界数据集 $D_{Loose}^{real}$ 用于评估。所有被试均已知晓实验目的并签署了知情同意书，其体型尺寸适配所设计的衣物；被试身体特征的更多信息见补充材料。每位被试被要求以两种不同的穿着方式采集数据：拉链拉上与拉开。采集过程中，被试需完成 5 个预定义动作（walking 走、running 跑、jumping 跳、boxing 拳、ping-pong 乒乓球），以及 5 次自由活动。每个动作持续 1 分钟。真值姿态方面，我们使用 Perception Neuron 3 系统 [35]，以 11 个紧身 IMU 捕获上半身姿态。总体上我们采集了 212,496 帧 30 fps 数据，总时长约 2 小时。

**评价指标。** 沿用 TransPose [54]，我们用两个指标度量姿态估计精度：1）角度误差，度量 10 个上半身关节的平均旋转误差（度）；2）位置误差，度量 12 个上半身关节端点的平均欧氏距离误差（厘米）。注意，实际中我们只计算 11 个关节端点的位置误差，因为骨盆关节位置被固定为 $[0,0,0]$。

### 6.2 训练细节

**IMU 数据格式。** 我们对所有模型都使用 IMU 的加速度与旋转测量作为输入。沿用 TransPose [54]，我们对 IMU 数据做了归一化，将左、右、背三个 IMU 的加速度与旋转测量转换为相对于腰部 IMU 的相对值。为便于姿态估计网络的训练，我们把 IMU 的旋转读数转换为相应的 6D 表示 [62]。由此我们把 IMU 数据定义为 $I \in \mathbb{R}^{36}$，由 4 个 IMU 的三轴加速度与 6D 旋转拼接得到，即 $(3+6)\times 4 = 36$。

**训练设置。** 所有实验均在一台配备 Intel Core i7-13700KF CPU 与 NVIDIA RTX 4080 GPU 的计算机上运行。模型使用 PyTorch 1.12.1 与 CUDA 11.3 实现。

- **训练 SeMo-AE**：使用配对的 $D_{Loose}^{sim}$ 与 $D_{Tight}^{sim}$ 训练，批大小 512，Adam [18] 优化器，学习率 $lr = 1\times10^{-3}$。
- **训练姿态估计网络**：使用 $D_{Loose}^{gen}$ 训练，批大小 256，Adam 优化器，学习率 $lr = 5\times10^{-4}$。

SeMo-AE 与姿态估计网络的详细结构请参见补充材料。

### 6.3 与 SOTA 方法的对比

**定量结果。** 我们在测试集 $D_{Loose}^{real}$ 上与稀疏惯性动捕领域的最新方法（SOTA）对比，包括 DIP [13]、IMUPoser [33]、TransPose [54]、TIP [16] 与 PIP [55]。由于这些 SOTA 方法是为紧身 IMU 设计的，且传感器数量与安装位置各不相同，我们遵循作者提供的官方代码，用 $D_{Loose}^{sim}$ 重训练各模型，并报告其在 $D_{Loose}^{real}$ 上的角度误差与位置误差。

如表 1、表 2 所示，由于 $D_{Loose}^{sim}$ 的多样性较低，SOTA 方法在宽松 IMU 动捕上效果明显不佳。此外我们观察到，表现最好的 SOTA 方法 PIP 会输出异常的关节位置估计，使其物理感知的运动优化器无法正常工作。相比之下，我们的方法超越了包括 PIP 在内的所有 SOTA 方法，显示出对二次运动明显的鲁棒性优势。

**表 1｜五名被试上的角度误差（单位：度）。** s1 表示 ID = 1 的被试。

| ID | DIP | IMUPoser | TransPose | TIP | PIP | **Ours** |
|---|---|---|---|---|---|---|
| s1 | 25.63 ± 6.06 | 25.90 ± 6.33 | 24.60 ± 6.31 | 25.50 ± 6.93 | 23.34 ± 6.02 | **19.91 ± 5.86** |
| s2 | 25.16 ± 5.44 | 23.19 ± 5.07 | 22.99 ± 5.37 | 21.78 ± 6.35 | 19.97 ± 3.89 | **18.10 ± 4.55** |
| s3 | 30.31 ± 7.20 | 29.87 ± 7.50 | 28.51 ± 6.92 | 29.42 ± 8.53 | 26.35 ± 6.89 | **23.72 ± 7.54** |
| s4 | 26.20 ± 7.78 | 26.09 ± 7.49 | 26.75 ± 7.65 | 25.63 ± 8.42 | 22.05 ± 6.68 | **19.62 ± 7.98** |
| s5 | 24.62 ± 5.99 | 23.20 ± 5.76 | 23.17 ± 6.13 | 22.64 ± 6.99 | 19.78 ± 5.01 | **17.81 ± 5.84** |
| zipped（拉上） | 25.20 ± 6.54 | 24.59 ± 6.40 | 24.63 ± 6.44 | 24.05 ± 7.54 | 21.62 ± 6.08 | **18.74 ± 6.28** |
| unzipped（拉开） | 27.57 ± 6.92 | 26.67 ± 7.29 | 25.73 ± 7.19 | 25.87 ± 8.23 | 22.95 ± 6.39 | **20.98 ± 6.93** |
| all（全部） | 26.38 ± 6.85 | 25.63 ± 6.94 | 25.18 ± 6.85 | 24.97 ± 7.94 | 22.28 ± 6.28 | **19.83 ± 6.79** |

**表 2｜五名被试上的位置误差（单位：厘米）。**

| ID           | DIP          | IMUPoser     | TransPose    | TIP          | PIP          | **Ours**         |
| ------------ | ------------ | ------------ | ------------ | ------------ | ------------ | ---------------- |
| s1           | 16.85 ± 6.84 | 17.75 ± 6.57 | 17.69 ± 6.26 | 16.47 ± 6.47 | 17.01 ± 7.68 | **10.23 ± 5.12** |
| s2           | 15.19 ± 5.88 | 15.58 ± 5.16 | 15.50 ± 5.54 | 14.36 ± 6.31 | 13.83 ± 6.70 | **9.08 ± 4.80**  |
| s3           | 16.95 ± 6.63 | 18.63 ± 6.38 | 16.72 ± 6.26 | 16.17 ± 6.95 | 15.33 ± 6.62 | **11.21 ± 6.17** |
| s4           | 20.10 ± 7.99 | 20.67 ± 7.39 | 20.40 ± 7.36 | 19.06 ± 7.60 | 19.62 ± 9.33 | **12.67 ± 7.87** |
| s5           | 14.99 ± 6.39 | 16.45 ± 5.34 | 14.96 ± 5.78 | 15.19 ± 7.09 | 13.23 ± 6.76 | **9.86 ± 6.41**  |
| zipped（拉上）   | 16.91 ± 7.00 | 17.99 ± 6.58 | 17.58 ± 6.40 | 16.63 ± 7.38 | 16.61 ± 8.22 | **10.19 ± 6.08** |
| unzipped（拉开） | 16.61 ± 6.99 | 17.56 ± 6.29 | 16.41 ± 6.63 | 15.78 ± 6.71 | 14.87 ± 7.25 | **10.98 ± 6.56** |
| all（全部）      | 16.77 ± 7.00 | 17.78 ± 6.44 | 17.00 ± 6.54 | 16.20 ± 7.07 | 15.74 ± 7.80 | **10.58 ± 6.24** |

**定性结果。** 在图 4 中，我们在 5 个不同动作上就与真值的吻合度定性地比较了本文方法与 SOTA 方法。可以观察到，二次运动给 SOTA 方法的结果带来了显著误差，在幅度较大的前两个动作上尤其明显。相比之下，我们的方法在所有动作上都保持了稳定准确的动作捕获，显示出在处理二次运动方面的明显优势。

### 6.4 消融实验

| 生成器 | 角度误差 (度) | 位置误差 (cm) |
|---|---|---|
| SeMo-AE | **19.83 ± 6.79** | **10.58 ± 6.24** |
| cGAN | 25.06 ± 7.18 | 16.47 ± 7.24 |
| 无（None） | 24.18 ± 7.38 | 18.61 ± 6.53 |

**表 3｜SeMo-AE 与 cGAN 的对比。**

**定量结果。** 由于我们的宽松 IMU 数据合成本质上是一个条件生成任务（式 2，其中 $\mathrm{IMU}(t)$ 是条件），我们把 SeMo-AE 与条件生成对抗网络（cGAN）[32] 做了对比。为公平比较，我们用与 SeMo-AE 相同的数据训练 cGAN（以 $D_{Tight}^{sim}$ 为条件、$D_{Loose}^{sim}$ 为输出），并采用相同的隐噪声分布。如表 3 所示，cGAN 生成的宽松 IMU 数据相比"不使用合成数据"（"None"，即直接在 $D_{Loose}^{sim}$ 上训练）几乎没有提升，性能远逊于 SeMo-AE。

| 情形  | NLSL | TCS | 角度误差 (度)         | 位置误差 (cm)        |
| --- | ---- | --- | ---------------- | ---------------- |
| 1   | +    | +   | **19.83 ± 6.79** | **10.58 ± 6.24** |
| 2   | +    | −   | 21.46 ± 7.19     | 12.11 ± 7.23     |
| 3   | −    | +   | 21.54 ± 6.52     | 11.91 ± 6.33     |
| 4   | −    | −   | 21.71 ± 7.01     | 12.14 ± 6.99     |

**表 4｜SeMo-AE 中噪声引导隐空间学习（NLSL）与时间一致性方案（TCS）的消融。**

**定性结果。** 更细致地，我们在表 4 中展示了噪声引导隐空间学习与时间一致性方案的有效性。注意在情形 3 与 4 中，隐空间里可加高斯噪声的 $\mu$ 与 $\sigma$ 是通过整个数据集上 $E(\widetilde{\mathrm{IMU}}) - E(\mathrm{IMU})$ 的统计量获得的。结果表明这两项技术都是达到最佳性能所必需的。

**定性结果（图 5）。** 如图 5 所示：i) 去掉噪声引导隐空间学习（NLSL）会使合成的宽松 IMU 数据 $D_{Loose}^{gen}$ 出现异常的空间模式；ii) 去掉时间一致性方案（TCS）会把 $D_{Loose}^{gen}$ 变成类噪声信号，与 $D_{Loose}^{sim}$ 显著不同；iii) cGAN 生成的 $D_{Loose}^{gen}$ 多样性极低，表明它忽略了输入噪声、未能建模二次运动的效应。

### 6.5 实时演示

我们用 Python 与 Unity 实现了一个实时姿态估计可视化系统。用户像平常一样穿上衣物后，只需一次 T-Pose 标定（5 秒）即可启动系统。运行期间，系统持续接收实时 IMU 数据，用类似 TransPose [54] 的标定与归一化方法处理后送入姿态估计模型，并显示实时动作捕获结果。

通过实时演示可以观察到，我们的系统把宽松衣物的便利与舒适，同准确的动捕能力无缝结合起来。即使在快跑、跳跃等剧烈活动中也保持稳定，展示了其可靠性与广泛适用性。演示请见补充视频。

---

## 7. 局限性与未来工作

**局限性。**
*硬件方面*：受成本限制，我们目前只制作了一件衣物。虽然已与不同用户做了比较，但衣物尺码与面料材质对精度的影响仍有待探索。此外，集成在夹克中的电路与传感器未做防水处理，使该夹克无法像常规衣物那样正常洗涤。另外，由于夹克是宽松穿着的，手臂的扭转对 IMU 读数影响很小，难以准确测量该自由度上的旋转。
*软件方面*：SeMo-AE 虽显著增强了宽松 IMU 数据的丰富度，但由于其训练数据中模拟的穿着方式有限，生成的数据无法全面覆盖各种穿着方式。该局限导致姿态估计误差上升，在拉链拉开的穿着方式下尤为明显。

**未来工作。** 我们的工作探索了以宽松衣物作为动捕载体。这种与人们日常普通衣物的契合，意味着把用户舒适性置于准确性等因素之前。值得探索的是采集一个规模显著更大的数据库，用于大规模、连续（24×7）的人体运动采集（预计超过 100 名参与者）。还需要更多工作去研究在不同体型与衣物类型变化下的人体运动模式。这可能支撑起面向人群层面的长期健康监测等未来应用。

---

## 8. 结论

本文提出 Loose Inertial Poser（LIP）——一个仅依靠宽松衣物上的稀疏惯性传感器即可实现实时、准确姿态估计的新网络。我们的关键创新是二次运动自编码器（SeMo-AE），它能够从有限的仿真数据中合成出表现出多样二次运动效应的逼真 IMU 数据。SeMo-AE 采用了两项新技术：i）噪声引导隐空间学习，将二次运动建模为隐空间中的可加高斯噪声；ii）时间一致性建模，刻画二次运动随时间的平滑性。我们通过在 SeMo-AE 仿真的 IMU 数据上训练姿态估计网络来验证 SeMo-AE 的有效性。大量实验表明，我们的方法能有效适应不同体型与运动，显著优于 SOTA，平均关节旋转误差低于 20 度。

---

## 参考文献（按原序）

[1] Y. Bao, X. Zhao, D. Qian. FusePose: IMU-vision sensor fusion in kinematic space for parametric human pose estimation. IEEE TMM, 2022.
[2] A. Chatzitofis, D. Zarpalas, P. Daras, S. Kollias. DemoCap: Low-cost marker-based motion capture. IJCV, 129(12):3338–3366, 2021.
[3] X. Chen, X. Jiang, J. Fang, S. Guo, J. Lin, M. Liao, G. Luo, H. Fu. DispAD: Flexible on-body displacement of fabric sensors for robust joint-motion tracking. ACM IMWUT, 7(1):1–27, 2023.
[4] Y. Du, R. Kips, A. Pumarola, S. Starke, A. Thabet, S. Sanakoyeu. Avatars grow legs: Generating smooth human motion from sparse tracking inputs with diffusion model. CVPR, 2023.
[5] P. Eichelberger et al. Analysis of accuracy in optical motion capture. Journal of Biomechanics, 49(10):2085–2088, 2016.
[6] M. A. Fadhil, W. K. Shareef. Human activity tracking using wearable sensors in loose-fitting clothes: survey. TELKOMNIKA, 21(6):1382–1390, 2023.
[7] A. Gilbert et al. Fusing visual and inertial sensors with semantics for 3d human pose estimation. IJCV, 127:381–397, 2019.
[8] S. Gleadhill, D. James, J. Lee. Validating temporal motion kinematics from clothing attached inertial sensors. MDPI, 2018.
[9] G. Guerra-Filho. Optical motion capture: Theory and implementation. RITA, 12(2):61–90, 2005.
[10] L. Herda et al. Skeleton-based motion capture for robust reconstruction of human motion. Computer Animation, 2000.
[11] S. Z. Homayounfar, P. L. Andrew. Wearable sensors for monitoring human motion: a review. SLAS Technology, 25(1):9–24, 2020.
[12] S. Hu, M. Dai, T. Dong, T. Liu. A textile sensor for long durations of human motion capture. Sensors, 19(10):2369, 2019.
[13] Y. Huang, M. Kaufmann, E. Aksan, M. J. Black, O. Hilliges, G. Pons-Moll. Deep inertial poser: Learning to reconstruct human pose from sparse inertial measurements in real time. ACM TOG, 37(6):1–15, 2018.
[14] U. Jayasinghe, W. S. Harwin, F. Hwang. Comparing clothing-mounted sensors with wearable sensors for movement analysis and activity classification. Sensors, 20(1):82, 2019.
[15] J. Jiang et al. AvatarPoser: Articulated full-body pose tracking from sparse motion sensing. ECCV, 2022.
[16] Y. Jiang et al. Transformer inertial poser: Real-time human motion reconstruction from sparse IMUs with simultaneous terrain generation. SIGGRAPH Asia, 2022.
[17] W. Kehl et al. Deep learning of local RGB-D patches for 3D object detection and 6D pose estimation. ECCV, 2016.
[18] D. P. Kingma, J. Ba. Adam: A method for stochastic optimization. arXiv:1412.6980, 2014.
[19] D. P. Kingma, M. Welling. Auto-encoding variational Bayes. arXiv:1312.6114, 2013.
[20] M. Kocabas et al. PARE: Part attention regressor for 3D human body estimation. ICCV, 2021.
[21] M. Kok, J. E. Hol, T. B. Schön. An optimization-based approach to human body motion capture using inertial sensors. IFAC, 47(3):79–85, 2014.
[22] K. Kurihara et al. Optical motion capture system with pan-tilt camera tracking and real time data processing. ICRA, 2002.
[23] W. Li et al. MHFormer: Multi-hypothesis transformer for 3D human pose estimation. CVPR, 2022.
[24] Z. Liang et al. Smart garment: A long-term feasible, whole-body textile pressure sensing system. IEEE Sensors Journal, 2023.
[25] Q. Lin et al. Subject-adaptive loose-fitting smart garment platform for human activity recognition. ACM TSN, 19(4):1–23, 2023.
[26] R. Liu et al. Reconstructing human joint motion with computational fabrics. ACM IMWUT, 3(1):1–26, 2019.
[27] M. Long, Y. Cao, J. Wang, M. Jordan. Learning transferable features with deep adaptation networks. ICML, 2015.
[28] M. Lorenz et al. Towards artefact aware human motion capture using inertial sensors integrated into loose clothing. ICRA, 2022.
[29] T. McGrath, L. Stirling. Body-worn IMU human skeletal pose estimation using a factor graph-based optimization framework. Sensors, 20(23):6887, 2020.
[30] M. Menolotto et al. Motion capture technology in industrial applications: A systematic review. Sensors, 20(19):5687, 2020.
[31] B. Michael, M. Howard. Activity recognition with wearable sensors on loose clothing. PLoS ONE, 12(10):e0184642, 2017.
[32] M. Mirza, S. Osindero. Conditional generative adversarial nets. arXiv:1411.1784, 2014.
[33] V. Mollyn et al. IMUPoser: Full-body pose estimation using IMUs in phones, watches, and earbuds. CHI, 2023.
[34] M. Moniruzzaman et al. Wearable motion capture: Reconstructing and predicting 3D human poses from wearable sensors. IEEE JBHI, 2023.
[35] Noitom. Perception Neuron, 2017.
[36] S. Pan et al. Fusing monocular images and sparse IMU signals for real-time human motion capture. arXiv:2309.00310, 2023.
[37] C. Patel, Z. Liao, G. Pons-Moll. TailorNet: Predicting clothing in 3D as a function of human pose, shape and garment style. CVPR, 2020.
[38] M. Paulich et al. Xsens MTw Awinda: Miniature wireless inertial-magnetic motion tracker. Xsens, 2018.
[39] Natural Point. OptiTrack. 2011.
[40] J. L. Ponton, H. Yun, A. Aristidou, C. Andujar, N. Pelechano. SparsePoser: Real-time full-body motion reconstruction from sparse data. ACM TOG, 2023.
[41] M. Rahul. Review on motion capture technology. Global Journal of Computer Science and Technology, 18(1):26–30, 2018.
[42] A. J. Redhouse. Joint Angle Estimation Method for Wearable Human Motion Capture. PhD thesis, Virginia Tech, 2021.
[43] T. Shen, I. Di Giulio, M. Howard. A probabilistic model of human activity recognition with loose clothing. Sensors, 23(10):4669, 2023.
[44] Tesla Suit. TeslaSuit developer kit, 2020.
[45] K. Sun, B. Xiao, D. Liu, J. Wang. Deep high-resolution representation learning for human pose estimation. CVPR, 2019.
[46] T. von Marcard et al. Sparse inertial poser: Automatic 3D human pose estimation from sparse IMUs. Computer Graphics Forum, 2017.
[47] T. von Marcard et al. Recovering accurate 3D human pose in the wild using IMUs and a moving camera. ECCV, 2018.
[48] A. Winkler, J. Won, Y. Ye. QuestSim: Human motion tracking from sparse sensors with simulated avatars. SIGGRAPH Asia, 2022.
[49] S. Wu et al. Graph-based 3D multi-person pose estimation using multi-view images. ICCV, 2021.
[50] X. Xiao, S. Zarar. Machine learning for placement-insensitive inertial motion capture. ICRA, 2018.
[51] Y. Xu et al. ViTPose: Simple vision transformer baselines for human pose estimation. NeurIPS, 35:38571–38584, 2022.
[52] S. Yang, Z. Quan, M. Nie, W. Yang. TransPose: Keypoint localization via transformer. ICCV, 2021.
[53] H. Ye et al. Faster VoxelPose: Real-time 3D human pose estimation by orthographic projection. ECCV, 2022.
[54] X. Yi, Y. Zhou, F. Xu. TransPose: Real-time 3D human translation and pose estimation with six inertial sensors. ACM TOG, 40(4):1–13, 2021.
[55] X. Yi et al. Physical Inertial Poser (PIP): Physics-aware real-time human motion tracking from sparse inertial sensors. CVPR, 2022.
[56] T. Yu et al. Function4D: Real-time human volumetric capture from very sparse consumer RGBD sensors. CVPR, 2021.
[57] J. Zhang et al. Direct multi-view multi-person 3D pose estimation. NeurIPS, 34:13153–13164, 2021.
[58] Q. Zhao, C. Zheng, M. Liu, C. Chen. A single 2D pose with context is worth hundreds for 3D human pose estimation. arXiv:2311.03312, 2023.
[59] J. Zhen et al. SMAP: Single-shot multi-person absolute 3D pose estimation. ECCV, 2020.
[60] Z. Zheng et al. HybridFusion: Real-time performance capture using a single depth sensor and sparse IMUs. ECCV, 2018.
[61] B. Zhou et al. MocaPose: Motion capturing with textile-integrated capacitive sensors in loose-fitting smart garments. ACM IMWUT, 7(1):1–40, 2023.
[62] Y. Zhou, C. Barnes, J. Lu, J. Yang, H. Li. On the continuity of rotation representations in neural networks. CVPR, 2019.
[63] C. Zimmermann et al. 3D human pose estimation in RGBD images for robotic task learning. ICRA, 2016.
[64] C. Zuo, J. Fang, S. Guo, Y. Qin. Self-adaptive motion tracking against on-body displacement of flexible sensors. NeurIPS, 2023.

---

## 术语对照表

| 英文                             | 本文译法      | 备选译法 / 说明                 |
| ------------------------------ | --------- | ------------------------- |
| secondary motion               | **二次运动**  | 也可译"次级运动"，指衣物相对身体的滑移、惯性摆动 |
| loose-wear / tight-wear        | 宽松穿着 / 紧身 | tight-wear 亦作"紧身衣"        |
| sparse inertial motion capture | 稀疏惯性动作捕获  | 一般简称 SIP                  |
| on-body fixation               | 贴身固定      | —                         |
| pose estimation                | 姿态估计      | —                         |
| joint rotation error           | 关节旋转误差    | 对应角度误差指标                  |
| positional error               | 位置误差      | 单位 cm                     |
| pelvis                         | 骨盆        | —                         |
| latent space                   | 隐空间       | 亦作潜空间                     |
| reparameterization             | 重参数化      | VAE 经典技巧                  |
| batch normalization (BN)       | 批归一化      | —                         |
| Maximum Mean Discrepancy (MMD) | 最大均值差异    | —                         |
| temporal coherence             | 时间一致性     | 亦作时序一致性                   |
| jittering                      | 抖动        | —                         |
| extrapolation                  | 外推        | 指用 η 放大噪声                 |
| ad-hoc data                    | 即席数据      | 临时生成、按需产出的数据              |
| tailor                         | （服装）定制/仿真 | TailorNet 为衣物仿真模型         |
| drape                          | （衣物）垂坠    | —                         |

## 图表清单（原论文）

- **图 1**：LIP 通过装备 4 个 IMU 的宽松夹克实现实时上半身动捕。
- **图 2**：嵌入 IMU 的宽松夹克原型与数据采集电路板。
- **图 3**：LIP 总览。(a) SeMo-AE 的训练过程，以及如何由紧身 IMU 数据生成宽松 IMU 数据；(b) 姿态估计模型的训练与推理。
- **图 4**：在真实测试集 $D_{Loose}^{real}$ 上的定性结果。
- **图 5**：消融实验定性结果（对 $D_{Loose}^{sim}$、$D_{Tight}^{sim}$ 与三次随机采样的 $D_{Loose}^{gen}$ 做 PCA 可视化）。



