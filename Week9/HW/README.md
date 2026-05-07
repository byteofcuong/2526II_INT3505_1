# Hướng dẫn Kiểm tra (Testing) Các Chiến lược Versioning API

Dự án này triển khai 4 phương pháp quản lý phiên bản API (API Versioning) khác nhau. Mặc dù kết quả dữ liệu trả về giống nhau, nhưng **cách client truyền yêu cầu** và **cách server phản hồi (headers)** là hoàn toàn khác biệt.

## Cài đặt chung
Mở terminal tại thư mục này và cài đặt Flask nếu chưa có:
```bash
pip install flask
```

---

## 1. URI Path Versioning (Dễ test nhất)
Phiên bản được nhúng trực tiếp vào URL (vd: `/api/v1/users`).
- **Khởi động server:** `python uri_path_versioning.py` (Chạy ở Port `5001`)

### Cách Test:
Phương pháp này **rất dễ test trực tiếp trên Trình duyệt web**.
- **Trình duyệt (Browser):**
  - Mở Chrome/Edge, nhập: `http://localhost:5001/api/v1/users` (Để xem V1)
  - Nhập: `http://localhost:5001/api/v2/users` (Để xem V2)
- **CURL:**
  ```bash
  curl http://localhost:5001/api/v1/users
  curl http://localhost:5001/api/v2/users
  ```

---

## 2. Query Parameter Versioning
Phiên bản được truyền qua dấu `?` trên URL.
- **Khởi động server:** `python query_param_versioning.py` (Chạy ở Port `5002`)

### Cách Test:
Phương pháp này cũng **dễ dàng test trên Trình duyệt web**.
- **Trình duyệt (Browser):**
  - Mở Chrome/Edge, nhập: `http://localhost:5002/api/users` (Mặc định sẽ gọi V1)
  - Nhập: `http://localhost:5002/api/users?version=2` (Để gọi V2)
- **CURL:**
  ```bash
  curl "http://localhost:5002/api/users?version=1"
  curl "http://localhost:5002/api/users?version=2"
  ```

---

## 3. Custom Header Versioning (Cần công cụ chuyên dụng)
URL được giữ nguyên (`/api/users`). Phiên bản được gửi giấu kín bên trong HTTP Header `X-API-Version`.
- **Khởi động server:** `python custom_header_versioning.py` (Chạy ở Port `5003`)

### Cách Test:
Bạn **KHÔNG THỂ test phương pháp này bằng cách gõ URL vào trình duyệt**, vì trình duyệt không cho phép bạn sửa Custom Headers khi gõ thanh địa chỉ. Bắt buộc dùng Postman hoặc CURL.

- **Dùng Postman:**
  1. Tạo request `GET` đến `http://localhost:5003/api/users`
  2. Chuyển sang tab **Headers**.
  3. Thêm Key: `X-API-Version`, Value: `1` (hoặc `2`).
  4. Bấm Send.

- **CURL:**
  ```bash
  # Test V1
  curl -H "X-API-Version: 1" http://localhost:5003/api/users
  
  # Test V2
  curl -H "X-API-Version: 2" http://localhost:5003/api/users
  ```

---

## 4. Media Type (Content Negotiation) - Chuẩn RESTful nhất
URL được giữ nguyên (`/api/users`). Client dùng Header chuẩn `Accept` để "đàm phán" định dạng với Server. Server cũng phải trả về đúng định dạng đó trong Header `Content-Type`.
- **Khởi động server:** `python media_type_versioning.py` (Chạy ở Port `5004`)

### Cách Test:
Tương tự Custom Header, bạn **KHÔNG THỂ test trên thanh địa chỉ trình duyệt**.

- **Dùng Postman (Quan trọng: Phải kiểm tra cả Request lẫn Response Header):**
  1. Tạo request `GET` đến `http://localhost:5004/api/users`
  2. Mở tab **Headers** (của Request), thêm Key: `Accept`, Value: `application/vnd.company.v2+json`.
  3. Bấm Send.
  4. **Quan sát sự khác biệt:** Sau khi nhận kết quả, hãy nhìn xuống phần **Headers của Response** (khung dưới cùng của Postman). Bạn sẽ thấy server trả về `Content-Type: application/vnd.company.v2+json` và `Vary: Accept`. Điều này chứng tỏ server đã thực sự tuân thủ chuẩn Content Negotiation!

- **CURL:**
  Sử dụng cờ `-i` để in ra cả Headers phản hồi từ Server nhằm thấy rõ sự khác biệt.
  ```bash
  # Test V1 (In ra Headers)
  curl -i -H "Accept: application/vnd.company.v1+json" http://localhost:5004/api/users
  
  # Test V2 (In ra Headers)
  curl -i -H "Accept: application/vnd.company.v2+json" http://localhost:5004/api/users
  ```
  *Trong Terminal, bạn sẽ thấy dòng `Content-Type: application/vnd.company.v2+json` xuất hiện trước phần dữ liệu JSON.*
