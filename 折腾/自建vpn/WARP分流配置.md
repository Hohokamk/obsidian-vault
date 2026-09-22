---
tags:
  - 科学上网
  - VPS
  - 代理
  - Cloudflare
  - WARP
---

# WARP 出站分流配置 · 只把 Google 域名走 Cloudflare WARP

> 2026-09-21 配置并验证完成。上游背景见 [[构建全流程]]，账号速查见 [[heihei]]。
> **目的**：VPS 的 IP 被 Google 风控，把 Google 系域名的流量切到 Cloudflare WARP 出口，其余照旧走 VPS 原生 IP。

---

## 一、结论先行：问题从来不在 WARP

排查时发现两件事：

| 检查项 | 结果 |
|---|---|
| WARP 本身 | ✅ **一直是好的**。官方 `warp-cli`，WarpProxy 模式监听 `127.0.0.1:40000`，状态 Connected，出口 colo=SJC |
| 面板里的配置 | ❌ **根本没生效**。服务器上实际生成的 `config.json` 里只有 `direct` 和 `blocked` 两个出站，没有任何 WARP 出站和 Google 路由规则 |

**踩坑教训**：在 3X-UI 面板 UI 上改的 Xray 配置，和服务器**实际生效**的配置是两回事。以后遇到「面板里配了不生效」，第一步永远是看这个文件：

```bash
cat /usr/local/x-ui/bin/config.json        # 面板真正生成、Xray 真正在跑的配置
# 面板数据库里存的模板在 /etc/x-ui/x-ui.db 的 settings.xrayTemplateConfig
```

## 二、最终配置（已生效）

### 出站（outbounds 里新增一个）

```json
{
  "tag": "warp",
  "protocol": "socks",
  "settings": { "servers": [{ "address": "127.0.0.1", "port": 40000 }] }
}
```

### 路由规则（routing.rules 里，**插在 api 规则之后**，最先命中）

```json
{
  "type": "field",
  "domain": ["geosite:google"],
  "outboundTag": "warp"
}
```

`geosite:google` 是 Xray 内置的 Google 域名库（本机 `geosite.dat` 里共 **1073 条**），覆盖 `google.com`、`googleapis.com`、`gstatic.com`、`googlevideo.com`、`gvt1.com`、各国 `google.*`、以及 `youtube.com` / `youtu.be` / `ytimg.com`。不用自己列域名清单。

> 💡 顺带实测过：`geosite:` 的类别名**大小写不敏感**，`geosite:google` 和 `geosite:GOOGLE` 都能匹配（这个 dat 文件里存的其实是大写）。

## 三、怎么改的（下次要改时的操作路径）

面板 API 从服务器本机 curl 登录会被 **403**（3X-UI 3.x 加了同源校验），所以直接改数据库模板：

```bash
# 1. 先备份（重要）
cp /etc/x-ui/x-ui.db /root/warp-backup/x-ui.db.bak
cp /usr/local/x-ui/bin/config.json /root/warp-backup/config.json.before

# 2. 改数据库里 settings 表的 xrayTemplateConfig（JSON 文本）
#    —— 脚本留了一份：/root/warp-backup/apply-warp.py

# 3. 重启服务，让面板重新生成 config.json
systemctl restart x-ui      # 代理会中断约 10 秒

# 4. 确认生效
grep -n "geosite:google" -A2 -B3 /usr/local/x-ui/bin/config.json
```

本次改动前的完整备份在服务器 **`/root/warp-backup/`**（含模板、`config.json`、数据库），要回滚就用它们覆盖回去再重启。

## 四、验证方法（三种，从弱到强）

### 1. 看 WARP 本身通不通

```bash
warp-cli --accept-tos status
curl -s --socks5-hostname 127.0.0.1:40000 https://www.cloudflare.com/cdn-cgi/trace | grep -E "^(ip|warp|colo)="
# 期望: warp=on，IP 是 2a09:bac1::/32（Cloudflare 段）
```

### 2. 看路由决策（最直观）

```bash
# 用生效配置里的 outbounds/routing 另起一个只监听本机的临时实例，开 debug 日志
# 然后 curl，看日志里的 "taking detour"
grep -o "taking detour \[[a-z]*\] for \[[a-z]*:[^]]*\]" /tmp/gt/error.log | sort -u
# 期望: taking detour [warp] for [tcp:www.youtube.com:443]
#       taking detour [direct] for [tcp:www.cloudflare.com:443]
```

### 3. 真机端到端（最可信）

用**你实际在用的节点**从本地连上去实测，看 Google 和服务器分别看到的来源 IP：

| 访问目标 | 期望结果 |
|---|---|
| `dns.google`（Google 域名） | Google 看到 `2a09:bac1:...`（Cloudflare WARP 段） |
| `cloudflare.com`（非 Google） | 看到 `2a13:7c00:3:3:...`（VPS 自己的 IPv6） |

```bash
# 本地客户端配置要点（VLESS-WS-TLS 节点）
#   address = komod.dpdns.org    port = 443
#   network = ws                 path = /api-stream, Host = komod.dpdns.org
#   security = tls               serverName = komod.dpdns.org, alpn = http/1.1
#   UUID 从面板「入站列表 → 客户端」里取
#   起一个本地 socks 入站，然后：
curl -s --socks5-hostname 127.0.0.1:10809 \
  "https://dns.google/resolve?name=o-o.myaddr.l.google.com&type=TXT"
# 看返回里的 edns0-client-subnet，就是 Google 眼中你的来源 IP
```

2026-09-21 实测结果：Google 看到 `2a09:bac1:76c0:d00::/56`（WARP），非 Google 看到 `2a13:7c00:3:3:...`（VPS 直连）。

## 五、注意事项

### ⚠️ YouTube 也走 WARP 了

`geosite:google` 里包含 `youtube.com`、`googlevideo.com`、`ytimg.com`，所以**视频流量也走了 WARP**。如果发现 YouTube 变慢、或弹「请确认你不是机器人」（YouTube 对 WARP 的共享 IP 会拦），把它拎回直连 —— 在模板的 routing 里**在 google 规则之前**插一条：

```json
{ "type": "field", "domain": ["geosite:youtube"], "outboundTag": "direct" }
```

改完重启 Xray（面板里点重启，或 `systemctl restart x-ui`）。规则顺序 = 从前到后第一个命中生效。

### ⚠️ 别点面板里的「重置」

3X-UI 的 **Xray 设置 → 重置** 会把整个模板打回默认，这条 WARP 规则一起没。在面板里编辑配置时能直接看到它（找 `"outboundTag": "warp"`），保留着就行。

### ⚠️ 如果 Google 还是找麻烦

WARP 是**共享出口 IP**，本身也可能是脏的。如果切过去之后验证码照旧、账号登录仍被拦，那说明问题不在链路而在出口 IP 质量，得换思路（换 WARP 落地、或换别的出口），不是这套配置能解决的。

### 客户端不用改

分流做在**服务端**，客户端保持原样即可（路由模式照旧用「绕过局域网及大陆地址」）。注意客户端别把 Google 设成「直连」绕过代理，否则根本到不了 VPS。

---

## 相关笔记
- [[构建全流程]] — 主文档（节点搭建全过程）
- [[heihei]] — 服务器信息与面板登录账号速查
- [[服务器设置]] — 基础设置步骤（SSH / BBR / Swap）
- [[流程]] — 前期通用教程（第五节是 WARP 的旧方案，已被本文取代）
