# N4.7 – Hệ thống giám sát máy chủ, Cloud và trung tâm dữ liệu (prototype)

Prototype giám sát chạy trong môi trường lab kiểm soát: thu thập metric CPU, RAM, disk, network, uptime và tình trạng endpoint; hiển thị trên dashboard; phát cảnh báo khi vượt ngưỡng; mô phỏng lỗi và đo thời gian phát hiện (MTTD).

Đề tài thuộc nhóm N4 – Mạng, IoT và hạ tầng số, thời gian thực hiện 18 tuần (01/11/2026 – 06/03/2027). Đây là bản minh họa vận hành theo hướng cloud-native, **không thay thế NOC/DCIM chính thức**.
# n47-monitoring

Prototype hệ thống giám sát máy chủ/dịch vụ lab (Prometheus, Grafana, Alertmanager) cho đề tài N4.7, chạy bằng Docker Compose trong môi trường thử nghiệm có kiểm soát. Không kết nối hệ thống thật và không dùng credential sản xuất.

## Quy ước Git

Áp dụng cho cả 6 thành viên. Nếu cần đổi quy ước, sửa mục này bằng một pull request và được Team Leader duyệt.

### 1. Nhánh

- `main` luôn ở trạng thái chạy được (`docker compose up -d` thành công). **Không commit trực tiếp vào `main`.**
- Mỗi việc làm trên một nhánh riêng, tách từ `main`, đặt tên theo mẫu `loại/mảng-mô-tả-ngắn`, chữ thường, không dấu, nối bằng dấu gạch ngang:

| Loại | Dùng khi | Ví dụ |
| --- | --- | --- |
| `feat` | thêm tính năng, cấu hình, luật mới | `feat/infra-cadvisor` |
| `fix` | sửa lỗi | `fix/alert-cpu-for` |
| `docs` | chỉ sửa tài liệu | `docs/runbook-cpu` |
| `test` | thêm hoặc sửa test, kịch bản | `test/scenario-s1-cpu` |
| `chore` | việc lặt vặt (CI, dọn repo, .gitignore) | `chore/ci-promtool` |

- Mảng là một trong: `infra`, `alert`, `backend`, `frontend`, `scenario`, `docs`.
- Nhánh sống ngắn: làm xong thì gộp và xóa, không để nhánh treo quá một tuần.

### 2. Commit

Dùng dạng `loại(phạm-vi): mô tả`:

```
feat(infra): thêm cAdvisor vào docker-compose
fix(alert): tăng for của luật CPU cao lên 5m
docs(runbook): thêm cách phân biệt cảnh báo giả
test(scenario): thêm s3_service_down.sh
chore(ci): chạy promtool check rules trong GitHub Actions
```

- Loại giống bảng nhánh ở trên. Phạm-vi là mảng hoặc thư mục: `infra`, `alert`, `backend`, `frontend`, `scenario`, `docs`, `ci`.
- Dòng mô tả ngắn gọn (khoảng 72 ký tự), viết ở dạng mệnh lệnh, không kết thúc bằng dấu chấm.
- Mỗi commit chỉ làm một việc. Không gộp việc không liên quan vào cùng một commit.
- Nếu có thêm ngữ cảnh, để một dòng trống rồi viết thân commit giải thích **vì sao** thay đổi.
- Ghi ID task trong thân commit hoặc trong pull request, ví dụ `Task: T08`.

### 3. Pull request

