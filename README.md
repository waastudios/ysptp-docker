# ysp-live v7.4

> **Acknowledgments**
> 1. Thanks to IPTV Official Group for sharing the algorithm source code
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
cd /opt && curl -sSL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36" -o v7.4.zip "https://github.com/waastudios/ysptp-rs/releases/download/v7.4/ysp-live-docker-v7.4.zip" && python3 -c "import zipfile; zipfile.ZipFile('v7.4.zip').extractall('/opt/ysp-live-docker')" && cd /opt/ysp-live-docker && docker compose up -d --build
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

- CCTV subscription (30 channels, with groups): `http://<VPS_PUBLIC_IP>:8767/cctv.m3u`
- Homepage: `http://<VPS_PUBLIC_IP>:8767/`
- Diagnostics: `http://<VPS_PUBLIC_IP>:8767/diag`

> Note: `localhost` only works on the machine itself. On a VPS, always replace it with the public IP.

## Ports & firewall

| Port | Purpose |
| --- | --- |
| 8767 | Single port: homepage, subscriptions, 30 channels, TS relay |

```bash
ufw allow 8767/tcp
```

## Notes

- **Bandwidth**: 4K channels relay video through the VPS (~15GB/hour at 35Mbps). A VPS far from CCTV's CDN (e.g. US) may stutter on 4K; an Asia VPS is recommended for smooth 4K.
- **Device registration**: first boot takes ~5-10s for device registration; rebuilding the container requires re-registration (normal).
- Subscriptions include logos, `tvg-id`, `group-title`, and EPG — no manual EPG setup needed.

## Common commands

```bash
docker compose up -d --build   # start / update
docker logs -f ysp-live        # logs
docker compose restart         # restart
docker compose down            # stop
```
