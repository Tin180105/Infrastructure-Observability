# Baseline CPU, RAM, disk, network (T15)

**Trạng thái:** baseline sơ bộ, chưa thống nhất với UTH và mentor VNPT.

## Cách đo
- Môi trường: VM Ubuntu 24.04 trên VMware Workstation, ... CPU, ... MB RAM, đĩa 40 GB. Chạy Docker Compose.
- Stack: Prometheus (scrape 15 giây) + Node Exporter (job `node`, host `lab-host`).
- Cửa sổ đo: 6,5 giờ, từ 14:47 đến 21:17 ngày 26/11/2026 (UTC+7).
  Bỏ khoảng 1 giờ đầu sau khi bật lab (khởi động, tải image).
- Không chạy kịch bản lỗi S1–S4 trong thời gian đo.
- Mỗi metric có 391 mẫu (step 60 giây).

## Kết quả (host lab-host)
| Metric | Trung bình | p95 | Lớn nhất |
| --- | --- | --- | --- |
| CPU (%) | 3,041 | 3,511 | 42,744 |
| RAM (%) | 41,050 | 41,698 | 43,142 |
| Disk `/` (%) | 36,457 | 37,969 | 37,975 |
| Network nhận (byte/s) | 37,305 | 37,200 | 41,956 |
| Network gửi (byte/s) | 736,901 | 738,122 | 739,644 |

Chi tiết: `baseline_summary.csv`.

## Cách tính
Script `scripts/baseline.py` lấy mẫu thô từ Prometheus qua API `query_range`
và tính trung bình, p95, lớn nhất từ mẫu thô (không tổng hợp từ giá trị đã tổng hợp).
Chạy lại: `python3 scripts/baseline.py 6.5` (đối số là số giờ gần nhất cần đo).
Các truy vấn PromQL nằm ở đầu file script.

## Hạn chế
- Chỉ đo 6,5 giờ, chưa phủ chu kỳ ngày đêm; p95 và max có thể thấp hơn thực tế.
- CPU max (42,7%) là đỉnh do thao tác cài gói trong VM lúc khoảng 21:00, không phải tải bình thường.
- Disk tăng một bậc (khoảng 36,4% lên khoảng 38%) vì cài phần mềm trong lúc đo, nên p95 của disk phản ánh mức sau khi cài.
- Một host duy nhất; chưa có dữ liệu VM thứ hai.
- VM gần như nhàn rỗi nên mean và p95 rất sát nhau; ngưỡng cảnh báo không nên đặt bằng p95.