# Hệ Thống Microservices Demo - Hướng Dẫn Kiến Trúc & Kiểm Thử

Tài liệu này cung cấp phân tích kiến trúc sâu sắc cho phần đầu tiên của hệ sinh thái microservices demo được xây dựng bằng Python Flask, trình bày các mẫu thiết kế API nâng cao (Advanced API Design Patterns) và hướng dẫn kiểm thử chi tiết từng bước thông qua các lệnh `curl` trên Terminal.

---

## 1. Phân Tích Kiến Trúc Sâu Sắc (In-Depth Architectural Analysis)

Dưới đây là chi tiết phân tích cách thức triển khai và vai trò doanh nghiệp của từng mẫu thiết kế được áp dụng trong mã nguồn `app_core.py`.

### A. CRUD Read Pattern (Đọc Tài Nguyên Đơn Lẻ)
* **Vị trí triển khai**: Hàm `get_order(order_id)` tại dòng định tuyến `@app.route("/api/v1/orders/<int:order_id>", methods=["GET"])`.
* **Cơ chế hoạt động**: 
  * API tiếp nhận định danh tài nguyên duy nhất (`order_id`) trực tiếp qua URL đường dẫn.
  * Truy cập vào từ điển bộ nhớ `ORDERS_DB` với độ phức tạp thời gian đạt mức hằng số $O(1)$.
  * Nếu tài nguyên không tồn tại, hệ thống trả về mã trạng thái tiêu chuẩn `404 Not Found` kèm payload lỗi định dạng chuẩn (`error` và `message`).
  * Nếu tìm thấy tài nguyên, hệ thống sao chép bản ghi dữ liệu gốc và làm phong phú thêm bằng việc gắn các liên kết trạng thái HATEOAS thích hợp trước khi trả về kết quả định dạng JSON cùng mã trạng thái `200 OK`.
* **Vai trò trong hệ thống Enterprise**:
  * Là giao thức đồng bộ cơ bản nhất của kiến trúc RESTful nhằm phục vụ hiển thị chi tiết thực thể.
  * Trong môi trường doanh nghiệp thực tế, thao tác này thường được tối ưu bằng việc áp dụng các lớp đệm đọc (Read-through Cache) như Redis để bảo vệ cơ sở dữ liệu lõi khỏi các truy vấn lặp lại.

### B. Query Filtering Pattern (Lọc Bộ Sưu Tập)
* **Vị trí triển khai**: Hàm `get_orders()` tại dòng định tuyến `@app.route("/api/v1/orders", methods=["GET"])`, cụ thể xử lý tại biến `status_filter`.
* **Cơ chế hoạt động**:
  * API trích xuất tham số lọc thông qua URL Query String `?status=<giá_trị>`.
  * Thực hiện chuẩn hóa dữ liệu đầu vào bằng phương thức chuyển đổi chữ hoa (`.upper()`).
  * Danh sách kết quả được lọc động chỉ giữ lại các đối tượng đơn hàng khớp chính xác với trạng thái được yêu cầu trước khi đi vào phân trang.
* **Vai trò trong hệ thống Enterprise**:
  * Giảm tải băng thông truyền tải trên đường truyền bằng cách ngăn chặn việc gửi các tập dữ liệu thừa không mong muốn về phía Client.
  * Tối ưu hóa hiệu năng máy chủ khi kết hợp với tầng dữ liệu dưới dạng câu lệnh `WHERE` sử dụng cột được đánh chỉ mục (Index) trong Database thực tế.

### C. Keyset Pagination Pattern (Phân Trang Theo Con Trỏ / Cursor)
* **Vị trí triển khai**: Hàm `get_orders()`, xử lý thông qua các tham số điều phối `starting_after` và `limit`.
* **Cơ chế hoạt động**:
  * Thay vì sử dụng cơ chế phân trang dựa trên vị trí sai lệch (`OFFSET` và `LIMIT`) thường gặp, hệ thống sử dụng định danh duy nhất tăng dần của bản ghi cuối cùng của trang trước đó làm mốc con trỏ (Cursor).
  * Tham số `starting_after` xác định ID của bản ghi mà từ đó trang tiếp theo sẽ bắt đầu (`id > starting_after`).
  * Tham số `limit` khống chế số lượng phần tử trả về tối đa trên mỗi trang (được cấu hình mặc định là `2` và giới hạn tối đa `100` để ngăn chặn các cuộc tấn công từ chối dịch vụ thông qua lượng payload khổng lồ).
  * API kiểm tra xem có bản ghi bổ sung nào vượt quá giới hạn trang hiện tại để thiết lập cờ trạng thái `has_more`.
