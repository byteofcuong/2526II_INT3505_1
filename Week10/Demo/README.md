# 🚀 Flask Task API: Observability, Security & Resiliency

## 📖 Tổng quan Dự án (Project Overview)
Đây là một RESTful API quản lý Danh sách công việc (Task List) được xây dựng bằng Python Flask. Điểm nhấn của dự án không chỉ nằm ở các tính năng CRUD cơ bản mà còn tập trung mạnh mẽ vào các yếu tố cốt lõi của một hệ thống Production-ready, bao gồm:
- **Service Operation & Resiliency**: Áp dụng pattern **Circuit Breaker** để ngăn chặn sụp đổ dây chuyền khi các external service gặp sự cố, cùng với cơ chế **Rate Limiting** bảo vệ tài nguyên máy chủ khỏi các cuộc tấn công lạm dụng (DDoS, Spam).
- **Monitoring & Observability**: Sử dụng **Prometheus** để đo lường các chỉ số RED (Rate, Error, Duration) và tích hợp **JSON Logging** có cấu trúc giúp việc phân tích và truy vết lỗi (tracing) dễ dàng hơn trên các hệ thống quản lý log tập trung.
- **Security**: Tăng cường bảo mật với **Flask-Talisman** nhằm tự động gán các HTTP Security Headers an toàn cho toàn bộ response để chống lại các lỗ hổng Web phổ biến.

---

## ⚙️ Yêu cầu & Cài đặt (Prerequisites & Setup)

Đảm bảo bạn đã cài đặt sẵn Python 3.x trên hệ thống. 

**Bước 1: Điều hướng đến thư mục dự án**
```bash
cd "d:\Direc of code\2526II_INT3505_1\Week10\Demo"
```

**Bước 2: Khởi tạo và kích hoạt môi trường ảo (Virtual Environment)**
```bash
python -m venv venv

# Dành cho Windows:
venv\Scripts\activate

# Dành cho macOS/Linux:
source venv/bin/activate
```

**Bước 3: Cài đặt các thư viện phụ thuộc**
```bash
pip install -r requirements.txt
```

**Bước 4: Khởi chạy Server**
```bash
python app.py
```
> Server sẽ lắng nghe tại địa chỉ: `http://127.0.0.1:5000/`

---

## 🧠 Giải phẫu Mã nguồn (Codebase Anatomy & Architecture)

Dự án này được thiết kế để minh họa các Pattern và Best Practices trong việc xây dựng một hệ thống Backend thực tế. Dưới đây là giải thích chi tiết về các thành phần cốt lõi được lập trình trong `app.py`:

### 1. API & Cấu trúc Dữ liệu
- **Vị trí trong code**: Các decorator `@app.route(...)` (từ dòng 123 đến 195) và biến `tasks = []` (dòng 106).
- **Ý nghĩa & Triển khai**: Ứng dụng cung cấp các RESTful endpoint chuẩn hóa để thực hiện thao tác CRUD (Create, Read, Update, Delete) trên thực thể `Task`. Dữ liệu hiện được lưu trữ trên RAM (In-memory) thông qua một list Python đơn giản nhằm mục đích đơn giản hóa việc demo. Mỗi Task có `id` tự tăng, `title` và trạng thái `completed`.

### 2. Monitoring: Structured JSON Logs
- **Vị trí trong code**: Class `JSONFormatter` (dòng 13) và phần cấu hình `logger` (dòng 90 - 103).
- **Ý nghĩa & Triển khai**: Thay vì in log dưới dạng văn bản thuần túy (plain-text) khó đọc cho máy tính, dự án kế thừa `logging.Formatter` để chuyển đổi mọi log thành chuỗi JSON. Điều này cực kỳ quan trọng trên Production. Các công cụ như ElasticSearch, Datadog hay CloudWatch có thể dễ dàng phân tích cấu trúc JSON để tìm kiếm, lọc (filter) theo `level` (INFO, ERROR), `method` (GET, POST), và theo dõi luồng request (Tracing).

### 3. Monitoring: Prometheus Metrics (RED)
- **Vị trí trong code**: Các biến `REQUEST_COUNT`, `REQUEST_LATENCY` (dòng 48 - 57) và Middleware `@app.before_request`, `@app.after_request` (dòng 109 - 121).
- **Ý nghĩa & Triển khai**: Áp dụng phương pháp luận RED (Rate - Error - Duration) để đo lường "sức khỏe" API:
  - Sử dụng `Counter` để đếm tổng số request và phân loại theo status_code (Rate & Error).
  - Sử dụng `Histogram` để đo thời gian phản hồi (Duration/Latency) của từng endpoint.
  - Các chỉ số này được middleware tự động ghi nhận sau mỗi request và expose ra ở endpoint `/metrics`. Các hệ thống cảnh báo (Alerting) có thể dựa vào dữ liệu này để báo động nếu Error Rate tăng cao hoặc Latency chậm đột biến.

