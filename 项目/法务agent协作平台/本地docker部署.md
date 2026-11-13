**服务已启动**

- Web：[http://127.0.0.1:5173](http://127.0.0.1:5173)
- API：`127.0.0.1:3310`，健康检查 `UP`
- Worker：运行中
- PostgreSQL：运行中
- 登录账号：执行 `Get-Content .local\demo-credentials.json` 查看

## 正确的本地启动顺序

```bash
# 终端 1：首次或 Docker 容器停了之后必须跑
cd D:\03_Projects\LegalAgent
npm run dev:setup
npm run dev

# 终端 2
cd D:\03_Projects\LegalAgent
npm run worker

# 终端 3
cd D:\03_Projects\LegalAgent
npm run dev --workspace @legalagent/web
```

登录账号：

```bash

cat .local/demo-credentials.json
```


## 简要分析

本笔记原先记录在 WSL 中重新克隆并启动 LegalAgent 的旧流程。该流程会生成第二份项目副本，现已废弃；当前只维护 Windows 目录 `D:\03_Projects\LegalAgent`，Docker 和 Node.js 服务优先从 Windows 启动。

## 固定路径

```powershell
Set-Location 'D:\03_Projects\LegalAgent'
```

当前本地链路固定为：

- Windows 项目目录：`D:\03_Projects\LegalAgent`
- Windows API：`http://127.0.0.1:3310`
- Windows Web：`http://127.0.0.1:5173`
- Windows Docker PostgreSQL：`127.0.0.1:32768`
- 开发凭据：`D:\03_Projects\LegalAgent\.local\demo-credentials.json`

## 禁止事项

- 不要在 WSL 的 `~/projects/LegalAgent` 重新克隆项目。
- 不要同时启动 WSL 和 Windows 两套 PostgreSQL。
- 不要混用两个目录中的 `.env.local`、Docker volume 或开发凭据。

如果必须在 WSL 中运行 Linux 命令，使用：

```bash
cd /mnt/d/03_Projects/LegalAgent
```

这样 WSL 读写的是同一份 Windows 工作树，不会产生第二个 Git 仓库。