* **Vai trò trong hệ thống Enterprise**:
  * **Hiệu năng vượt trội**: Phân trang truyền thống (`OFFSET`) đòi hỏi cơ sở dữ liệu phải quét qua và loại bỏ toàn bộ bản ghi trước đó, dẫn đến hiệu năng giảm dần về tuyến tính $O(N)$ đối với các trang sâu. Keyset Pagination tận dụng tối đa cấu trúc cây B-Tree của Index để thực hiện tìm kiếm trực tiếp với chi phí $O(\log N)$ bất kể độ sâu của trang.
  * **Nhất quán dữ liệu**: Tránh hiện tượng bỏ sót (skipping) hoặc trùng lặp (duplication) dữ liệu hiển thị trên giao diện người dùng khi có các thao tác ghi mới (thêm, xóa bản ghi) xảy ra đồng thời trong quá trình người dùng duyệt danh sách.

### D. HATEOAS Pattern (Hypermedia As The Engine Of Application State)
* **Vị trí triển khai**: Hàm sinh liên kết `generate_order_links(order)` và phần tạo siêu liên kết danh mục `root_links` trong `get_orders()`.
* **Cơ chế hoạt động**:
  * Mỗi bản ghi đơn hàng trả về chứa đối tượng `_links` định nghĩa rõ các hành động hợp lệ mà Client có thể thực hiện trên tài nguyên đó.
  * Các hành động này thay đổi động dựa trên trạng thái (State) hiện tại của thực thể:
    * Nếu đơn hàng ở trạng thái `PENDING`, API cung cấp hành động `"pay"` (`POST`) để thanh toán.
    * Nếu đơn hàng ở trạng thái `PAID`, hành động `"pay"` bị ẩn đi, thay vào đó API cung cấp hành động `"receipt"` (`GET`) để truy xuất hóa đơn.
  * Ở cấp độ bộ sưu tập danh sách, nếu cờ `has_more` bằng `True`, API tự động tạo liên kết `"next"` trích xuất con trỏ từ thực thể cuối cùng của trang hiện tại, giúp Client dễ dàng duyệt tiếp mà không cần tự tính toán hay lắp ghép URL.
* **Vai trò trong hệ thống Enterprise**:
  * **Phi tập trung liên kết (Decoupling)**: Client không cần phải ghi nhớ hay mã hóa cứng (hardcode) cấu trúc URL cho từng hành động nghiệp vụ. Điều này cho phép Backend thay đổi hoặc nâng cấp cấu trúc phiên bản API (API Versioning) mà không gây đổ vỡ (breaking changes) ứng dụng phía Client.
  * **Tự khám phá (Discoverability)**: Hướng dẫn Client các bước chuyển đổi trạng thái nghiệp vụ tiếp theo một cách động ngay trong payload dữ liệu trả về.

### E. Server-Sent Events Pattern - SSE (Truyền Tải Sự Kiện Thời Gian Thực)
* **Vị trí triển khai**: Điểm cuối `@app.route("/api/v1/orders/stream", methods=["GET"])` sử dụng generator `sse_generator()` kết hợp bộ phân phối luồng bất đồng bộ dựa trên `queue.Queue` và luồng chạy ngầm `simulate_background_events()`.
* **Cơ chế hoạt động**:
  * Thiết lập một kết nối HTTP hướng đơn (unidirectional), giữ lâu (long-lived) thông qua giao thức truyền tải chuẩn `text/event-stream`.
  * Mỗi Client kết nối đến sẽ được cấp một hàng đợi thread-safe `queue.Queue` riêng nằm dưới sự bảo vệ của `LISTENERS_LOCK` để tránh xung đột luồng khi đọc/ghi đồng thời.
  * Cơ chế chạy ngầm liên tục đẩy các sự kiện mô phỏng phát sinh đơn hàng thông qua hàm `broadcast_event()`. Hàm này sẽ lặp qua các hàng đợi đang đăng ký và đẩy thông điệp xuống.
  * Để ngăn chặn hiện tượng mất kết nối do các proxy trung gian ngắt vì nhàn rỗi (idle), generator định kỳ gửi sự kiện `heartbeat` sau mỗi 15 giây.
  * Khi Client đóng kết nối, cơ chế bắt ngoại lệ `GeneratorExit` được kích hoạt để loại bỏ hàng đợi ra khỏi danh sách lắng nghe hoạt động, giúp giải phóng tài nguyên RAM ngay lập tức.
* **Vai trò trong hệ thống Enterprise**:
  * SSE cung cấp một giải pháp truyền tải đẩy thời gian thực cực kỳ gọn nhẹ so với WebSockets vì nó chạy trực tiếp trên giao thức HTTP tiêu chuẩn, dễ dàng vượt qua các bức tường lửa (Firewalls) và tương thích tốt với các cơ chế cân bằng tải (Load Balancers).
  * Lý tưởng cho các bảng theo dõi trạng thái (Dashboards), theo dõi tiến trình xử lý đơn hàng từ các hệ thống ERP/kho bãi chạy ngầm mà không cần thực hiện kỹ thuật liên tục thăm dò (Polling) gây quá tải máy chủ.

---

## 2. Hướng Dẫn Kiểm Thử Từng Bước (Step-by-Step Testing Guide)

Hãy đảm bảo rằng máy chủ Flask đã được khởi chạy thành công bằng cách chạy lệnh sau trên Terminal của bạn:
```bash
python app_core.py
```
Máy chủ sẽ hoạt động tại địa chỉ `http://localhost:5000`.

