#!/bin/bash
# ysp-live v9.0 一键部署脚本
set -e
cd /opt
curl -sSL -o v9.0.zip "https://github.com/waastudios/ysptp-docker/releases/download/v9.0/ysp-live-docker-v9.0.zip"
python3 -c "import zipfile;zipfile.ZipFile('v9.0.zip').extractall('/opt/ysp-live-docker')"
cd /opt/ysp-live-docker
docker compose up -d --build
IP=$(curl -s --max-time 5 ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
echo ""
echo "ysp-live已部署完毕"
echo "订阅地址: http://$IP:8767/cctv.m3u"
echo "节目单订阅: http://$IP:8767/epg.xml"
echo "查看日志: docker logs -f ysp-live"
