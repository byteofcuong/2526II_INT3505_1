# Hệ Thống Microservices Demo - Hướng Dẫn Kiến Trúc & Kiểm Thử (Cập nhật Phase 2)

Tài liệu này cung cấp phân tích kiến trúc sâu sắc cho cả hai giai đoạn (Phase 1 & Phase 2) của hệ sinh thái microservices demo được xây dựng bằng Python Flask, trình bày các mẫu thiết kế API nâng cao (Advanced API Design Patterns) và hướng dẫn kiểm thử chi tiết từng bước thông qua các lệnh `curl` trên Terminal.

---

## 1. Phân Tích Kiến Trúc Sâu Sắc (In-Depth Architectural Analysis)

Dưới đây là chi tiết phân tích cách thức triển khai và vai trò doanh nghiệp của từng mẫu thiết kế được áp dụng trong mã nguồn `app_core.py`.

### A. CRUD Read Pattern (Đọc Tài Nguyên Đơn Lẻ)
* **Vị trí triển khai**: Hàm `get_order(order_id)` tại dòng định tuyến `@app.route("/api/v1/orders/<int:order_id>", methods=["GET"])`.
* **Cơ chế hoạt động**: 
  * API tiếp nhận định danh tài nguyên duy nhất (`order_id`) trực tiếp qua URL đường dẫn.
  * Truy cập vào từ danh sách bộ nhớ `ORDERS_DB` với độ phức tạp thời gian đạt mức hằng số $O(1)$.
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

### F. CRUD Update & Business Logic State Transition (Cập nhật Trạng Thái Nghiệp Vụ - Phase 2)
* **Vị trí triển khai**: Hàm `pay_order(order_id)` tại định tuyến `@app.route("/api/v1/orders/<int:order_id>/pay", methods=["POST"])`.
* **Cơ chế hoạt động**:
  * Tiếp nhận yêu cầu thanh toán cho một đơn hàng cụ thể.
  * Kiểm tra thực thể đơn hàng trong kho lưu trữ `ORDERS_DB`. Trả về `404` nếu không tìm thấy.
  * Xác thực tính hợp lệ của trạng thái nghiệp vụ hiện tại: Nếu đơn hàng đã có trạng thái `PAID`, API từ chối xử lý và phản hồi lỗi `400 Bad Request` để ngăn chặn hành vi thanh toán trùng lặp (Double Payment).
  * Thực hiện quá trình chuyển đổi trạng thái (State Transition) từ `PENDING` thành `PAID` và cập nhật cơ sở dữ liệu.
* **Vai trò trong hệ thống Enterprise**:
  * Đảm bảo tính toàn vẹn của mô hình máy trạng thái (State Machine) của thực thể đơn hàng.
  * Ngăn chặn các lỗi logic nghiêm trọng trong giao dịch tài chính ở môi trường phân tán bằng các ràng buộc xác thực trạng thái nghiêm ngặt trước khi chuyển đổi.

