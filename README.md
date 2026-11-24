# N4.7 - Lab giám sát máy chủ / container (bản khởi đầu)

Prometheus + Node Exporter + cAdvisor + Blackbox + Alertmanager + Grafana, chạy bằng Docker Compose.
Chỉ dùng cho lab cục bộ; không dùng credential sản xuất, không kết nối hệ thống thật.

**Mục lục:** [1. Chạy lab](#1-chạy-lab) · [2. Kiểm tra nhanh](#2-kiểm-tra-nhanh) · [3. Thử kịch bản](#3-thử-kịch-bản) · [4. Ghi chú](#4-ghi-chú) · [5. Khảo sát dữ liệu public (T14)](#5-khảo-sát-dữ-liệu-public-t14)

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

Ngưỡng và thời gian `for` trong `infra/prometheus/rules/alerts.yml` chỉ là giá trị nháp, sẽ chỉnh sau khi đo baseline và thống nhất với UTH, mentor VNPT.

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
- Không commit file `.env` thật; chỉ commit `.env.example`.

---

## 5. Khảo sát dữ liệu public (T14)

Cập nhật: 24/11/2026 (task T14, tuần 4). Khảo sát ba bộ dữ liệu public: Google Cluster Data, NAB, Loghub.

### 5.1. Tóm tắt

| Bộ dữ liệu | Loại dữ liệu | Giấy phép | Dung lượng chính | Vai trò trong đề tài |
|---|---|---|---|---|
| [Google Cluster Data](https://github.com/google/cluster-data) | Trace sử dụng tài nguyên cụm máy chủ | CC BY 4.0 | V2: khoảng 41 GB nén; V3: khoảng 2,4 TiB nén | Tham khảo hình dạng tải, lấy mẫu nhỏ nếu cần |
| [NAB](https://github.com/numenta/NAB) | Chuỗi thời gian có nhãn bất thường (58 tệp) | MIT (repo) | Nhỏ (CSV) | Dùng chính để thử luật ngưỡng và cảnh báo giả |
| [Loghub](https://github.com/logpai/loghub) | Log hệ thống (HDFS, Hadoop, Linux...) | Giấy phép riêng: nghiên cứu hoặc học thuật | Từ vài trăm KB đến khoảng 2 GB mỗi bộ | Chỉ khảo sát, không đưa vào demo |

Dữ liệu public chỉ để tham khảo và kiểm thử ngoài lab. Baseline và kịch bản S1-S4 dùng metric do nhóm tự thu từ Prometheus. Không dùng dữ liệu VNPT nhạy cảm (IP, tên hệ thống, log truy cập, sơ đồ DC).

### 5.2. Google Cluster Data

#### Mục đích sử dụng

Bộ dữ liệu ghi lại hoạt động của các cụm máy chủ do Google sử dụng: cách job và task được thực thi, cùng thông tin tài nguyên hệ thống.

- Phân tích mức sử dụng tài nguyên: CPU, RAM, tài nguyên được yêu cầu so với thực tế sử dụng.
- Nghiên cứu lập lịch công việc: job/task vào cluster, chạy và kết thúc ra sao.
- Phân tích quá tải: tìm khoảng thời gian sử dụng tài nguyên tăng cao hoặc bất thường.
- Mô phỏng tải hệ thống: dùng hành vi workload trong trace để tạo tải thử nghiệm.
- Đánh giá hệ thống giám sát: kiểm tra khả năng phát hiện biến động tài nguyên hoặc thay đổi trạng thái tác vụ.

Phạm vi phù hợp: nghiên cứu hoạt động cụm máy chủ và tài nguyên hệ thống. Đây không phải bộ dữ liệu về log ứng dụng. Nếu dùng cho phát hiện bất thường, nhóm phải tự xác định tiêu chí bất thường.

#### Giấy phép

Dữ liệu và tài liệu trace theo Creative Commons Attribution 4.0 International (CC BY 4.0). Cho phép chia sẻ và chỉnh sửa, kể cả thương mại, với điều kiện ghi công, đính kèm liên kết giấy phép và nêu rõ nếu đã thay đổi dữ liệu. Khi đưa vào báo cáo, ghi tên bộ dữ liệu, phiên bản và nguồn tải.

- Giấy phép: https://creativecommons.org/licenses/by/4.0/
- Repository chính thức: https://github.com/google/cluster-data

#### Cách tải

Có nhiều phiên bản:

- Version 2 (2011): khoảng 41 GB nén, một cell Borg 12,5 nghìn máy.
- Version 3 (2019): khoảng 2,4 TiB nén, chỉ truy cập qua Google BigQuery, không tải về trực tiếp.
- Version 1 (2009): đã lỗi thời, tài liệu khuyên dùng V2 hoặc V3.

Các bước cho Version 2:

1. Đọc tài liệu: https://github.com/google/cluster-data/blob/master/ClusterData2011_2.md
2. Tham gia mailing list `googleclusterdata-discuss` tại https://groups.google.com/g/googleclusterdata-discuss và điền trường **Reason** (mục đích sử dụng). Theo tài liệu V2, đơn thiếu lý do sẽ bị từ chối. Đây là bước cần làm trước khi truy cập dữ liệu V2.
3. Cài Google Cloud CLI: https://cloud.google.com/sdk/docs/install, rồi kiểm tra:

   ```bash
   gcloud --version
   ```

4. Tạo thư mục lưu dữ liệu (xem quy ước ở mục 5.6):

   ```bash
   mkdir -p data/raw/google-cluster
   ```

5. Kiểm tra quyền truy cập bucket (chỉ liệt kê, không tải):

   ```bash
   gcloud storage ls gs://clusterdata-2011-2
   ```

6. Chọn các bảng hoặc tệp cần dùng và chỉ tải phần đó, không tải toàn bộ 41 GB. Sau khi biết đường dẫn từ bước 5:

   ```bash
   gcloud storage cp gs://clusterdata-2011-2/<đường-dẫn-tệp-cần-tải> data/raw/google-cluster/
   ```

   (`<đường-dẫn-tệp-cần-tải>` là chỗ điền sau khi xem kết quả `ls`.)

7. Đọc tài liệu schema để hiểu cấu trúc, tên trường, kiểu dữ liệu và ý nghĩa thuộc tính.

Trạng thái kiểm thử: **chưa kiểm chứng.** Các lệnh `gcloud storage` ở trên chưa được chạy thực tế, nên chưa xác nhận quyền truy cập bucket. Khi đã chạy thử, cập nhật dòng này và ghi kết quả.

Lưu ý: `git clone https://github.com/google/cluster-data.git` chỉ tải repository hướng dẫn, không tải trace. Version 3 xem hướng dẫn BigQuery: https://github.com/google/cluster-data/blob/master/ClusterData2019.md

### 5.3. NAB (Numenta Anomaly Benchmark)

#### Mục đích sử dụng

NAB là bộ dữ liệu chuẩn để đánh giá các phương pháp phát hiện bất thường trên chuỗi thời gian, đặc biệt dữ liệu streaming. Gồm chuỗi thời gian thực tế và nhân tạo, kèm nhãn các khoảng thời gian bất thường. Theo Ahmad, Lavin, Purdy và Agha (2017) [1], NAB được xây dựng để đánh giá thuật toán phát hiện bất thường theo thời gian thực, tập trung vào phát hiện sớm.

Dùng để:

- Kiểm thử thuật toán phát hiện bất thường trên chuỗi thời gian.
- Đánh giá khả năng phát hiện sớm khi dữ liệu cập nhật liên tục.
- So sánh kết quả nhiều thuật toán trên cùng tập dữ liệu.
- Đánh giá cảnh báo nhầm (false positive) và bỏ sót (false negative).

Thành phần cần chú ý:

- `data/`: các tệp CSV chuỗi thời gian (thực tế và nhân tạo), tổng cộng 58 tệp.
- `labels/`: nhãn và khoảng thời gian bất thường.
- `labels/combined_windows.json`: khoảng bắt đầu và kết thúc của từng cửa sổ bất thường theo từng tệp dữ liệu.

#### Giấy phép

Repository NAB dùng MIT License: cho phép sử dụng, sao chép, chỉnh sửa, phân phối, với điều kiện giữ thông báo bản quyền và nội dung giấy phép. Repository có chứa dữ liệu thu thập từ nhiều nguồn; MIT của repo không mặc nhiên thay thế điều kiện riêng của dữ liệu bên thứ ba. Cần kiểm tra nguồn gốc từng bộ nếu tái phân phối hoặc dùng ngoài phạm vi học tập.

- Repository: https://github.com/numenta/NAB
- MIT License: https://github.com/numenta/NAB/blob/master/LICENSE.txt

Trích dẫn khi dùng: Ahmad et al. (2017) [1].

#### Cách tải

Cách 1: tải ZIP.

1. Vào https://github.com/numenta/NAB, nhấn **Code** > **Download ZIP**, giải nén.
2. Lấy dữ liệu ở `NAB/data`, nhãn ở `NAB/labels`.

Cách 2: dùng Git.

```bash
git clone https://github.com/numenta/NAB.git data/raw/NAB
```

Kết quả: các tệp CSV chuỗi thời gian và các tệp nhãn. Chỉ cần đọc CSV, không cần cài framework Python của NAB.

Trạng thái kiểm thử: chưa chạy thử. <!-- TODO tester: clone thử, mở 1 tệp CSV và combined_windows.json, ghi kết quả vào đây. -->

### 5.4. Loghub

#### Mục đích sử dụng

Loghub là bộ sưu tập nhật ký hệ thống từ nhiều loại phần mềm và hạ tầng, dùng trong nghiên cứu phân tích log, khai thác thông tin vận hành và học máy phát hiện sự cố.

- Phân tích log của hệ điều hành, máy chủ, hệ thống phân tán.
- Kiểm thử phát hiện thông báo lỗi và hành vi bất thường trong log.
- Đánh giá công cụ đọc và phân tích log (tách thời gian, thành phần, mức độ, nội dung).
- Nghiên cứu phân loại log, phát hiện bất thường, hỗ trợ tìm nguyên nhân sự cố.
- Có dữ liệu từ HDFS, Hadoop, Spark, Linux, Windows, OpenStack, Apache...

Lưu ý nhãn: không phải bộ nào cũng có nhãn bất thường. Xem cột **Labeled** trong bảng chính thức của repo để chọn bộ có nhãn.

#### Giấy phép

Nhóm đối chiếu ba nguồn:

| Nguồn | Nội dung |
|---|---|
| README repo | Dữ liệu miễn phí cho nghiên cứu hoặc học thuật; dẫn nguồn repo và trích dẫn bài Loghub khi phù hợp |
| Tệp LICENSE của repo | Giấy phép riêng (không phải MIT): phạm vi nghiên cứu hoặc học thuật; dẫn URL repo; trích dẫn bài Loghub; giữ thông báo giấy phép trong mọi bản sao. Không nói rõ về dùng thương mại |
| Zenodo (record 8196385) | Ghi CC BY 4.0, yêu cầu ghi công và dẫn liên kết |

Kết luận áp dụng: LICENSE của repo giới hạn phạm vi nghiên cứu hoặc học thuật, chặt hơn nhãn CC BY trên Zenodo, nên nhóm **chỉ dùng trong học phần** và áp dụng điều kiện chặt hơn. Không mặc định là MIT hoặc được dùng thương mại; nếu sau này dùng ngoài phạm vi học tập thì phải liên hệ tác giả.

Điều kiện khi dùng hoặc phân phối lại:

- Dẫn liên kết repository: https://github.com/logpai/loghub
- Trích dẫn bài báo Loghub [2] (và [3] khi dùng Loghub-2.0).
- Giữ nguyên thông báo giấy phép trong mọi bản sao.

Nguồn: [Repository](https://github.com/logpai/loghub), [LICENSE](https://github.com/logpai/loghub/blob/master/LICENSE), [Zenodo 8196385](https://zenodo.org/records/8196385).

#### Cách tải

Loghub gồm nhiều bộ riêng, tải từng bộ cần dùng.

1. Vào https://github.com/logpai/loghub, tìm bảng **Logs currently available** (tên bộ, mô tả, có nhãn hay không, số dòng, dung lượng, liên kết tải).
2. Chọn bộ cần dùng (ví dụ HDFS_v1, Hadoop, BGL, Linux). Cần nhãn thì ưu tiên bộ có dấu Labeled.
3. Nhấn **Download** ở dòng tương ứng, mở trang Zenodo, chọn tệp và tải.
4. Giải nén (nếu là ZIP hoặc tar.gz) vào `data/raw/loghub/`.
5. Đọc README đi kèm để biết định dạng và cách hiểu nhãn.

Ví dụ: HDFS_v1 là bộ log HDFS có nhãn, thường dùng trong nghiên cứu phát hiện bất thường.

Dung lượng một số bộ (tệp nén trên Zenodo, có thể lớn hơn sau khi giải nén):

| Bộ dữ liệu | Tên tệp | Dung lượng |
|---|---|---|
| HDFS_v1 | `HDFS_v1.zip` | 186,6 MB |
| Windows | `Windows.tar.gz` | 1,7 GB |
| Thunderbird | `Thunderbird.tar.gz` | 2,0 GB |

Với các bộ lớn như Thunderbird và Windows, chuẩn bị đủ dung lượng ổ đĩa trước khi tải.

#### Tài liệu nghiên cứu liên quan

- Loghub (ISSRE 2023) [2]: bộ sưu tập log từ nhiều hạ tầng và phần mềm, hỗ trợ nghiên cứu phân tích log dựa trên AI.
- Loghub-2.0 (ISSTA 2024) [3]: mở rộng dữ liệu để đánh giá kỹ thuật tách mẫu log (log parsing), quy mô lớn hơn và gần log hệ thống thực tế hơn.

### 5.5. Áp dụng vào đề tài N4.7

Đề tài tập trung giám sát metric (CPU, RAM, disk, network) bằng Prometheus, chưa có pipeline log. Vì vậy ba bộ dữ liệu được dùng ở mức độ khác nhau.

#### NAB: dùng chính

Dữ liệu có sẵn nhãn, phù hợp thử luật phát hiện bất thường theo ngưỡng. Dùng để:

- Kiểm thử luật cảnh báo khi chỉ số (như CPU) vượt ngưỡng.
- Đánh giá khả năng phát hiện và thời điểm phát sinh cảnh báo.
- Kiểm tra cảnh báo giả khi dữ liệu biến động nhưng chưa thực sự bất thường (liên quan kịch bản S4).
- Đối chiếu kết quả với nhãn có sẵn.

Cách dùng: dữ liệu NAB là CSV ngoại tuyến, không tự đổ vào Prometheus. Có hai cách: đánh giá ngưỡng bằng script Python trên CSV, hoặc chuyển chuỗi sang `input_series` của `promtool test rules` để kiểm thử luật cảnh báo.

Cần chốt: NAB tập trung vào chuỗi hạ tầng trên cloud nên chưa chắc có đủ mọi chỉ số (ví dụ RAM). <!-- TODO tester: mở thư mục data/ và liệt kê tên các tệp sẽ dùng (CPU, disk, network...), bỏ chỉ số nào NAB không có. -->

#### Google Cluster Data: tham khảo

- Tham khảo hình dạng tải CPU, RAM và mức sử dụng theo thời gian.
- Tham khảo biến động tải giữa các job và task.
- Có thể lấy mẫu nhỏ để thử xử lý dữ liệu và biểu diễn xu hướng.

Do dung lượng lớn và cấu trúc phức tạp, không dùng toàn bộ trong demo. Đóng vai trò tham khảo cho thiết kế kịch bản kiểm thử tải.

#### Loghub: chỉ khảo sát

Dùng để tìm hiểu các dạng log hệ thống và khả năng phát hiện bất thường dựa trên log. Phạm vi hiện tại chưa có pipeline thu thập và phân tích log, nên Loghub không đưa vào demo thực nghiệm.

### 5.6. Quy ước lưu trữ dữ liệu trong repository

- **Vị trí:** dữ liệu thô nằm trong `data/raw/`, mỗi bộ một thư mục riêng (`google-cluster/`, `NAB/`, `loghub/`).
- **Git:** thêm `data/raw/` vào `.gitignore`, không commit tệp dữ liệu lớn.
- **Ghi nhận:** mỗi bộ ghi rõ nguồn tải, phiên bản, ngày tải (bảng bên dưới).
- **Chỉnh sửa:** giữ nguyên dữ liệu gốc. Nếu xử lý hoặc chỉnh sửa, ghi rõ nội dung và phương pháp.
- **Giấy phép:** với dữ liệu CC BY 4.0, ghi công nguồn, dẫn liên kết giấy phép và mô tả thay đổi đã thực hiện (nếu có).

Bảng ghi nhận (cập nhật khi tải thật):

| Bộ dữ liệu | Phiên bản | Nguồn | Ngày tải | Trạng thái kiểm thử |
|---|---|---|---|---|
| Google Cluster Data | V2 (2011) | `gs://clusterdata-2011-2` | chưa tải | chưa kiểm chứng |
| NAB | (ghi commit hoặc ngày) | github.com/numenta/NAB | chưa tải | chưa kiểm chứng |
| Loghub | (ghi tên bộ, ví dụ HDFS_v1) | zenodo.org/records/8196385 | chưa tải | chưa kiểm chứng |

### Tài liệu tham khảo

[1] Ahmad, S., Lavin, A., Purdy, S., & Agha, Z. (2017). Unsupervised real-time anomaly detection for streaming data. *Neurocomputing*, 262, 134-147. https://doi.org/10.1016/j.neucom.2017.04.070

[2] Zhu, J., He, S., He, P., Liu, J., & Lyu, M. R. (2023). Loghub: A Large Collection of System Log Datasets for AI-driven Log Analytics. *2023 IEEE 34th International Symposium on Software Reliability Engineering (ISSRE)*. https://doi.org/10.1109/ISSRE59848.2023.00071

[3] Jiang, Z., Liu, J., Huang, J., Li, Y., Huo, Y., Gu, J., Chen, Z., Zhu, J., & Lyu, M. R. (2024). A Large-scale Evaluation for Log Parsing Techniques: How Far are We? *ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA)*. https://doi.org/10.1145/3650212.3652123