1. Trước khi mở PR: `git fetch` rồi cập nhật nhánh theo `main` (`git rebase origin/main`), sau đó tự đọc lại diff.
2. Mỗi PR một việc, nhỏ vừa đủ để review trong 15–20 phút. Tiêu đề theo cùng dạng như commit.
3. Mô tả PR gồm: làm gì, vì sao, liên quan task nào (`T..`), cách kiểm tra, ảnh chụp nếu là dashboard hoặc giao diện.
4. Cần **ít nhất 1 người review** không phải tác giả. Người review xem cả mục "Bảo mật" bên dưới.
5. Khi đã có CI (từ tuần 7), PR chỉ được gộp khi CI xanh.
6. Gộp bằng **Squash and merge**, sau đó xóa nhánh.
7. Người tạo PR tự gộp sau khi được duyệt. Team Leader gộp thay khi cần.
8. Nếu repo cho phép, bật branch protection cho `main` (bắt buộc PR, bắt buộc review, cấm force-push).

### 4. Kiểm tra trước khi commit

- Luật cảnh báo: `promtool check rules infra/prometheus/rules/*.yml`
- Cấu hình Alertmanager: `amtool check-config infra/alertmanager/alertmanager.yml`
- Backend: `pytest`
- Frontend: `npm run lint` và `npm test`
- Dashboard Grafana: export JSON rồi commit, không sửa tay file JSON trừ khi hiểu rõ.

### 5. Bảo mật và dữ liệu (bắt buộc)

- **Không commit** mật khẩu, token, khóa riêng, file `.env`. Chỉ commit `.env.example` với giá trị giả.
- **Không commit** địa chỉ IP, tên hệ thống, log truy cập hoặc sơ đồ trung tâm dữ liệu của VNPT. Dữ liệu trong `data/` chỉ là dữ liệu public hoặc giả lập.
- Không commit file lớn hoặc file sinh ra: `*.db`, `node_modules/`, volume dữ liệu Prometheus, video. Video và ảnh lưu ở thư mục hồ sơ tập trung, trong repo chỉ để đường dẫn.
- Nếu lỡ commit thông tin nhạy cảm: **báo Team Leader ngay**, đổi giá trị bí mật đó, rồi mới xử lý lịch sử Git. Chỉ xóa file ở commit sau thì chưa đủ.
- Repo được rà soát credential ở tuần 13 và tuần 18.

### 6. Tag và phát hành

| Tag | Mốc | Tuần |
| --- | --- | --- |
| `v0.1-prototype` | prototype chạy end-to-end | 8 |
| `v0.9-beta` | trước báo cáo tháng #3 | 12 |
| `v1.0-rc` | từ đây chỉ sửa lỗi, không thêm tính năng | 16 |
| `v1.0` | bản bàn giao | 18 |

Chỉ Team Leader gắn tag, trên `main`: `git tag -a v0.1-prototype -m "Prototype end-to-end"` rồi `git push --tags`.

### 7. Issue

- Mỗi lỗi hoặc đề xuất là một issue, có nhãn theo mảng và gắn người phụ trách.
- Phản hồi từ đánh giá chéo (tuần 9) phân loại thành: **sửa ngay**, **backlog**, **không nhận** (ghi lý do).
- Đóng issue bằng cách ghi `Closes #số` trong PR.

### 8. Một số điều cần tránh

- Không `git push --force` lên `main`.
- Không sửa lịch sử đã đẩy lên (rebase hoặc amend) trên nhánh người khác đang dùng.
- Không để nhánh chứa việc dở dang được gộp vào `main`. Việc chưa xong thì mở PR dạng draft.
## Hệ thống gồm những gì

| Thành phần | Vai trò |
| --- | --- |
| Prometheus | Thu thập metric (scrape 15 giây), chấm luật cảnh báo |
| Node Exporter | Metric của host: CPU, RAM, disk, network, uptime |
| cAdvisor | Metric theo từng container |
| Blackbox Exporter | Thăm dò endpoint (`probe_success`, thời gian phản hồi) |
| Alertmanager | Gom nhóm cảnh báo, gửi webhook về backend |
| Grafana | Dashboard theo host/service, nạp tự động từ file trong Git |
| backend (Python, FastAPI) | Nhận webhook, ghi thí nghiệm, tính MTTD |
| frontend (TypeScript, React) | Console 4 màn hình: thí nghiệm, lịch sử cảnh báo, kết quả MTTD, trạng thái target |
| demo-app | Dịch vụ mô phỏng làm mục tiêu cho kịch bản lỗi |

