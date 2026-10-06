#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPG 聚合订阅模块 (ysptp-docker 版)

从两个上游 EPG 源拉取节目单，只保留本项目实际在播的频道，
合并去重后生成单一 XMLTV，供 /epg.xml 接口使用。

上游源:
  1. https://epg.pw/xmltv/epg_CN.xml.gz（数字 ID，需映射为标准 ID）
  2. https://epg.zsdc.eu.org/t.xml.gz

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
    "https://epg.pw/xmltv/epg_CN.xml.gz",
    "https://epg.zsdc.eu.org/t.xml.gz",
]

# epg.pw 数字频道 ID → 标准 ID 映射
EPGPW_ID_MAP = {
    "545932": "CCTV1", "545933": "CCTV2", "545934": "CCTV3",
    "545935": "CCTV4", "545936": "CCTV5", "545937": "CCTV5+",
    "545938": "CCTV6", "545939": "CCTV7", "545940": "CCTV8",
    "545941": "CCTV9", "545942": "CCTV10", "545943": "CCTV11",
    "545944": "CCTV12", "545945": "CCTV13", "545946": "CCTV14",
    "545947": "CCTV15", "545948": "CCTV16", "545949": "CCTV17",
    "539634": "CCTV4K", "545950": "CCTV-8K",
    "544310": "CCTV怀旧剧场", "544354": "CCTV第一剧场", "544381": "CCTV风云剧场",
    "544390": "CGTN纪录", "570483": "CGTN西语", "570484": "CGTN俄语",
    "570492": "CGTN阿语", "570493": "CGTN法语",
    # 卫视（display-name 即中文名，直接映射）
    "539726": "北京卫视", "539834": "江苏卫视", "539699": "东方卫视",
    "539700": "浙江卫视", "539731": "湖南卫视", "539692": "湖北卫视",
    "539712": "广东卫视", "539698": "广西卫视", "539850": "黑龙江卫视",
    "539659": "海南卫视", "539790": "重庆卫视", "539856": "深圳卫视",
    "539826": "四川卫视", "539838": "河南卫视", "539717": "东南卫视",
    "539814": "贵州卫视", "539876": "江西卫视", "539777": "辽宁卫视",
    "539701": "安徽卫视", "539695": "河北卫视", "539740": "山东卫视",
    "539703": "天津卫视", "539864": "吉林卫视", "539697": "陕西卫视",
    "539644": "宁夏卫视", "539839": "内蒙古卫视", "539641": "云南卫视",
    "539843": "山西卫视", "539728": "青海卫视", "539730": "西藏卫视",
    "539831": "新疆卫视",
}

# 刷新间隔（秒）：6 小时
REFRESH_INTERVAL = 6 * 3600

# 请求超时（秒）
FETCH_TIMEOUT = 60


def _normalize_id(cid: str, url: str) -> str:
    """epg.pw 用数字 ID，映射为标准 ID；其他源直接用"""
    if "epg.pw" in url:
        return EPGPW_ID_MAP.get(cid, cid)
    return cid


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
                cid = _normalize_id(ch.get("id", ""), url)
                if cid not in self.wanted_ids:
                    continue
                if cid not in channels:
                    dn = ch.find("display-name")
                    channels[cid] = dn.text if dn is not None and dn.text else cid
            for pg in root.findall("programme"):
                cid = _normalize_id(pg.get("channel", ""), url)
                if cid not in self.wanted_ids:
                    continue
                key = (cid, pg.get("start", ""))
                # 先到的源优先（epg.pw 在前）；同时修正 programme 的 channel 属性
                if key not in programmes:
                    pg.set("channel", cid)
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
