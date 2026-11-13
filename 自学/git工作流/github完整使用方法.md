我们从头梳理一遍。假设你要参与 LegalAgent 的开源项目开发，采用 Fork + 本地开发分支 + Pull Request 的协作方式。

我把整个过程分成 6 个阶段，你可以跟着终端一步一步操作。

## 一、GitHub 网页端：Fork 原作者仓库

假设原作者的仓库是：

```
https://github.com/author/LegalAgent
```

1. 打开原作者的 GitHub 仓库。
    
2. 点击右上角 `Fork`。
    
3. 点击 `Create fork`。
    

完成后，你就有了自己的仓库：

```
原作者：author/LegalAgent
你自己：wgqq/LegalAgent
```

Fork 相当于在 GitHub 上创建了一份与你关联的项目副本。

## 二、本地配置：设置远程仓库

进入你本地的项目目录：

```powershell
Set-Location 'D:\03_Projects\LegalAgent'
```

先查看现有远程仓库：

```
git remote -v
```

假设你最初是直接从原作者仓库 Clone 的，那么通常会看到：

```
origin  https://github.com/author/LegalAgent.git
```

现在我们要调整它。

第一步：把 origin 改成自己的仓库

```
git remote set-url origin https://github.com/wgqq/LegalAgent.git
```

第二步：添加原作者仓库，命名为 upstream

```
git remote add upstream https://github.com/author/LegalAgent.git
```

第三步：检查配置

```
git remote -v
```

最终应该是：

```
origin    https://github.com/wgqq/LegalAgent.git (fetch)
origin    https://github.com/wgqq/LegalAgent.git (push)

upstream  https://github.com/author/LegalAgent.git (fetch)
upstream  https://github.com/author/LegalAgent.git (push)
```

## 三、理解本地和远程分支

现在你的项目有三个概念：

远程仓库

origin：你的 GitHub 仓库

wgqq/LegalAgent

远程仓库

upstream：原作者的 GitHub 仓库

author/LegalAgent

本地分支

main

用于保持稳定代码，与原作者同步

开发分支

feature/login

用于开发登录功能

注意：`origin/main` 和 `upstream/main` 是本地记录的远程分支状态，不是远程仓库本身的分支。

## 四、正式开始功能开发

假设你要开发一个登录功能。

1. 获取原作者最新代码

```
git fetch upstream
```

2. 切换到 main

```
git switch main
```

3. 合并原作者的最新代码

```
git merge upstream/main
```

4. 将同步后的 main 推送到自己的仓库

```
git push origin main
```

5. 创建功能开发分支

```
git switch -c feature/login
```

这条命令相当于：

- 创建一个名为 `feature/login` 的分支。
    
- 自动切换到这个分支。
    

## 五、开发完成后提交代码

假设你修改了登录模块。

1. 查看修改情况

```
git status
```

2. 将修改添加到暂存区

```
git add .
```

3. 提交本地修改

```
git commit -m "feat: implement login feature"
```

4. 推送到自己的 GitHub

```
git push -u origin feature/login
```

这里的 `-u` 是建立本地分支与远程分支的跟踪关系。

以后再次推送，只需要：

```
git push
```

## 六、提交 Pull Request

打开 GitHub 上自己的 Fork 仓库，创建 Pull Request。

目标关系应该是：

|项目|选择|
|---|---|
|base repository|原作者的仓库|
|base branch|main|
|head repository|你的 Fork|
|compare branch|feature/login|

这样你就把自己的功能提交给原作者审核了。

## 最后：完整命令速查表

以后你可以把下面这些命令作为日常开发流程。

|操作|命令|
|---|---|
|查看远程仓库| `git remote -v` |
|修改 origin| `git remote set-url origin URL` |
|添加 upstream| `git remote add upstream URL` |
|获取原作者更新| `git fetch upstream` |
|切换 main| `git switch main` |
|同步原作者 main| `git merge upstream/main` |
|创建功能分支| `git switch -c feature/xxx` |
|查看当前分支| `git branch` |
|添加修改| `git add .` |
|提交修改| `git commit -m "说明"` |
|推送功能分支| `git push -u origin feature/xxx` |

我建议你现在先不要急着开发功能。

先在 LegalAgent 项目目录执行：

```
git remote -v
git branch -vv
```

把输出发给我，我帮你检查当前仓库的绑定关系和分支状态，然后我们再一步一步配置，避免误操作覆盖代码。