```mermaid
flowchart LR
  T["demo-app, node-exporter, cAdvisor, blackbox"] -->|"scrape"| P[Prometheus]
  P -->|"cảnh báo"| A[Alertmanager]
  A -->|"webhook"| B["backend FastAPI"]
  G[Grafana] -->|"PromQL"| P
  B -->|"REST API"| F["frontend React"]
  S["scenarios/*.sh"] -->|"gây lỗi trên host"| T
  S -->|"ghi mốc thí nghiệm"| B
```

## Cấu trúc thư mục

```text
infra/        Cấu hình Prometheus, Alertmanager, Blackbox, Grafana (dashboard + provisioning)
backend/      API FastAPI, nhận webhook, tính MTTD
frontend/     Console React + TypeScript
demo-app/     Dịch vụ mô phỏng (/health, /work, /metrics)
scenarios/    Kịch bản lỗi S1 đến S4 và thư mục results/
scripts/      Script hỗ trợ (đĩa loop cho kịch bản disk đầy)
data/         Hướng dẫn tải dữ liệu NAB, Google Cluster Data, Loghub (không commit dữ liệu)
docs/         Kiến trúc, hướng dẫn dựng lại, runbook, báo cáo kiểm thử, quyết định thiết kế
```

## Yêu cầu

- Ubuntu 22.04 hoặc 24.04 (VM hoặc máy thật), tối thiểu 4 vCPU, 8 GB RAM, 30 GB disk.
- Docker Engine và Docker Compose plugin, Git, `make`, `curl`, `jq`, `stress-ng`, `chrony`.
- Docker Desktop trên Windows/macOS chạy Linux VM ẩn nên Node Exporter chỉ đo máy ảo đó, không phải máy thật. Khi demo hãy dùng Ubuntu thật.

## Dựng lab trong 5 bước

### Bước 1. Chuẩn bị máy và tải mã nguồn

```bash
sudo apt update && sudo apt install -y git make curl jq stress-ng chrony
docker --version && docker compose version    # cài Docker theo hướng dẫn chính thức nếu chưa có

git clone <địa-chỉ-repo> n47-monitoring
cd n47-monitoring
```

### Bước 2. Cấu hình môi trường

```bash
cp .env.example .env
```

Mở `.env`, đổi `GRAFANA_ADMIN_PASSWORD`. Các biến `*_VERSION` ghim phiên bản image; không dùng `latest`. Nếu một tag không kéo về được, chọn bản ổn định gần nhất trên Docker Hub rồi ghi lại trong `.env`. Không commit file `.env` và không dùng credential sản xuất.

### Bước 3. Tạo đĩa loop cho kịch bản disk đầy

```bash
bash scripts/make-loop-disk.sh      # tạo và mount đĩa 1 GB tại /mnt/labdisk
df -h /mnt/labdisk
```

Làm bước này trước khi khởi động lab để Node Exporter thấy phân vùng. Mount không giữ sau khi khởi động lại máy; khi đó chạy `sudo mount -o loop /var/lib/labdisk.img /mnt/labdisk` rồi `docker compose restart node-exporter`.

### Bước 4. Kiểm tra cấu hình và khởi động

```bash
make lint-infra     # promtool check config, promtool test rules, amtool check-config
make up             # docker compose up -d --build
docker compose ps
```

`make lint-infra` phải báo SUCCESS cho cả ba lệnh trước khi khởi động.

### Bước 5. Kiểm tra lab và chạy thử một kịch bản

Mở các địa chỉ sau (các cổng chỉ bind `127.0.0.1`; xem từ máy khác thì dùng SSH tunnel):