### 4. Rate Limiting (Giới hạn lưu lượng)
- **Vị trí trong code**: Khởi tạo `limiter = Limiter(...)` (dòng 40) và decorator `@limiter.limit("5 per minute")` trên các route POST/DELETE.
- **Ý nghĩa & Triển khai**: Bảo vệ hệ thống khỏi các hành vi DDoS hoặc Spam dữ liệu. Nếu một địa chỉ IP gọi API vượt quá số lần cho phép trong một khoảng thời gian, server sẽ từ chối xử lý và trả về mã lỗi HTTP `429 Too Many Requests`.

### 5. Circuit Breaker (Ngắt mạch tự động)
- **Vị trí trong code**: Class `CircuitBreaker` (dòng 60 - 88) và endpoint `/external` (dòng 204).
- **Ý nghĩa & Triển khai**: Khi API của chúng ta gọi đến một dịch vụ bên ngoài (External Service) và dịch vụ đó đang bị chậm hoặc sập, nó có thể làm "treo" (hang) toàn bộ hệ thống của chúng ta vì phải chờ timeout. 
  - `Circuit Breaker` đóng vai trò như một cầu chì: Nếu phát hiện dịch vụ ngoài lỗi liên tục (vượt quá `failure_threshold`), nó sẽ "Ngắt mạch" (trạng thái OPEN) và lập tức từ chối mọi request tiếp theo, giúp giải phóng tài nguyên.
  - Sau một thời gian (`recovery_timeout`), nó chuyển sang trạng thái HALF_OPEN để thử gọi lại dịch vụ. Nếu thành công, mạch đóng lại (CLOSED) và hệ thống trở lại bình thường.

### 6. Security (Bảo mật Headers)
- **Vị trí trong code**: `Talisman(app, ...)` (dòng 37).
- **Ý nghĩa & Triển khai**: Sử dụng thư viện Flask-Talisman để tự động chèn các HTTP Security Headers chuẩn mực (như CSP, X-Frame-Options) vào mọi Response. Việc này giúp giảm thiểu rủi ro từ các cuộc tấn công phía Client như XSS hoặc Clickjacking.

---

## 🗂️ Tài liệu API (API Documentation)

Dưới đây là danh sách các endpoints cốt lõi và các endpoints phục vụ vận hành:

| Phương thức | Đường dẫn (Endpoint) | Chức năng | Giới hạn (Rate Limit) |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Kiểm tra trạng thái sống còn (Health Check) của API | Không |
| `GET` | `/metrics` | Expose dữ liệu Monitoring cho hệ thống Prometheus | Không |
| `GET` | `/external` | Giả lập gọi dịch vụ bên ngoài để test Circuit Breaker | Không |
| `GET` | `/tasks` | Truy xuất toàn bộ danh sách Task | Không |
| `POST` | `/tasks` | Tạo mới một Task vào hệ thống | **5 requests / phút** |
| `GET` | `/tasks/<id>` | Truy xuất thông tin chi tiết một Task | Không |
| `PUT` | `/tasks/<id>` | Cập nhật thông tin một Task đã tồn tại | Không |
| `DELETE` | `/tasks/<id>` | Xóa bỏ một Task | **5 requests / phút** |

---

## 🛠️ Hướng dẫn Vận hành & Demo (Operational Demo Guide)

Phần này hướng dẫn bạn cách sử dụng công cụ **Postman** để kích hoạt và quan sát các tính năng nâng cao của API.

### 1. Quan sát Log có cấu trúc (Observe Logs)
Mọi request gửi tới server đều được ghi nhận lại trên cửa sổ terminal đang chạy `app.py` dưới định dạng JSON. Điều này giúp các công cụ thu thập log (như ELK stack, Fluentd, CloudWatch) dễ dàng parse và phân tích tự động.

**Cách test bằng Postman:** 
1. Mở Postman, tạo một Request mới.
2. Chọn method **GET**.
3. Nhập URL: `http://127.0.0.1:5000/tasks`
4. Bấm **Send**.
**Kết quả hiển thị trên terminal của server (nơi chạy python app.py):**
```json
{"timestamp": "2026-05-14T12:00:00+00:00", "level": "INFO", "message": "Handling request", "method": "GET", "path": "/tasks"}
```
> *Lưu ý: Các trường `timestamp`, `level`, `method`, và `path` được cấu trúc hóa rõ ràng để giúp kỹ sư hệ thống nắm được ngữ cảnh chính xác của từng request.*

