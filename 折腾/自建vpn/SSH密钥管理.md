---
tags:
  - 科学上网
  - VPS
  - SSH
  - 密钥
---

# SSH 密钥管理 · 存放位置与备份

> 2026-09-21 整理。起因：重装电脑后一度**登不上 VPS**，因为旧备份不完整。
> ⚠️ 本笔记只记录**密钥的位置和指纹**，绝不放私钥内容本身。

---

## 一、VPS 的登录方式（重要）

**服务器现在只允许公钥登录，密码登录已关闭。**

```
PasswordAuthentication no           # /etc/ssh/sshd_config 及 sshd_config.d/50-cloud-init.conf
PermitRootLogin yes                 # 但密码关了，等于只能用 key
```

- 2026-08-26 关闭的，原因是**有人在爆破 SSH**（`sshd_config.d/50-cloud-init.conf.bak-20260826` 是改动前的备份，当时还是 `yes`）。
- 所以 `ssh root@95.182.91.188` 输入 root 密码是**连不上的**，会报 `Permission denied (publickey)`。这不是故障，是预期行为。

## 二、四把密钥

存放在 `~/.ssh/`，**完整镜像备份在金士顿 U 盘 `KINGSTON文件/备份/.ssh/`**。

| 文件 | 指纹 (SHA256) | 用途 | 有效性 |
|---|---|---|---|
| `id_ed25519` | `4n/GJrKWi13PoVB0GqimeUHd8ueqcELKoWNRbFoCA7c` | 本机默认身份（2026-09-10 重装后新生成） | 2026-09-21 已加入 VPS |
| `id_ed25519_vps` | `OVxS8WSERE6PgDpoBWN22hqONsJOsIS0Q2z41JebHfY` | **VPS `95.182.91.188` 登录** | ✅ 在用 |
| `id_ed25519_wuji` | `j5gk2cQXRIb9f1Z0L1l5XT3sI09/RtDxeRlrRMJTL90` | 旧机器 `wang@WUJI` 遗留 | 未知，可能已弃用 |
| `id_rsa_github` | `mOBLJNkDnSwl6Ftxgzw+XFQkZ4pkx2XOtA21zf55sW0` | GitHub（`hohokamk@github`） | GitHub |

## 三、怎么连

```bash
ssh vps                    # 已配好别名（~/.ssh/config），最省事
ssh -i ~/.ssh/id_ed25519_vps root@95.182.91.188   # 等价写法
```

## 四、这次踩的坑（教训）

- 重装电脑后翻出 `~/Documents/ssh/ssh-gitconfig/` 那份备份，结果**登不上**。
- 原因：那份备份是 **2026-07** 的，而 VPS 用的 key 是 **2026-08** 才生成的，**从来没进过那份备份**。两份 `known_hosts` 里都没有 `95.182.91.188` 的记录，等于从没连过。
- 最后是在**金士顿 U 盘** `KINGSTON文件/备份/.ssh/id_ed25519`（2026-08-24 备份）里找到的。
- **教训**：① 备份要定期做；② **备份完一定要实登验证一次**（`ssh -i <key> ...` 真连上去），别只看文件在不在；③ 密钥别只放一个地方。

## 五、加新 key 到 VPS 的方法

```bash
# 在服务器上（或本地用 ssh vps 进去）：
mkdir -p /root/.ssh && chmod 700 /root/.ssh
echo 'ssh-ed25519 AAAA...你的公钥... 备注' >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
# 注意：一定是 .pub 公钥，私钥永远不出本机
```

## 六、存放现状

| 位置 | 内容 | 说明 |
|---|---|---|
| `~/.ssh/` | 4 把私钥 + 公钥 + `config` + `keys.md` | **规范存放位置** |
| 金士顿 U 盘 `备份/.ssh/` | 上面这套的完整镜像 | exFAT 不支持权限位，U 盘要物理保管好 |
| `~/Documents/ssh/ssh-gitconfig/.ssh/` | 旧机器配置备份的遗留副本 | 已冗余（未删，可清理） |

> ⚠️ **私钥不要放进 Obsidian 库**（会被同步到云），也别放网盘。就放 `~/.ssh/` + U 盘。

---

## 相关笔记
- [[构建全流程]] — 主文档（节点搭建全过程）
- [[WARP分流配置]] — WARP 分流配置实录
- [[heihei]] — 服务器信息与面板登录账号速查