| Dịch vụ | Địa chỉ | Kiểm tra |
| --- | --- | --- |
| Prometheus | http://localhost:9090/targets | Mọi target ở trạng thái UP |
| Grafana | http://localhost:3000 | Đăng nhập `admin` và mật khẩu trong `.env`; thư mục N4.7 có 3 dashboard |
| Alertmanager | http://localhost:9093 | Mở được, chưa có cảnh báo đang bật |
| Backend | http://localhost:8000/docs | Hiển thị API |
| Console | http://localhost:8080 | Mở được 4 màn hình |

Chạy thử kịch bản service down (khoảng 2 phút):

```bash
bash scenarios/03_service_down.sh
```

Kết quả đúng: cảnh báo `ServiceDown` hiện ở Alertmanager trong khoảng một phút, xuất hiện ở `GET /api/alerts`, rồi chuyển resolved khi demo-app chạy lại. Xem thời gian phát hiện tại `GET /api/experiments`.

## Kịch bản lỗi

| ID | Kịch bản | Lệnh | Cảnh báo kỳ vọng |
| --- | --- | --- | --- |
| S1 | CPU cao | `bash scenarios/01_cpu_high.sh` | HostHighCpu |
| S2 | Disk đầy giả lập | `bash scenarios/02_disk_full.sh` | HostDiskAlmostFull |
| S3 | Service down | `bash scenarios/03_service_down.sh` | ServiceDown |
| S4 | Spike ngắn (cảnh báo giả) | `bash scenarios/04_short_spike.sh` | Không có cảnh báo nào |

Chạy mỗi kịch bản từ thư mục gốc của repo. Trước khi đo MTTD, kiểm tra đồng hồ đồng bộ bằng `chronyc tracking`. Lưu kết quả vào `scenarios/results/`. Ngưỡng cảnh báo trong `infra/prometheus/rules/` là giá trị khởi đầu, hiệu chỉnh sau khi đo baseline.

## Dừng và dọn lab

```bash
make down                       # dừng các container, giữ dữ liệu
docker compose down -v          # dừng và xóa cả dữ liệu Prometheus, Grafana, backend
```

## Xử lý lỗi thường gặp

- **Target `node` DOWN:** kiểm tra `curl localhost:9100/metrics` trên host, tường lửa, và mục `extra_hosts` của dịch vụ prometheus.
- **Không thấy `/mnt/labdisk` trong metric disk:** đĩa loop chưa được mount, hoặc mount sau khi Node Exporter chạy; chạy `docker compose restart node-exporter`.
- **cAdvisor không có nhãn `name`:** thiếu `privileged` hoặc mount `/var/lib/docker`.
- **Backend không nhận cảnh báo:** xem `docker compose logs alertmanager backend` và kiểm tra URL webhook.

## Phạm vi và an toàn

- Chỉ chạy trên lab do nhóm quản lý. Không kết nối nền tảng quản trị trung tâm dữ liệu thật khi chưa có phân quyền và phê duyệt an toàn thông tin.
- Node Exporter và cAdvisor chạy với quyền cao (mount `/`, `privileged`). Không dùng cấu hình này cho môi trường thật. Cổng 9100 của Node Exporter mở trên mọi interface, hãy chặn từ bên ngoài bằng `ufw`.
- Grafana bật truy cập ẩn danh (chỉ xem) để nhúng panel; chỉ dùng trong lab.
- Không đưa IP, tên hệ thống, log truy cập hoặc sơ đồ trung tâm dữ liệu thật vào repo. Dữ liệu VNPT chỉ dùng khi đã được phê duyệt và đã tổng hợp.

## Tài liệu thêm

- `docs/architecture.md`: sơ đồ kiến trúc
- `docs/setup-guide.md`: hướng dẫn dựng lại lab chi tiết
- `docs/runbooks/`: runbook xử lý từng cảnh báo
- `docs/test-report.md`: kết quả kiểm thử và MTTD
