#### 基础操作
ssh 连接：ssh linaro@192.168.10.13
创建文件树：
文件编辑器： nano ~/workspace/ai_camera/src/main.py
查询温度： cat /sys/class/thermal/thermal_zone 0/temp
常见命令：cat sudo 
安装：更新和安装 python3 及依赖
==驱动摄像头==：
先写好 python 脚本，在脚本中写好各种操作（设置好参数，再在 while true  里面写流程和操作），写好接口，打开显示器
![[Pasted image 20260906135425.png|319]]


文件树：
可以直接在 `linaro` 用户的家目录下建立以下分层清晰的结构：

Plaintext

```
/home/linaro/                # 用户主工作区
├── workspace/               # 【项目源码区】所有自己编写的代码与工程
│   ├── ai_camera/           # 当前的 AI 相机工程
│   │   ├── src/             # Python 源代码 (main.py, camera.py, ui.py 等)
│   │   ├── filters/         # OpenCV / 传统图像算法脚本
│   │   ├── assets/          # 静态资源 (UI 图标、音效、测试图)
│   │   ├── scripts/         # 启动/停止/自启管理脚本
│   │   └── requirements.txt # Python 依赖清单
│   └── other_projects/      # 未来的其他开发项目
│
├── ai_hub/                  # 【AI 资产区】大体积、跨项目通用的模型与推理引擎
│   ├── models/              # 模型权重库 (统一集中存放，避免重复占用空间)
│   │   ├── llm/             # 语言模型 (如 qwen2.5-0.5b-instruct.gguf, rkllm 文件)
│   │   ├── rknn/            # 转换好的 RKNN 视觉风格模型 (.rknn)
│   │   └── clip/            # CLIP 相关特征提取模型
│   ├── runtimes/            # 编译好的底层推理引擎源码或二进制
│   │   ├── llama.cpp/       # llama.cpp 编译目录
│   │   └── rknn-toolkit2/   # 瑞芯微官方工具链
│   └── venvs/               # Python 独立虚拟环境 (隔离相机、大模型等不同依赖)
│       ├── env_camera/      # AI 相机专用环境 (OpenCV, RKNN-Lite2)
│       └── env_llm/         # 大模型/PyTorch 专用环境
│
├── services/                # 【容器与后台服务区】青龙面板、数据库、网络服务
│   ├── docker-compose.yml   # 统一编排多容器服务 (青龙、数据库等)
│   ├── qinglong/            # 青龙面板数据持久化挂载目录
│   │   ├── data/            # 脚本、依赖、日志
│   │   └── config/          # 配置文件
│   ├── databases/           # 数据库持久化目录
│   │   ├── mysql/           # 或 postgresql / sqlite 数据卷
│   │   └── redis/           # 缓存数据
│   └── clash/               # 或 mihomo 代理核心及配置
│
├── data/                    # 【业务数据/输出区】
│   ├── captures/            # AI 相机拍摄的原图与风格化成图
│   └── logs/                # 各类后台任务运行日志
│
└── bin/                     # 【个人快捷脚本区】(加入 PATH 环境变量)
    ├── set_proxy.sh         # 快速开启/关闭代理脚本
    └── check_npu.sh         # 查看 NPU 负载与状态脚本
```

### 这套布局的核心优势