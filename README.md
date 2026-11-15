# N4.7 - Lab giám sát máy chủ / container (bản khởi đầu)

Prometheus + Node Exporter + cAdvisor + Blackbox + Alertmanager + Grafana, chạy bằng Docker Compose.
Chỉ dùng cho lab cục bộ; không dùng credential sản xuất, không kết nối hệ thống thật.

## 1. Chạy lab

```bash
docker compose pull          # kiểm tra các tag trong .env có tồn tại không
docker compose up -d
docker compose ps            # tất cả phải ở trạng thái running
```

| Dịch vụ | Địa chỉ | Ghi chú |
|---|---|---|
| Grafana | http://localhost:3000 | admin / admin-lab (xem .env). Dashboard nằm trong thư mục "N4.7" |
| Prometheus | http://localhost:9090 | Trang Status > Targets: các job phải UP. Trang Alerts: xem luật |
| Alertmanager | http://localhost:9093 | Xem cảnh báo đang kích hoạt |
| cAdvisor | http://localhost:8080 | Metric theo container |

Dừng lab: `docker compose down`. Xóa cả dữ liệu: `docker compose down -v`.

## 2. Kiểm tra nhanh

1. Prometheus > Status > Targets: các job `prometheus`, `node`, `cadvisor`, `alertmanager`, `blackbox-http` đều UP.
2. Grafana > Dashboards > N4.7 > "Host và dịch vụ (tổng quan)": có số liệu sau khoảng 1 phút.
3. Kiểm tra cú pháp luật cảnh báo:
   `docker compose exec prometheus promtool check rules /etc/prometheus/rules/alerts.yml`

## 3. Thử kịch bản

Ngưỡng và thời gian `for` trong `infra/prometheus/rules/alerts.yml` chỉ là giá trị nháp.

**S1 - CPU cao** (cảnh báo `HostHighCpu` sau khoảng 2 phút):

```bash
docker compose exec ubuntu-target bash -c \
  "apt-get update && apt-get install -y stress-ng && stress-ng --cpu 0 --timeout 300s"
```

**S3 - Service down** (cảnh báo `EndpointDown` sau khoảng 30 giây):

```bash
docker compose stop demo-app      # gây lỗi
docker compose start demo-app     # khôi phục
```

**S2 - Disk đầy** và **S4 - spike ngắn** sẽ bổ sung ở bước sau
(S2 dùng volume dung lượng giới hạn thay cho đĩa loop để không cần quyền đặc biệt).

## 4. Ghi chú

- Cổng chỉ mở ở 127.0.0.1 để tránh lộ ra mạng.
- Docker Desktop (Windows/Mac) chạy container trong một VM Linux ẩn, nên Node Exporter đo VM đó, không đo máy thật.
  Khi đo baseline và demo nghiệm thu, nên chạy trên một máy Ubuntu chuẩn của nhóm.
- Nếu `node-exporter` báo lỗi mount `rslave` (thường gặp trên Mac), bỏ phần `,rslave` trong docker-compose.yml.
- Nếu `cadvisor` lỗi trên Docker Desktop, xem log: `docker compose logs cadvisor`.
