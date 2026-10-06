# ysp-live v7.4

> **Acknowledgments**
> 1. Thanks to [IPTV Official Group](http://t.me/iptvorganization) for sharing the algorithm source code
> 2. Thanks to ll from the Gary's Club group for providing live_ids for many channels
> 3. Thanks to the APTV group owner for technical help

**中文文档**: [README-CN.md](README-CN.md)

CCTV live streaming via Docker — **CCTV channels only** (30 channels): CCTV-1~17, 5+, 6, 3 theater channels, 4K/8K, CGTN. Local satellite channels have been completely removed.

## What's inside

- **30 CCTV channels** with groups (`group-title`): 央视FHD / 央视UHD / CGTN
- **True 4K channels**: CCTV-4K, CCTV-8K, CCTV-16 4K via device protocol
- **7-day catchup & timeshift**: 19 channels support 7-day program replay (`catchup="append"`)
- Pure Python, zero dependencies, single port (8767)
- Auto keep-alive: heartbeat every 30s, silent session renewal, 24/7 background worker
- Persistent device identity: `./data` volume survives container rebuilds
- APTV player optimized: no preview/latency probing to avoid triggering rate limits

## One-command VPS deploy

```bash
curl -sSL https://cdn.jsdelivr.net/gh/waastudios/ysptp-docker@main/install.sh|bash
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

> Note: `localhost` only works on the machine itself. On a VPS, always replace it with the public IP.

## Ports & firewall

| Port | Purpose |
| --- | --- |
| 8767 | Single port: homepage, subscriptions, 30 channels, TS relay, aggregated EPG |

```bash
ufw allow 8767/tcp
```

## EPG Guide Subscription

This project ships a built-in aggregated EPG endpoint — no need to configure third-party EPG sources manually:

- URL (copy-paste ready; replace `<VPS_PUBLIC_IP>` with your VPS public IP or LAN IP):
  ```
  http://<VPS_PUBLIC_IP>:8767/epg.xml
  ```
- Content: programme guide for only the 30 channels in this project (CCTV FHD / CCTV UHD / CGTN); irrelevant channels are filtered out
- Upstream sources (merged automatically; the two complement each other, one going down won't break the other):
  - `https://live.fanmingming.com/e.xml`
  - `https://epg.112114.xyz/pp.xml.gz`
- Refresh: auto-updates every 6 hours; fetched in the background on first access, just retry after a moment

The `/cctv.m3u` playlist already points to this address, so players load the guide automatically.

## Notes

- **Bandwidth**: 4K channels relay video through the VPS (~15GB/hour at 35Mbps). A VPS far from CCTV's CDN (e.g. US) may stutter on 4K; an Asia VPS is recommended for smooth 4K.
- **Device registration**: first boot takes ~5-10s for device registration; rebuilding the container requires re-registration (normal).
- Subscriptions include logos, `tvg-id`, `group-title`, and aggregated EPG (`/epg.xml`, merged from two upstream sources, only the 30 channels in this project) — no manual EPG setup needed.

## Common commands

```bash
docker compose up -d --build   # start / update
docker logs -f ysp-live        # logs
docker compose restart         # restart
docker compose down            # stop
```