### Bước 1: Kiểm thử API Truy xuất Đơn Hàng Đơn Lẻ (CRUD Read)
Gửi yêu cầu kiểm tra đơn hàng có ID là `1`.
```bash
curl -i -X GET http://localhost:5000/api/v1/orders/1
```
* **Kết quả kỳ vọng**: Trả về thông tin đơn hàng số 1 với trạng thái `PENDING`. Quan sát trong trường `_links` phải xuất hiện hành động `"pay"` trỏ tới phương thức `POST http://localhost:5000/api/v1/orders/1/pay`.

Gửi yêu cầu kiểm tra đơn hàng có ID là `2` (đơn hàng đã thanh toán):
```bash
curl -i -X GET http://localhost:5000/api/v1/orders/2
```
* **Kết quả kỳ vọng**: Trả về thông tin đơn hàng số 2 với trạng thái `PAID`. Quan sát trong trường `_links` hành động `"pay"` đã biến mất và được thay thế bằng hành động `"receipt"`.

Gửi yêu cầu kiểm tra đơn hàng không tồn tại (ID là `999`):
```bash
curl -i -X GET http://localhost:5000/api/v1/orders/999
```
* **Kết quả kỳ vọng**: Trả về mã trạng thái `404 Not Found` kèm theo thông điệp lỗi JSON:
  ```json
  {"error": "OrderNotFound", "message": "An order with ID 999 could not be found."}
  ```

---

### Bước 2: Kiểm thử Phân Phối và Lọc Dữ Liệu Bộ Sưu Tập (Query & Pagination & HATEOAS)

#### Kịch bản A: Lấy trang đầu tiên của tất cả đơn hàng (Mặc định limit = 2)
```bash
curl -i -X GET "http://localhost:5000/api/v1/orders?limit=2"
```
* **Kết quả kỳ vọng**:
  * Trả về danh sách 2 đơn hàng đầu tiên (ID `1` và `2`).
  * Trường `meta` ghi nhận `has_more: true` và `size: 2`.
  * Trong trường `_links` ở cấp độ gốc sẽ xuất hiện một liên kết `"next"` có dạng:
    `"next": {"href": "http://localhost:5000/api/v1/orders?limit=2&starting_after=2", ...}`

#### Kịch bản B: Sử dụng liên kết `"next"` để lấy trang tiếp theo
Sử dụng giá trị ID cuối cùng làm cursor (`starting_after=2`) để lấy tiếp 2 phần tử tiếp theo:
```bash
curl -i -X GET "http://localhost:5000/api/v1/orders?limit=2&starting_after=2"
```
* **Kết quả kỳ vọng**: Trả về đơn hàng số `3` và `4`. Liên kết `"next"` mới tiếp tục được sinh ra với `starting_after=4`.

#### Kịch bản C: Lọc đơn hàng kết hợp phân trang
Thực hiện lọc các đơn hàng chỉ có trạng thái là `PENDING`:
```bash
curl -i -X GET "http://localhost:5000/api/v1/orders?status=pending&limit=2"
```
* **Kết quả kỳ vọng**: Trả về các đơn hàng có trạng thái `PENDING` (ID `1` và `3`). Bản ghi số `2` (đã thanh toán) bị loại bỏ khỏi luồng phân trang.

---

### Bước 3: Kiểm thử Sự Kiện Thời Gian Thực (Event-Driven SSE Stream)

Mở một Terminal mới độc lập và chạy lệnh sau để lắng nghe sự kiện đẩy về từ máy chủ theo thời gian thực:
```bash
curl -N -H "Accept: text/event-stream" http://localhost:5000/api/v1/orders/stream
```
*Tham số `-N` vô hiệu hóa cơ chế buffer của curl để hiển thị sự kiện ngay lập tức khi máy chủ vừa gửi.*

* **Kết quả kỳ vọng**:
  * Ngay lập tức nhận được thông điệp bắt tay thành công từ máy chủ:
    ```text
    event: handshake
    data: {"message": "Connected to real-time orders stream"}
    ```
  * Cứ mỗi 5 giây, luồng chạy ngầm của máy chủ sẽ tạo ngẫu nhiên một đơn hàng và bạn sẽ nhận được thông điệp dạng:
    ```text
    event: order_created
    data: {"event": "order_created", "timestamp": 1779344445.1234, "data": {"id": 101, "item": "Smart Watch", "price": 145, "status": "PENDING"}}
    ```
  * Nếu không có sự kiện nào phát sinh, sau mỗi 15 giây bạn sẽ thấy một gói tin `heartbeat` được gửi xuống để duy trì đường truyền.
  * Nhấn `Ctrl + C` để đóng Terminal. Quan sát log phía máy chủ sẽ thấy hệ thống tự động phát hiện kết nối đóng và thực hiện thu hồi tài nguyên hàng đợi liên kết thành công mà không gây rò rỉ bộ nhớ.