### 2. Kiểm thử Giới hạn Request (Test Rate Limiting)
Các endpoints `POST /tasks` và `DELETE /tasks/<id>` được bảo vệ bằng Flask-Limiter, cho phép tối đa 5 requests/phút từ cùng một địa chỉ IP nhằm tránh việc spam dữ liệu.

**Cách test bằng Postman:** 
1. Tạo một Request mới trong Postman.
2. Chọn method **POST**.
3. Nhập URL: `http://127.0.0.1:5000/tasks`
4. Chuyển sang tab **Body**, chọn **raw** và định dạng **JSON**.
5. Nhập nội dung:
   ```json
   {
       "title": "Spam Task"
   }
   ```
6. Bấm nút **Send** liên tục **hơn 5 lần** một cách nhanh chóng.
**Kết quả nhận được ở lần thứ 6:**
Bạn sẽ bị chặn lại và nhận HTTP Status Code `429 Too Many Requests` với nội dung thông báo cho biết bạn đã vượt qua giới hạn cho phép.

### 3. Giám sát các Chỉ số RED (Monitor Metrics)
Hệ thống sử dụng thư viện `prometheus_client` để liên tục thu thập và phơi bày (expose) các số liệu hiệu suất tại endpoint `/metrics`.

**Cách test bằng Postman:**
1. Tạo một Request mới.
2. Chọn method **GET**.
3. Nhập URL: `http://127.0.0.1:5000/metrics`
4. Bấm **Send** và xem dữ liệu văn bản trả về trong tab Body.
**Ý nghĩa các chỉ số RED hiển thị trong output:**
- **Rate (Tần suất):** Bộ đếm `request_total` cho biết tổng số lượng request API đã tiếp nhận, được gán nhãn theo từng `method` (GET/POST), `endpoint` và `http_status`.
- **Errors (Lỗi):** Căn cứ theo `request_total`, hệ thống Prometheus có thể gom nhóm các nhãn `http_status` >= 400 (như 404, 429, 503) để vẽ biểu đồ và kích hoạt chuông cảnh báo lỗi tự động.
- **Duration (Thời lượng):** Biểu đồ Histogram `request_latency_seconds` liên tục đo lường độ trễ (thời gian xử lý request), giúp bạn biết API đang có độ phản hồi trung bình (latency) nhanh hay chậm.

### 4. Kích hoạt Ngắt mạch (Trigger Circuit Breaker)
Endpoint `/external` gọi một hàm giả lập dịch vụ của đối tác bên ngoài. Hàm này được thiết lập để trả về Exception một cách ngẫu nhiên (tỉ lệ lỗi 50%). Nếu dịch vụ lỗi liên tiếp 3 lần, Circuit Breaker sẽ tự động ngắt mạch (chuyển sang trạng thái **OPEN**).

**Cách test bằng Postman:** 
1. Tạo một Request mới.
2. Chọn method **GET**.
3. Nhập URL: `http://127.0.0.1:5000/external`
4. Bấm **Send** nhiều lần để quan sát sự thay đổi trạng thái mạch và HTTP Status Code nhận được.
**Chu kỳ hoạt động của Circuit Breaker:**
- **CLOSED (Bình thường):** Mạch đóng, hệ thống hoạt động ổn định.
- **OPEN (Ngắt mạch):** Khi dịch vụ lỗi đủ 3 lần, mạch sẽ **OPEN**. Ngay lúc này, bất kỳ request nào gửi tới `/external` cũng lập tức bị từ chối với HTTP Code `503 Service Unavailable` và thông báo `"Circuit is OPEN"`. Việc ngắt mạch giúp hệ thống chính không bị nghẽn (hang) khi chờ đợi một dịch vụ đang sập.
- **HALF_OPEN (Thử nghiệm lại):** Sau khoảng thời gian Recovery Timeout (10 giây), mạch sẽ chuyển sang `"HALF_OPEN"` cho phép 1 request đi qua để "thăm dò" xem dịch vụ bên ngoài đã khôi phục chưa.

### 5. Ghi chú về Bảo mật (Security Note)
Bảo mật Headers đóng vai trò then chốt trong việc bảo vệ API. Dự án sử dụng thư viện **Flask-Talisman** để làm việc này một cách tự động.

Flask-Talisman sẽ chèn thêm các HTTP Security Headers vào mọi Response trả về cho Client. Nó đóng vai trò bảo vệ hệ thống khỏi:
- **XSS (Cross-Site Scripting)** thông qua header `Content-Security-Policy`.
- **Clickjacking** thông qua `X-Frame-Options`.
- **MIME Sniffing** thông qua `X-Content-Type-Options`.
Điều này đảm bảo API luôn đạt chuẩn bảo mật ngay từ lớp mạng HTTP mà không đòi hỏi lập trình viên cấu hình phức tạp trên từng endpoint.
