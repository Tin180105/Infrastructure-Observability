#!/usr/bin/env python3
"""T15 - Tổng hợp baseline (mean, p95, max) CPU, RAM, disk, network từ Prometheus.

Chạy ở thư mục gốc repo, trong VM đang chạy lab:
    python3 scripts/baseline.py 24          # đo 24 giờ gần nhất
    PROM_URL=http://localhost:9090 python3 scripts/baseline.py 48

Kết quả:
    data/baseline/raw_<metric>.csv          mẫu thô (có thể không commit nếu nặng)
    data/baseline/baseline_summary.csv      mean, p95, max theo host/metric
"""
import os
import sys
import time
from datetime import timedelta, timezone

import pandas as pd
import requests

PROM = os.environ.get("PROM_URL", "http://localhost:9090")
HOURS = float(sys.argv[1]) if len(sys.argv) > 1 else 24
STEP = 60  # giây
OUT = "data/baseline"

FS = 'fstype!~"tmpfs|overlay|squashfs|ramfs|.*fuse.*"'
NIC = 'device!~"lo|veth.*|docker.*|br-.*"'
QUERIES = {
    "cpu_pct": '100 - avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100',
    "ram_pct": "(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100",
    "disk_pct": f"(1 - node_filesystem_avail_bytes{{{FS}}} / node_filesystem_size_bytes{{{FS}}}) * 100",
    "net_rx_Bps": f"sum by(instance)(rate(node_network_receive_bytes_total{{{NIC}}}[1m]))",
    "net_tx_Bps": f"sum by(instance)(rate(node_network_transmit_bytes_total{{{NIC}}}[1m]))",
}


def fetch(query, start, end):
    """Lấy mẫu thô; chia nhỏ vì Prometheus giới hạn ~11.000 điểm mỗi truy vấn."""
    rows, t = [], start
    while t < end:
        t2 = min(t + STEP * 10000, end)
        r = requests.get(
            f"{PROM}/api/v1/query_range",
            params={"query": query, "start": t, "end": t2, "step": STEP},
            timeout=60,
        )
        r.raise_for_status()
        body = r.json()
        if body.get("status") != "success":
            raise RuntimeError(f"Prometheus lỗi: {body}")
        for s in body["data"]["result"]:
            m = s["metric"]
            key = m.get("instance", "?") + (f" {m['mountpoint']}" if "mountpoint" in m else "")
            rows += [(key, float(ts), float(v)) for ts, v in s["values"]]
        t = t2 + STEP
    return pd.DataFrame(rows, columns=["series", "ts", "value"])


def main():
    end = int(time.time())
    start = int(end - HOURS * 3600)
    os.makedirs(OUT, exist_ok=True)
    parts = []
    for name, query in QUERIES.items():
        df = fetch(query, start, end)
        if df.empty:
            print(f"CẢNH BÁO: không có dữ liệu cho {name}. Kiểm tra target UP và khoảng thời gian.")
            continue
        df.to_csv(f"{OUT}/raw_{name}.csv", index=False)
        s = (
            df.groupby("series")["value"]
            .agg(mean="mean", p95=lambda x: x.quantile(0.95), max="max", n_samples="count")
            .reset_index()
        )
        s.insert(0, "metric", name)
        parts.append(s)
    if not parts:
        sys.exit("Không có dữ liệu nào. Kiểm tra PROM_URL và Prometheus.")
    res = pd.concat(parts, ignore_index=True).round(3)
    res = res[res["n_samples"] > 0]  # bỏ series toàn NaN (ví dụ phân vùng ảo vmblock-fuse)
    vn = timezone(timedelta(hours=7))  # giờ Việt Nam (UTC+7)
    res["window_start"] = pd.to_datetime(start, unit="s", utc=True).tz_convert(vn).isoformat()
    res["window_end"] = pd.to_datetime(end, unit="s", utc=True).tz_convert(vn).isoformat()
    res.to_csv(f"{OUT}/baseline_summary.csv", index=False)
    print(res.to_string(index=False))
    print(f"\nĐã ghi {OUT}/baseline_summary.csv")


if __name__ == "__main__":
    main()