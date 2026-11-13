# Phase 2 · 风格路由接入记录

日期：2026-09-08

## 现在做到哪里了

- Phase 1 已经完成并提交：板子能打开 USB 摄像头、实时预览、切换 7 个 OpenCV 滤镜、3 秒快门倒计时保存照片。
- Phase 2 已经把本地 Qwen2.5-0.5B 接到主流程里：你输入一句中文风格描述，程序会把它变成一个固定标签，再切到对应滤镜。

## 现在能做什么

1. 关键词风格：梵高星空 -> VAN_GOGH、浮世绘 -> UKIYOE、赛博朋克 -> CYBERPUNK、素描 -> SKETCH、动漫 -> ANIME，基本 0 秒命中。
2. 冷门句子：没有关键词时走板子上的 Qwen 模型，大约 4 秒返回一个合法标签。
3. 主控集成：启动时可以用 `--prompt` 直接指定风格；也可以在 SSH 终端里输入中文，按快门时自动应用。

## 怎么使用

### 电脑端部署

代码源头在电脑目录 `D:\03_Projects\Stylized_Camera`。

```powershell
# 上传代码，只跑滤镜测试，不占用 HDMI 屏幕
.\deploy.ps1 -SkipSmoke

# 上传代码 + 跑 10 秒整机冒烟测试
.\deploy.ps1
```

脚本会把 `main.py`、`camera/`、`filters/`、`router/`、`tools/` 推到开发板。

### 板子端运行

```bash
ssh linaro@192.168.10.13

# 路由单测
cd /home/linaro/workspace/stylized_camera
PYTHONPATH=. python3 tools/test_router.py

# 相机短测，指定风格
export DISPLAY=:0
export XAUTHORITY=/home/linaro/.Xauthority
python3 main.py --prompt "梵高星空"
```

主控按键：

- `0 ~ 6`：切换滤镜。
- `S` 或空格：快门倒计时并保存照片。
- `F`：全屏切换。
- `Q` 或 Esc：退出。

## 怎么判断通没通过

跑路由单测时，输出应该接近下面这样：

```text
VAN_GOGH     0.000s  我想拍出梵高星空一样的感觉
UKIYOE       0.000s  来一张浮世绘风格的画面
CYBERPUNK    0.000s  赛博朋克霓虹雨夜
SKETCH       0.000s  变成铅笔素描
ANIME        0.000s  二次元动漫风
```

跑相机冒烟测试时，日志里应该出现：

```text
[router] 梵高星空 -> VAN_GOGH -> oil
```

看到这两条，就说明 Phase 2 的路由已经接进主流程了。

## 这次的关键设计

- 为什么加关键词：0.5B 模型自由生成时，容易把所有句子都压到列表第一个标签，所以先用关键词快速兜底。
- 为什么加 GBNF 语法：强制模型只能从六个标签里选一个，不能乱写。
- 为什么用 `llama-completion -st`：`llama-cli` 是交互式程序，Python 的 `subprocess` 调它会一直卡住，所以改用单轮生成参数。

## 下一步

- 把现在用来占位的 OpenCV 滤镜，换成真正的 Fast Neural Style Transfer 或 CycleGAN 风格网络。
- 这一步需要 RKNN 工具链；目前板子还没有 `/dev/rknpu`，之后还要装供应商的 SDK。
