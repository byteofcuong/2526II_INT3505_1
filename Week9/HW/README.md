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

---

## 5. Giải pháp Kiến trúc: Parallel Running (Chạy Song Song)
Thay vì dùng `if/else` để sửa đè mã nguồn cũ hoặc dùng chung một API Server, chúng ta tách V1 và V2 ra thành các tiến trình (process) hoặc server hoàn toàn độc lập.
Điều này giúp đảm bảo:
- **Zero Churn**: Khách hàng cũ không bị ép nâng cấp, code V1 chạy ổn định không lo bị ảnh hưởng bởi lỗi của V2.
- **Sandbox**: V2 thoải mái dùng công nghệ mới, database mới, cấu trúc mới.
- **Monitoring**: Dễ dàng theo dõi server V1 còn ai dùng không để tắt.

Mình đã chuẩn bị sẵn **2 cách thực hiện** Parallel cho bạn:

### Cách A: Parallel Vật Lý (Microservices + API Gateway)
Cách này là đúng chuẩn "Parallel" thực tế nhất ở quy mô lớn.
1. Mở Terminal 1 và chạy V1: `python parallel_v1_app.py` (Port 5011)
2. Mở Terminal 2 và chạy V2: `python parallel_v2_app.py` (Port 5012)
3. Mở Terminal 3 và chạy Gateway: `python parallel_gateway.py` (Port 5010)

**Cách Test (Chỉ cần gọi vào cổng 5010 của Gateway):**
- V1: `curl http://localhost:5010/api/v1/users`
- V2: `curl http://localhost:5010/api/v2/users`
*(Gateway sẽ tự động định tuyến ngầm request đến server tương ứng)*

### Cách B: Parallel Logic (Dùng Flask Blueprint)
Nếu dự án nhỏ, không muốn mở 3 terminal, bạn có thể gom V1 và V2 chạy trên cùng 1 server nhưng được cách ly mã nguồn hoàn toàn bằng **Blueprint**.
- **Khởi động server:** `python parallel_blueprint.py` (Chạy ở Port 5013)

**Cách Test:**
- V1: `curl http://localhost:5013/api/v1/users`
- V2: `curl http://localhost:5013/api/v2/users`

---

## 6. Giải pháp Kiến trúc: Adapter (Contract Bridge)
Thay vì duy trì cả 2 bộ mã nguồn cho V1 và V2 (dễ dẫn đến lặp code, lặp logic, bug gấp đôi), chúng ta chỉ duy trì **Core Logic duy nhất theo chuẩn V2**.
V1 lúc này chỉ đóng vai trò như một "Adapter" hoặc "Cái Cầu (Bridge)":
1. V1 nhận Request từ Client cũ.
2. V1 gọi Core Logic (V2).
3. Core Logic trả về dữ liệu phức tạp của V2.
4. V1 **hạ cấp / cắt gọt (downgrade)** dữ liệu đó xuống cho đúng với cấu trúc đơn giản ngày xưa mà Client cũ mong đợi.

Điều này giúp hệ thống luôn giữ được nguyên tắc **Single Source of Truth** (Chỉ có một luồng sự thật) nhưng vẫn không phá vỡ hợp đồng (Contract) với khách hàng cũ.

- **Khởi động server:** `python adapter_bridge_versioning.py` (Chạy ở Port 5014)

**Cách Test (Dễ dàng qua trình duyệt):**
- **V2 (Gốc):** `curl http://localhost:5014/api/v2/users`
  *Sẽ trả về danh sách user chi tiết kèm role, email.*
- **V1 (Adapter):** `curl http://localhost:5014/api/v1/users`
  *Vẫn gọi chung 1 hàm logic với V2 bên dưới hệ thống, nhưng kết quả trả ra đã bị Adapter gọt bớt, chỉ còn lại danh sách tên mộc mạc như bản cũ.*
