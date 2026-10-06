#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPG 聚合订阅模块 (ysptp-docker 版)

从两个上游 EPG 源拉取节目单，只保留本项目实际在播的频道，
合并去重后生成单一 XMLTV，供 /epg.xml 接口使用。

上游源:
  1. https://live.fanmingming.com/e.xml
  2. https://epg.112114.xyz/pp.xml.gz

两个项目各自独立，本模块只服务 docker 版（30 路 cctv/cgtn）。
"""
from __future__ import annotations

import gzip
import io
import threading
import time
import urllib.request
import xml.etree.ElementTree as ET

# 上游 EPG 源
UPSTREAM_SOURCES = [
    "https://live.fanmingming.com/e.xml",
    "https://epg.112114.xyz/pp.xml.gz",
]

# 刷新间隔（秒）：6 小时
REFRESH_INTERVAL = 6 * 3600

# 请求超时（秒）
FETCH_TIMEOUT = 60


def _bust_url(url: str) -> str:
    """fanmingming 的 CDN 缓存激进，加时间戳参数强制回源"""
    if "fanmingming.com" in url:
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}_t={int(time.time())}"
    return url


class EpgAggregator:
    """EPG 聚合器：拉取、过滤、合并、缓存。"""

    def __init__(self, wanted_ids: set[str], refresh_interval: int = REFRESH_INTERVAL):
        """
        :param wanted_ids: 本项目需要的 EPG channel id 集合（如 {"CCTV1", "CGTN英语"}）
        :param refresh_interval: 缓存刷新间隔（秒）
        """
        self.wanted_ids = wanted_ids
        self.refresh_interval = refresh_interval
        self._lock = threading.Lock()
        self._xml: str | None = None
        self._last_refresh: float = 0
        self._last_error: str | None = None
        self._refreshing = False

    def get_xml(self) -> str | None:
        """返回聚合后的 XMLTV 字符串；缓存过期则触发后台刷新。"""
        with self._lock:
            xml = self._xml
            age = time.time() - self._last_refresh
        if xml is None or age > self.refresh_interval:
            self._trigger_refresh()
        with self._lock:
            return self._xml

    def last_error(self) -> str | None:
        with self._lock:
            return self._last_error

    def last_refresh_time(self) -> float:
        with self._lock:
            return self._last_refresh

    def refresh_now(self) -> bool:
        """同步刷新，返回是否成功。"""
        try:
            xml = self._build()
        except Exception as e:
            with self._lock:
                self._last_error = f"{type(e).__name__}: {e}"
            return False
        with self._lock:
            self._xml = xml
            self._last_refresh = time.time()
            self._last_error = None
        return True

    def _trigger_refresh(self):
        with self._lock:
            if self._refreshing:
                return
            self._refreshing = True

        def _run():
            try:
                self.refresh_now()
            finally:
                with self._lock:
                    self._refreshing = False

        t = threading.Thread(target=_run, daemon=True, name="epg-refresh")
        t.start()

    def _fetch(self, url: str) -> bytes:
        url = _bust_url(url)
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ysp-epg/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            return resp.read()

    def _parse(self, data: bytes, url: str) -> ET.Element:
        if ".gz" in url:
            data = gzip.decompress(data)
        # 容错解析：忽略编码问题
        return ET.fromstring(data)

    def _build(self) -> str:
        # channel_id -> display-name
        channels: dict[str, str] = {}
        # (channel_id, start) -> programme element（去重用）
        programmes: dict[tuple[str, str], ET.Element] = {}

        for url in UPSTREAM_SOURCES:
            try:
                data = self._fetch(url)
                root = self._parse(data, url)
            except Exception:
                continue  # 单个源失败不影响另一个
            for ch in root.findall("channel"):
                cid = ch.get("id", "")
                if cid not in self.wanted_ids:
                    continue
                if cid not in channels:
                    dn = ch.find("display-name")
                    channels[cid] = dn.text if dn is not None and dn.text else cid
            for pg in root.findall("programme"):
                cid = pg.get("channel", "")
                if cid not in self.wanted_ids:
                    continue
                key = (cid, pg.get("start", ""))
                # 先到的源优先（fanmingming 在前）
                if key not in programmes:
                    programmes[key] = pg

        # 生成 XMLTV
        tv = ET.Element("tv")
        tv.set("generator-info-name", "ysptp-epg-aggregator")
        for cid in sorted(channels):
            ch_el = ET.SubElement(tv, "channel", id=cid)
            dn_el = ET.SubElement(ch_el, "display-name", lang="zh")
            dn_el.text = channels[cid]
        # 按频道 + 开始时间排序
        for (cid, _start), pg in sorted(programmes.items(), key=lambda kv: (kv[0][0], kv[0][1])):
            tv.append(pg)

        buf = io.BytesIO()
        tree = ET.ElementTree(tv)
        tree.write(buf, encoding="utf-8", xml_declaration=True)
        return buf.getvalue().decode("utf-8")
