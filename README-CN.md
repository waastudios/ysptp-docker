# ysp-live v6.2

> **致谢**
> 1. 感谢 IPTV 总部分享的算法源码
> 2. 感谢 Gary's Club 群里小伙伴 ll 提供大量频道的 live_id
> 3. 感谢 APTV 群主提供的技术帮助

**English README**: [README.md](README.md)

央视频直播 Docker 部署版——**仅含央视系频道**（30 路）：CCTV-1~17、5+、6、三个剧场、4K/8K、CGTN。地方卫视等非央视系频道已彻底移除。

## 包含内容

- **30 路央视频道**，带分组（`group-title`）：央视FHD / 央视UHD / CGTN
- **真 4K 频道**：CCTV-4K、CCTV-8K、CCTV-16 4K（设备协议）
- 纯 Python，零依赖，单端口（8767）
- 后台自动保活：每 30 秒心跳、静默续期 Session、24/7 保活

## VPS 一键部署

```bash
cd /opt && curl -sSL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36" -o v6.2.zip "https://github.com/waastudios/ysptp-rs/releases/download/v6.2/ysp-live-docker-v6.2.zip" && python3 -c "import zipfile; zipfile.ZipFile('v6.2.zip').extractall('/opt/ysp-live-docker')" && cd /opt/ysp-live-docker && docker compose up -d --build
```

等约 30 秒，看日志出现 `设备协议就绪`：

```bash
docker logs -f ysp-live
```

## 使用

获取 VPS 公网 IP：

```bash
curl -s ifconfig.me
```

- 聚合订阅（30 路央视）：`http://<VPS公网IP>:8767/all.m3u`
- 央视订阅（同上，带分组）：`http://<VPS公网IP>:8767/cctv.m3u`
- 首页：`http://<VPS公网IP>:8767/`
- 诊断：`http://<VPS公网IP>:8767/diag`

> 注意：`localhost` 只能本机用。VPS 上必须换成公网 IP；局域网用内网 IP（如 `http://192.168.1.10:8767/all.m3u`）。

订阅分组：
- 央视FHD：CCTV-1~17、5+、6、三个剧场等
- 央视UHD：CCTV-4K、8K、16-4K
- CGTN：CGTN 主频道及法/俄/阿/西/纪录

## 端口与防火墙

| 端口 | 用途 |
| --- | --- |
| 8767 | 单端口：首页、订阅、30 路频道、TS 中继 |

```bash
ufw allow 8767/tcp
```

## 注意

- **带宽**：看 4K 时 VPS 会中继视频流量（约 15GB/小时，按 35Mbps 算）。离央视 CDN 远的 VPS（如美国）看 4K 可能卡顿，推荐用亚洲 VPS。
- **设备注册**：首次启动约 5~10 秒完成设备注册；容器删了重建后需重新注册（正常）。
- 订阅自带台标、`tvg-id`、分组和 EPG，不用手动填 EPG 源。

## 常用命令

```bash
docker compose up -d --build   # 启动 / 更新
docker logs -f ysp-live        # 看日志
docker compose restart         # 重启
docker compose down            # 停止
```
