# ysp-live v8.1

> **致谢**
> 1. 感谢 [IPTV 总部](http://t.me/iptvorganization)分享的算法源码
> 2. 感谢 Gary's Club 群里小伙伴 ll 提供大量频道的 live_id
> 3. 感谢 APTV 群主提供的技术帮助

**English README**: [README.md](README.md)

央视频直播 Docker 部署版——**仅含央视系频道**（30 路）：CCTV-1~17、5+、6、三个剧场、4K/8K、CGTN。地方卫视等非央视系频道已彻底移除。

## 包含内容

- **30 路央视频道**，带分组（`group-title`）：央视FHD / 央视UHD / CGTN
- **双引擎四层兜底**：设备投屏真 4K/8K → 1080p JCE → bkliveinfo → Node.js WASM 兜底
- **7 天回看与时移**：19 路频道支持 7 天节目回看（`catchup="append"`）
- 纯 Python + Node.js，单端口（8767）
- 后台自动保活：每 30 秒心跳、静默续期 Session、24/7 保活
- 设备身份持久化：`./data` 数据卷，容器重建不丢注册
- APTV 播放器优化：关闭预览/测速，避免触发风控限流

## VPS 一键部署

```bash
curl -sSL https://raw.githubusercontent.com/waastudios/ysptp-docker/main/install.sh|bash
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

- 央视订阅（30 路，带分组）：
  ```
  http://<VPS公网IP>:8767/cctv.m3u
  ```
- 聚合 EPG（30 路，6 小时刷新）：
  ```
  http://<VPS公网IP>:8767/epg.xml
  ```
- 首页：`http://<VPS公网IP>:8767/`
- 诊断：`http://<VPS公网IP>:8767/diag`

> 注意：`localhost` 只能本机用。VPS 上必须换成公网 IP；局域网用内网 IP（如 `http://192.168.1.10:8767/cctv.m3u`）。

订阅分组：
- 央视FHD：CCTV-1~17、5+、6、三个剧场等
- 央视UHD：CCTV-4K、8K、16-4K
- CGTN：CGTN 主频道及法/俄/阿/西/纪录

## 端口与防火墙

| 端口 | 用途 |
| --- | --- |
| 8767 | 单端口：首页、订阅、30 路频道、TS 中继、聚合 EPG |

```bash
ufw allow 8767/tcp
```

## EPG 节目单订阅

本项目自带聚合 EPG 接口（地址见上文使用一节），开箱即用，不用再手动填第三方 EPG 源：

- 内容：只包含本项目 30 路频道的节目单（央视FHD/央视UHD/CGTN），无用频道已过滤
- 数据源：自动合并以下两个上游 EPG（两源互补，单个源挂了不影响）：
  - `https://live.fanmingming.com/e.xml`
  - `https://epg.112114.xyz/pp.xml.gz`
- 刷新：每 6 小时自动更新；首次访问时后台拉取，稍等片刻再刷新即可

`/cctv.m3u` 订阅已默认指向该地址，播放器会自动加载节目单。

## 注意

- **带宽**：看 4K 时 VPS 会中继视频流量（约 15GB/小时，按 35Mbps 算）。离央视 CDN 远的 VPS（如美国）看 4K 可能卡顿，推荐用亚洲 VPS。
- **设备注册**：首次启动约 5~10 秒完成设备注册；容器删了重建后需重新注册（正常）。
- 订阅自带台标、`tvg-id`、分组和聚合 EPG，不用手动填 EPG 源。

## 常用命令

```bash
docker compose up -d --build   # 启动 / 更新
docker logs -f ysp-live        # 看日志
docker compose restart         # 重启
docker compose down            # 停止
```

## 更新日志

### v9.0 (2026-10-07)
- 上游：双设备热备池（0ms 切换）、400 智能自愈重试
- 默认 26 路走设备协议原生高码流
- 本定制版：30 路（仅 CCTV/CGTN），分组 央视FHD/央视UHD/CGTN
- 内置 EPG 聚合（`/epg.xml`），4K 频道锁死真 4K

### v8.1
- 双引擎：Python 主网关 + Node.js WASM 兜底，四层故障切换
- 30 路频道，EPG 聚合

## 卸载

```bash
cd /opt/ysp-live-docker && docker compose down -v
docker rmi ysp-live:v8.1
cd /opt && rm -rf /opt/ysp-live-docker /opt/v8.1.zip
```
`docker compose down -v` 会连设备注册数据一起删除。
