# ysp-live v6.0

> **致谢**
> 1. 感谢 IPTV 总部分享的算法源码
> 2. 感谢 Gary's Club 群里小伙伴 ll 提供大量频道的 live_id
> 3. 感谢 APTV 群主提供的技术帮助

央视频全频道直播（64 路，含 26 路真 4K / 高码率），纯 Python 单文件，单端口，一条命令在 VPS 上跑起来。

**中文文档**: [README-CN.md](README-CN.md)

## 这是什么

- **64 路直播**：央视 21 + CGTN 6 + 剧场 3 + 卫视 32 + CETV-1 + 国学。纯 Python 标准库，零二进制、零依赖。
- **26 路真 4K / 高码率**：CCTV-1/2/3/4/5/5+/7/8/9/10/11/12/13/14/15/16/17、CCTV-4K/8K/16-4K（真 4K 3840×2160）、CGTN 主频道/法语/俄语/阿拉伯语/西班牙语/纪录，走设备协议；未就绪时自动回落 1080p。
- **单端口架构**：全部服务都在 8767 一个端口，不用再映射 8766。
- 设备身份永久固化，后台自动保活续期；订阅自带台标、`tvg-id` 和 EPG 地址，播放器导入后节目单自动匹配。

## VPS 一键部署

```bash
curl -sSL -O https://github.com/waastudios/ysptp-rs/releases/download/v6.0/ysp-live-v6.0.zip && python3 -c "import zipfile; zipfile.ZipFile('ysp-live-v6.0.zip').extractall('ysp-live-v6')" && cd ysp-live-v6 && sudo ./deploy.sh
```

`deploy.sh` 会：检查/安装 Python3 → 装到 `/opt/ysp-live` → 注册 systemd 服务并开机自启 → 输出订阅地址。

设备协议首次注册约 5~10 秒，看日志确认：

```bash
journalctl -u ysp-live -f
```

看到 `设备协议就绪` 就是 26 路高码率/真 4K 好了。

## 实测结论（机房 VPS 可用）

- **不需要家庭宽带**。已在美国机房 VPS 实测：设备协议注册一次成功。旧文档里"机房网络会被央视拒绝"的说法已过时。
- 注册信息保存在 `/opt/ysp-live/device-state-rs.json`，**不要删除**，避免触发央视 695 拦截。

## 端口与防火墙

只需要放行 **8767/TCP** 一个端口：

```bash
# ufw 示例
ufw allow 8767/tcp
```

## 使用

查 VPS 公网 IP：

```bash
curl -s ifconfig.me
```

- 聚合订阅（64 路一次导入，推荐）：`http://<VPS公网IP>:8767/all.m3u`
- 首页：`http://<VPS公网IP>:8767/`
- 诊断页：`http://<VPS公网IP>:8767/diag`（每路状态、Session 有效性、设备 GUID）

> 新手注意：`localhost` 只在本机有效。在 VPS 上跑、手机/电视上看时，必须换成 VPS 公网 IP；局域网用内网 IP（如 `http://192.168.1.10:8767/all.m3u`）。

## 常用命令

```bash
sudo systemctl restart ysp-live   # 重启
sudo systemctl stop ysp-live      # 停止
journalctl -u ysp-live -f         # 看日志
```

不想跑设备协议（只要 1080p）：`python3 ysp-live.py --no-4k`

## 排错

- **设备协议一直没就绪**：看 `http://<VPS公网IP>:8767/diag`，再看 `journalctl -u ysp-live`。
- **端口被占用**：`ss -tlnp | grep 8767` 找出占用进程并处理。
- **Windows / Mac 本地跑**：`python3 ysp-live.py`（Windows 用 `py ysp-live.py`），然后浏览器打开 `http://localhost:8767/`。
