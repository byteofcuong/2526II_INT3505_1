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

Phần này hướng dẫn bạn cách sử dụng công cụ `curl` (chạy trên Command Prompt, PowerShell, hoặc Terminal) để kích hoạt và quan sát các tính năng nâng cao của API.

### 1. Quan sát Log có cấu trúc (Observe Logs)
Mọi request gửi tới server đều được ghi nhận lại trên cửa sổ terminal đang chạy `app.py` dưới định dạng JSON. Điều này giúp các công cụ thu thập log (như ELK stack, Fluentd, CloudWatch) dễ dàng parse và phân tích tự động.

**Cách test:** Mở một cửa sổ dòng lệnh khác (terminal mới) và chạy:
```bash
curl -X GET http://127.0.0.1:5000/tasks
```
**Kết quả hiển thị trên terminal của server (nơi chạy python app.py):**
```json
{"timestamp": "2026-05-14T12:00:00+00:00", "level": "INFO", "message": "Handling request", "method": "GET", "path": "/tasks"}
```
> *Lưu ý: Các trường `timestamp`, `level`, `method`, và `path` được cấu trúc hóa rõ ràng để giúp kỹ sư hệ thống nắm được ngữ cảnh chính xác của từng request.*

### 2. Kiểm thử Giới hạn Request (Test Rate Limiting)
Các endpoints `POST /tasks` và `DELETE /tasks/<id>` được bảo vệ bằng Flask-Limiter, cho phép tối đa 5 requests/phút từ cùng một địa chỉ IP nhằm tránh việc spam dữ liệu.

**Cách test:** Chạy lệnh sau đây liên tục **hơn 5 lần** một cách nhanh chóng:
```bash
curl -X POST http://127.0.0.1:5000/tasks -H "Content-Type: application/json" -d "{\"title\": \"Spam Task\"}"
```
**Kết quả nhận được ở lần thứ 6:**
Bạn sẽ bị chặn lại và nhận HTTP Status Code `429 Too Many Requests` với nội dung thông báo cho biết bạn đã vượt qua giới hạn cho phép.

### 3. Giám sát các Chỉ số RED (Monitor Metrics)
Hệ thống sử dụng thư viện `prometheus_client` để liên tục thu thập và phơi bày (expose) các số liệu hiệu suất tại endpoint `/metrics`.

**Cách test:**
```bash
curl -X GET http://127.0.0.1:5000/metrics
```
**Ý nghĩa các chỉ số RED hiển thị trong output:**
- **Rate (Tần suất):** Bộ đếm `request_total` cho biết tổng số lượng request API đã tiếp nhận, được gán nhãn theo từng `method` (GET/POST), `endpoint` và `http_status`.
- **Errors (Lỗi):** Căn cứ theo `request_total`, hệ thống Prometheus có thể gom nhóm các nhãn `http_status` >= 400 (như 404, 429, 503) để vẽ biểu đồ và kích hoạt chuông cảnh báo lỗi tự động.
- **Duration (Thời lượng):** Biểu đồ Histogram `request_latency_seconds` liên tục đo lường độ trễ (thời gian xử lý request), giúp bạn biết API đang có độ phản hồi trung bình (latency) nhanh hay chậm.

### 4. Kích hoạt Ngắt mạch (Trigger Circuit Breaker)
Endpoint `/external` gọi một hàm giả lập dịch vụ của đối tác bên ngoài. Hàm này được thiết lập để trả về Exception một cách ngẫu nhiên (tỉ lệ lỗi 50%). Nếu dịch vụ lỗi liên tiếp 3 lần, Circuit Breaker sẽ tự động ngắt mạch (chuyển sang trạng thái **OPEN**).

**Cách test:** Chạy lệnh dưới đây nhiều lần để quan sát sự thay đổi trạng thái mạch:
```bash
curl -X GET http://127.0.0.1:5000/external
```
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
