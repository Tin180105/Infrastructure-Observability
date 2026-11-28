# T16 – Bộ tham số khởi đầu (ngưỡng, for) từ baseline

**Trạng thái:** Đây là tham số khởi đầu, không phải kết quả tối ưu. Việc chốt chính thức: CPU ở T66 (tuần 10); chỉ tiêu định lượng đề xuất chốt trong tuần 6 (email T19, câu 12).

Lập: 28/11/2026 (tuần 4).

1\. Dữ liệu đầu vào

* Baseline T15: `data/baseline/baseline\_summary.csv`, host `lab-host`, VM Ubuntu 24.04 gần như nhàn rỗi.
* Cửa sổ đo: 6,5 giờ, 14:47–21:17 ngày 26/11/2026, 391 mẫu, bước lấy mẫu 60 giây.
* Cấu hình Prometheus (`infra/prometheus/prometheus.yml`): `scrape\_interval` 15s, `evaluation\_interval` 15s.
* Luật hiện có: `infra/prometheus/rules/alerts.yml`.

|Metric|Trung bình|p95|Lớn nhất|
|-|-|-|-|
|CPU (%)|3,041|3,511|42,744|
|RAM (%)|41,050|41,698|43,142|
|Disk `/` (%)|36,457|37,969|37,975|
|Network nhận (byte/s)|37,305|37,200|41,956|
|Network gửi (byte/s)|736,901|738,122|739,644|

## 2\. Quy tắc chọn (quy tắc nháp của nhóm)

1. Ngưỡng phải cao hơn **max baseline cộng đệm 10 điểm %**, để lúc rảnh không báo.
2. Ngưỡng phải thấp hơn mức mà kịch bản lỗi đạt được (S1 đẩy CPU gần 100%; S2 làm đầy phân vùng ảo).
3. Lấy giá trị đang có trong `alerts.yml` làm điểm xuất phát; chỉ đổi khi vi phạm quy tắc 1 hoặc 2.
4. Không đặt ngưỡng bằng p95 (VM nhàn rỗi nên p95 sát mean; README baseline đã ghi điều này).
5. `for` tối thiểu bằng 2 chu kỳ scrape (30s) và phải dài hơn thời gian vượt ngưỡng của spike S4. `for` cộng thẳng vào thời gian phát hiện.

## 3\. Bảng tham số nháp

|Luật|Max baseline|Ngưỡng|Chỗ trống tới ngưỡng|`for`|Mức|Lý do ngắn|Trạng thái|
|-|-|-|-|-|-|-|-|
|HostHighCpu|42,744%|80%|37,3 điểm|2m (8 chu kỳ)|warning|42,7 + 10 = 52,7 < 80; S1 vượt 80|Nháp|
|HostHighMemory|43,142%|85%|41,9 điểm|2m|warning|43,1 + 10 = 53,1 < 85|Nháp|
|HostDiskAlmostFull|37,975% (`/`)|85%|47,0 điểm|2m|critical|38,0 + 10 = 48,0 < 85; S2 chỉ làm đầy phân vùng ảo|Nháp|
|ExporterDown|–|`up == 0`|–|1m (4 chu kỳ)|critical|Chịu được vài lần scrape hụt|Nháp|
|EndpointDown|–|`probe\_success == 0`|–|30s (2 chu kỳ)|critical|Cần xuống liên tục, S3 muốn phát hiện nhanh|Nháp|
|Network (rx/tx)|41,956 / 739,644 B/s|không đặt|–|–|–|Chỉ để dashboard; chưa có luật mạng|–|

**Kết luận T16:** baseline không buộc đổi giá trị nào trong `alerts.yml`. Cả ba luật tài nguyên có chỗ trống trên 37 điểm % so với max baseline. Cần sửa comment đầu file và mô tả cảnh báo để ghi "đã đối chiếu baseline 26/11/2026, chưa thống nhất".

## 4\. Ước tính thời gian phát hiện (tính toán, CHƯA đo)

Giả định S1 đưa CPU lên khoảng 100%. Cửa sổ `rate(...\[1m])` cần khoảng 48 giây gây tải để vượt 80%.

|Kịch bản|Ước tính tới khi firing|Ghi chú|
|-|-|-|
|S1 CPU cao|khoảng 48s + 2m ≈ 3 phút (cộng tối đa 15s)|README đang ghi "khoảng 2 phút": cần đo lại và sửa|
|S3 service down|khoảng 30–45s|`for: 30s`, probe mỗi 15s|
|ExporterDown|khoảng 1 phút đến 1 phút 15s||
|S4 spike|không được firing|Spike nên dài 60–90s: đủ vượt 80% trên `rate\[1m]` nhưng chỉ vượt khoảng dưới 1 phút, ngắn hơn `for`. Spike dưới khoảng 48s không vượt ngưỡng nên không chứng minh được tác dụng của `for`|

Thời gian gửi thông báo còn cộng `group\_wait` của Alertmanager. Các số trên là ước tính để lên kế hoạch kịch bản, số liệu chính thức lấy từ T67.

## 5\. Hạn chế của baseline

* Chỉ 6,5 giờ, chưa phủ chu kỳ ngày đêm; max có thể thấp hơn thực tế.
* Mẫu bước 60s nên có thể bỏ sót đỉnh ngắn hơn một phút (Prometheus quét 15s).
* CPU max 42,7% là một lần cài gói trong VM khoảng 21:00, không phải tải bình thường.
* Disk tăng một bậc (khoảng 36,4% lên khoảng 38%) do cài phần mềm trong lúc đo.
* Một host duy nhất; chưa có VM thứ hai.
* VM nhàn rỗi: baseline chỉ chứng minh ngưỡng nằm xa mức rảnh, không chứng minh ngưỡng tốt cho tải thật.
* Phân vùng ảo của S2 chưa có baseline.

## 6\. Việc cần làm tiếp

1. Người kiểm đối chiếu bảng mục 3 với `baseline\_summary.csv`, ghi một dòng vào `ai-verification-log.md`.
2. Sửa comment đầu `infra/prometheus/rules/alerts.yml` và mô tả cảnh báo (đang ghi cứng "ngưỡng nháp 80%"): ghi ngày đối chiếu. Chạy `promtool check rules`.
3. Sửa README mục S1 sau khi đo thật ("khoảng 2 phút" so với ước tính khoảng 3 phút).
4. Tuần 10 (T66): chốt tham số CPU sau khi có số đo S1.