### G. Secure Webhook Sender Pattern (Bộ Phát Webhook Bảo Mật Bất Đồng Bộ - Phase 2)
* **Vị trí triển khai**: Hàm `send_webhook_async(order_id, price)` sử dụng thư viện mạng chuẩn `urllib.request` kết hợp mã hóa bảo mật từ các module `hmac`, `hashlib` và `uuid`.
* **Cơ chế hoạt động**:
  * **Thực thi bất đồng bộ**: Khi thanh toán thành công, hệ thống không giữ chân luồng xử lý chính của người dùng mà ngay lập tức khởi tạo một luồng chạy ngầm độc lập (`threading.Thread`) để gửi Webhook. Điều này giúp tối ưu hóa thời gian phản hồi (Response Time) về phía Client ở mức tối đa.
  * **Cấu trúc Payload chuẩn**: Tạo gói dữ liệu JSON chứa định danh sự kiện duy nhất (`event_id` sử dụng UUID v4 nhằm phục vụ cơ chế xử lý trùng lặp - Idempotency), phân loại sự kiện (`type: "order.payment_succeeded"`) và trường dữ liệu chứa thông tin nghiệp vụ cốt lõi (`data`).
  * **Ký số bảo mật HMAC-SHA256**: 
    1. Lấy mốc thời gian Unix hiện tại dạng chuỗi (`timestamp`).
    2. Gom nhóm thông tin: Kết hợp `f"{timestamp}.{raw_json_payload}"` thành một thông điệp chuỗi byte đồng nhất.
    3. Mã hóa: Sử dụng thuật toán HMAC kết hợp SHA-256 cùng khóa bí mật dùng chung (`"super_secret_signing_key"`) để sinh mã chữ ký bảo mật (Hex digest).
    4. Gắn cờ tiêu đề: Truyền tải mốc thời gian qua tiêu đề `X-Webhook-Timestamp` và chữ ký qua `X-Webhook-Signature` trên yêu cầu HTTP gửi đi.
* **Tại sao Chữ ký HMAC-SHA256 là tối quan trọng đối với tích hợp Enterprise?**
  1. **Xác thực danh tính (Authenticity)**: Bên nhận Webhook (Third-Party Receiver) có thể tự tính toán lại chữ ký bằng khóa bí mật dùng chung. Nếu hai chữ ký trùng khớp hoàn toàn, bên nhận có thể khẳng định 100% rằng Webhook này được gửi từ chính hệ thống lõi đáng tin cậy của chúng ta chứ không phải từ một kẻ mạo danh.
  2. **Chống giả mạo dữ liệu (Integrity)**: Bất kỳ sự thay đổi nhỏ nào (dù chỉ là 1 ký tự) trong payload JSON trong quá trình truyền tải trên môi trường mạng đều sẽ làm sai lệch chữ ký tính toán được ở đầu nhận, giúp đầu nhận phát hiện ngay hành vi can thiệp trái phép.
  3. **Chống tấn công phát lại (Replay Attacks)**: Kẻ tấn công có thể nghe lén gói tin Webhook và gửi lại gói tin đó nhiều lần nhằm gây ra lỗi nghiệp vụ ở hệ thống đích. Bằng cách nhúng tiêu đề `X-Webhook-Timestamp` trực tiếp vào chuỗi ký chữ ký HMAC, bên nhận có thể giới hạn thời hạn hiệu lực của chữ ký (ví dụ: từ chối các webhook có timestamp lệch quá 5 phút so với thời gian hiện tại của máy chủ nhận). K kẻ tấn công không thể sửa timestamp mà không làm hỏng chữ ký bảo mật.

---

## 2. Hướng Dẫn Kiểm Thử Từng Bước (Step-by-Step Testing Guide - Phase 2)

Hãy đảm bảo rằng máy chủ Flask đã được khởi chạy thành công bằng cách chạy lệnh sau trên Terminal của bạn:
```bash
python app_core.py
```
Máy chủ sẽ hoạt động tại địa chỉ `http://localhost:5000`.

### Bước 1: Chu bị Lắng Nghe Sự Kiện Thời Gian Thực (SSE Stream)
Mở một Terminal mới độc lập và chạy lệnh dưới đây để kết nối vào cổng sự kiện thời gian thực:
```bash
curl -N -H "Accept: text/event-stream" http://localhost:5000/api/v1/orders/stream
```
*Hãy giữ Terminal này luôn mở.* Khi thực hiện thanh toán thành công ở Bước 2, bạn sẽ ngay lập tức quan sát thấy sự kiện thanh toán được đẩy trực tiếp về Terminal này theo thời gian thực mà không cần tải lại trang.

---

### Bước 2: Thực hiện Kiểm Thử API Thanh Toán (POST CRUD Update & State Transition)

