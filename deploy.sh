#!/usr/bin/env bash
# ysp-live v6.0 一键部署脚本（VPS）
# 用法：sudo ./deploy.sh
# 做什么：装 Python3（如缺）→ 装 systemd 服务 → 开机自启 → 输出订阅地址
set -euo pipefail
cd "$(dirname "$0")"

PORT="${PORT:-8767}"

if [ "$(id -u)" -ne 0 ]; then
  echo "请用 root 运行：sudo ./deploy.sh"
  exit 1
fi

echo "[1/4] 检查 Python3..."
if ! command -v python3 >/dev/null 2>&1; then
  echo "正在安装 Python3..."
  if command -v apt-get >/dev/null 2>&1; then
    apt-get update -qq && apt-get install -y -qq python3
  elif command -v yum >/dev/null 2>&1; then
    yum install -y -q python3
  elif command -v apk >/dev/null 2>&1; then
    apk add --no-cache python3
  else
    echo "装不上 Python3，请手动安装后重试"
    exit 1
  fi
else
  echo "Python3 已就绪：$(python3 --version)"
fi

echo "[2/4] 安装 ysp-live 到 /opt/ysp-live..."
mkdir -p /opt/ysp-live
cp ysp-live.py /opt/ysp-live/
chmod +x /opt/ysp-live/ysp-live.py

echo "[3/4] 安装 systemd 服务..."
sed -e "s/{{PORT}}/$PORT/g" ysp-live.service > /etc/systemd/system/ysp-live.service
systemctl daemon-reload
systemctl enable --now ysp-live

# 放行防火墙
if command -v ufw >/dev/null 2>&1; then ufw allow "$PORT"/tcp || true; fi
if command -v firewall-cmd >/dev/null 2>&1; then
  firewall-cmd --permanent --add-port="$PORT"/tcp || true
  firewall-cmd --reload || true
fi

echo "[4/4] 等待启动..."
sleep 8

IP=$(curl -s --max-time 10 ifconfig.me 2>/dev/null || echo "")
[ -z "$IP" ] && IP="<VPS公网IP>"

echo
echo "=== 部署完成 ==="
echo "聚合订阅（64 路）: http://$IP:$PORT/all.m3u"
echo "首页            : http://$IP:$PORT/"
echo "诊断页          : http://$IP:$PORT/diag"
echo
echo "设备协议首次注册约 5~10 秒，看日志确认："
echo "  journalctl -u ysp-live -f"
echo "看到 '设备协议就绪' 即为 26 路高码率/真4K 就绪。"
