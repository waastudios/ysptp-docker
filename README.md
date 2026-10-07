# ysp-live v9.0

> **Acknowledgments**
> 1. Thanks to [IPTV Official Group](http://t.me/iptvorganization) for sharing the algorithm source code
> 2. Thanks to ll from the Gary's Club group for providing live_ids for many channels
> 3. Thanks to the APTV group owner for technical help

**中文文档**: [README-CN.md](README-CN.md)

CCTV live streaming via Docker — **CCTV channels only** (30 channels): CCTV-1~17, 5+, 6, 3 theater channels, 4K/8K, CGTN. Local satellite channels have been completely removed.

## What's inside

- **30 CCTV channels** with groups (`group-title`): 央视FHD / 央视UHD / CGTN
- **Dual-engine 4-layer fallback**: device 4K/8K → 1080p JCE → bkliveinfo → Node.js WASM fallback
- **7-day catchup & timeshift**: 19 channels support 7-day program replay (`catchup="append"`)
- Python + Node.js, single port (8767)
- Auto keep-alive: heartbeat every 30s, silent session renewal, 24/7 background worker
- Persistent device identity: `./data` volume survives container rebuilds
- APTV player optimized: no preview/latency probing to avoid triggering rate limits

## One-command VPS deploy

```bash
curl -sSL https://raw.githubusercontent.com/waastudios/ysptp-docker/main/install.sh|bash
```

Wait ~30s, then check logs for `设备协议就绪` (device protocol ready):

```bash
docker logs -f ysp-live
```

## Usage

Get your VPS public IP:

```bash
curl -s ifconfig.me
```

- CCTV subscription (30 channels, with groups):
  ```
  http://<VPS_PUBLIC_IP>:8767/cctv.m3u
  ```
- Aggregated EPG (30 channels, refreshes every 6h):
  ```
  http://<VPS_PUBLIC_IP>:8767/epg.xml
  ```
- Homepage: `http://<VPS_PUBLIC_IP>:8767/`
- Diagnostics: `http://<VPS_PUBLIC_IP>:8767/diag`

> Note: `localhost` only works on the machine itself. On a VPS, always replace it with the public IP; on a LAN use the private IP (e.g. `http://192.168.1.10:8767/cctv.m3u`).

Channel groups:
- 央视FHD: CCTV-1~17, 5+, 6, 3 theater channels, etc.
- 央视UHD: CCTV-4K, 8K, 16-4K
- CGTN: CGTN main + French / Russian / Arabic / Spanish / Documentary

## Ports & firewall

| Port | Purpose |
| --- | --- |
| 8767 | Single port: homepage, subscriptions, 30 channels, TS relay, aggregated EPG |

```bash
ufw allow 8767/tcp
```

## EPG Guide Subscription

This project ships a built-in aggregated EPG endpoint (see Usage above for the URL) — no need to configure third-party EPG sources manually:

- Content: programme guide for only the 30 channels in this project (CCTV FHD / CCTV UHD / CGTN); irrelevant channels are filtered out
- Upstream sources (merged automatically; the two complement each other, one going down won't break the other):
  - `https://live.fanmingming.com/e.xml`
  - `https://epg.112114.xyz/pp.xml.gz`
- Refresh: auto-updates every 6 hours; fetched in the background on first access, just retry after a moment

The `/cctv.m3u` playlist already points to this address, so players load the guide automatically.

## Notes

- **Bandwidth**: 4K channels relay video through the VPS (~15GB/hour at 35Mbps). A VPS far from CCTV's CDN (e.g. US) may stutter on 4K; an Asia VPS is recommended for smooth 4K.
- **Device registration**: first boot takes ~5-10s for device registration; rebuilding the container requires re-registration (normal).
- Subscriptions include logos, `tvg-id`, `group-title`, and aggregated EPG — no manual EPG setup needed.

## Common commands

```bash
docker compose up -d --build   # start / update
docker logs -f ysp-live        # logs
docker compose restart         # restart
docker compose down            # stop
```

## Changelog

### v9.0 (2026-10-07)
- Upstream: dual-device hot-standby pool (0ms failover), 400 self-healing retry
- 26 channels via device protocol native high-bitrate by default
- This build: 30 channels (CCTV/CGTN only), groups 央视FHD/央视UHD/CGTN
- Built-in EPG aggregation (`/epg.xml`), 4K channels locked to true 4K

### v8.1
- Dual engine: Python gateway + Node.js WASM fallback, 4-layer failover
- 30 channels, EPG aggregation

## Uninstall

```bash
cd /opt/ysp-live-docker && docker compose down -v
docker rmi ysp-live:v9.0
cd /opt && rm -rf /opt/ysp-live-docker /opt/v9.0.zip
```
`docker compose down -v` also removes the device registration data.