#### Kịch bản A: Thực hiện thanh toán thành công cho đơn hàng đang chờ (`PENDING`)
Gửi yêu cầu thanh toán (`POST`) cho đơn hàng số `1`:
```bash
curl -i -X POST http://localhost:5000/api/v1/orders/1/pay
```
* **Kết quả kỳ vọng**: 
  * Máy chủ trả về HTTP Status `200 OK` kèm theo JSON:
    ```json
    {
      "message": "Payment successfully processed for order 1.",
      "data": {
        "id": 1,
        "item": "Wireless Mouse",
        "price": 25,
        "status": "PAID",
        "_links": {
          "self": {
            "href": "http://localhost:5000/api/v1/orders/1",
            "method": "GET"
          },
          "receipt": {
            "href": "http://localhost:5000/api/v1/orders/1/receipt",
            "method": "GET"
          }
        }
      }
    }
    ```
  * **Quan sát Terminal SSE**: Ngay lập tức, trên Terminal SSE đang mở ở Bước 1 sẽ xuất hiện thông điệp sự kiện cập nhật trạng thái đơn hàng thời gian thực:
    ```text
    event: order_updated
    data: {"event": "order_updated", "timestamp": 1779344499.1234, "data": {"event": "order.updated", "order_id": 1, "status": "PAID"}}
    ```
  * **Quan sát Log Máy Chủ Flask**: Bạn sẽ nhận thấy log ghi nhận nỗ lực kích hoạt gửi Webhook bảo mật dưới luồng chạy ngầm tới `http://127.0.0.1:5001/webhook/order-paid`. (Hiện tại receiver chưa chạy nên log sẽ xuất hiện thông điệp lỗi gửi webhook trong luồng ngầm nhưng tuyệt đối không gây sập máy chủ Flask chính, chứng minh tính bất đồng bộ cô lập lỗi hoàn hảo).

#### Kịch bản B: Kiểm thử chặn thanh toán trùng lặp (Double Payment Protection)
Thực hiện gửi lại yêu cầu thanh toán cho chính đơn hàng số `1` vừa được thanh toán ở trên:
```bash
curl -i -X POST http://localhost:5000/api/v1/orders/1/pay
```
* **Kết quả kỳ vọng**:
  * Máy chủ phát hiện đơn hàng đã ở trạng thái `PAID`. Trả về mã lỗi `400 Bad Request` kèm theo phản hồi JSON ngăn chặn giao dịch:
    ```json
    {
      "error": "OrderAlreadyPaid",
      "message": "Order with ID 1 has already been paid and cannot be processed again."
    }
    ```

#### Kịch bản C: Kiểm thử thanh toán cho đơn hàng không tồn tại
Gửi yêu cầu thanh toán cho đơn hàng có định danh lỗi `999`:
```bash
curl -i -X POST http://localhost:5000/api/v1/orders/999/pay
```
* **Kết quả kỳ vọng**:
  * Máy chủ trả về mã lỗi `404 Not Found` kèm JSON:
    ```json
    {
      "error": "OrderNotFound",
      "message": "An order with ID 999 could not be found."
    }
    ```

---

### Bước 3: Kiểm thử Đọc Trạng Thái Đơn Hàng Mới (HATEOAS State Transition Verification)
Thực hiện truy xuất thông tin chi tiết đơn hàng số `1` sau khi đã thanh toán thành công:
```bash
curl -i -X GET http://localhost:5000/api/v1/orders/1
```
* **Kết quả kỳ vọng**: Trả về trạng thái `PAID`. Điểm đặc biệt là liên kết hành động chuyển đổi trạng thái `"pay"` (`POST`) trong `_links` đã tự động biến mất và được thay thế bằng liên kết truy xuất hóa đơn thanh toán `"receipt"` (`GET`), chứng minh nguyên lý HATEOAS dẫn dắt vòng đời nghiệp vụ hoạt động chính xác tuyệt đối.
