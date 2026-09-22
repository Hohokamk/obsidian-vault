终端连接我的 linux：
ssh 连接： `ssh vps`（别名）　或　`ssh -i ~/.ssh/id_ed25519_vps root@95.182.91.188`
（⚠️ 2026-08-26 起因挡 SSH 爆破已关闭密码登录，只认公钥；密钥见 [[SSH密钥管理]]）
sysctl net.ipv 4.tcp_congestion_control
系统 debian 12
CPU：单核
内存：1 GB+2 GB 虚拟内存
存储：10 GB
流量：500 GB
控制指令栏：x-ui

3 x-ui 登录：
地址：http://95.182.91.188:55321/VDEBv14LayHvhV6yyT/panel/
用户名：QUNQUN
密码：1 q 22 q 11 q 2

1. BBR 加速
2. swap 配置虚拟内存
3. 安装 3 x-ui 控制台
4. 添加 velss-reality 节点
5. 添加客户端配置
6. 添加 cloudflare 反代
7. cloudflare 证书申请 tls 加密
8. 优选 ip(待定) ,xhttp 迁移
9. ✅ warp 反代 —— **2026-09-21 完成**，官方 `warp-cli` + `geosite:google` 分流，见 [[WARP分流配置]]

![[Pasted image 20260824170658.png]]






配置节点：![[Pasted image 20260824133808.png]] ![[Pasted image 20260824230424.png]] ![[Pasted image 20260825092816.png]] ![[Pasted image 20260826105635.png]] ![[Pasted image 20260826111715.png]] ![[Pasted image 20260826111743.png]]