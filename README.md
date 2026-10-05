# ysp-live v6.0

> **Acknowledgments**
> 1. Thanks to IPTV Official Group for sharing the algorithm source code
> 2. Thanks to ll from the Gary's Club group for providing live_ids for many channels
> 3. Thanks to the APTV group owner for technical help

64 live CCTV channels, pure Python single file, single port. One command to run on a VPS.

**中文文档**: [README-CN.md](README-CN.md)

## What's inside

- **64 channels**: 21 CCTV + 6 CGTN + 3 theater + 32 satellite + CETV-1 + Chinese classics. Pure Python stdlib, zero binaries, zero dependencies.
- **26 true-4K / high-bitrate channels** via device protocol: CCTV-1/2/3/4/5/5+/7/8/9/10/11/12/13/14/15/16/17, CCTV-4K/8K/16-4K (real 3840×2160), CGTN main/French/Russian/Arabic/Spanish/Documentary. Falls back to 1080p seamlessly if the device protocol isn't ready.
- **Single-port architecture**: everything on port 8767, no extra 8766 mapping.
- Device identity persisted permanently, background keep-alive; subscription includes channel logos, `tvg-id` and EPG URLs — players match the program guide automatically.

## One-command VPS deploy

```bash
curl -sSL -O https://github.com/waastudios/ysptp-rs/releases/download/v6.0/ysp-live-v6.0.zip && python3 -c "import zipfile; zipfile.ZipFile('ysp-live-v6.0.zip').extractall('ysp-live-v6')" && cd ysp-live-v6 && sudo ./deploy.sh
```

`deploy.sh`: checks/installs Python3 → installs to `/opt/ysp-live` → registers a systemd service with autostart → prints subscription URLs.

First device-protocol registration takes ~5–10s. Confirm with:

```bash
journalctl -u ysp-live -f
```

`设备协议就绪` means the 26 high-bitrate/4K channels are ready.

## Tested on datacenter VPS

No home broadband required. Verified on a US datacenter VPS: device registration succeeded on first try. The old "datacenter networks will be rejected" warning is outdated.

Registration is saved at `/opt/ysp-live/device-state-rs.json` — **do not delete it**.

## Ports & firewall

Only **8767/TCP** needs to be open:

```bash
ufw allow 8767/tcp
```

## Usage

Get your VPS public IP with `curl -s ifconfig.me`, then:

- Aggregated subscription (all 64 channels, recommended): `http://<VPS_PUBLIC_IP>:8767/all.m3u`
- Homepage: `http://<VPS_PUBLIC_IP>:8767/`
- Diagnostics: `http://<VPS_PUBLIC_IP>:8767/diag`

> Note: `localhost` only works on the machine itself. On a VPS, replace it with the public IP; on LAN, use the LAN IP (e.g. `http://192.168.1.10:8767/all.m3u`).

## Common commands

```bash
sudo systemctl restart ysp-live   # restart
sudo systemctl stop ysp-live      # stop
journalctl -u ysp-live -f         # logs
```

1080p only (skip device protocol): `python3 ysp-live.py --no-4k`

## Troubleshooting

- **Device protocol never ready**: check `http://<VPS_PUBLIC_IP>:8767/diag`, then `journalctl -u ysp-live`.
- **Port in use**: `ss -tlnp | grep 8767` to find the culprit.
- **Windows / Mac**: run `python3 ysp-live.py` (Windows: `py ysp-live.py`), open `http://localhost:8767/`.
