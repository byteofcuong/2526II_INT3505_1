# Hệ Thống Quản Lý Thiết Bị & Kiểm Thử Toàn Diện

Dự án này là một bài tập mô phỏng quá trình xây dựng Hệ thống mục tiêu (System Under Test - SUT) bằng Flask API, kết hợp với các cấp độ kiểm thử toàn diện từ Unit Test, Integration Test, cho tới API Automation Test (Postman/Newman) và Performance Test (Locust).

## 🗂️ Cấu Trúc File và Vai Trò

- **`app.py`**: Đây là file chạy chính của API (Flask Server). Nó định nghĩa 5 RESTful endpoints (GET, POST, PUT, DELETE) cho tài nguyên `equipments`. Đóng vai trò là cầu nối xử lý Request và trả về Response (JSON).
- **`database.py`**: Quản lý việc kết nối và khởi tạo cơ sở dữ liệu SQLite (`equipments.db`). Cung cấp các hàm tiện ích (`get_db_connection()`, `init_db()`) để các file khác gọi đến.
- **`business_logic.py`**: Tách biệt logic nghiệp vụ khỏi API để dễ dàng viết Unit Test. Chứa các hàm tính toán ngày bảo trì dựa trên loại thiết bị (`calculate_maintenance_date`) và hàm kiểm tra định dạng mã thiết bị (`validate_equipment_code`).
- **`requirements.txt`**: Danh sách các thư viện Python cần cài đặt.
- **`tests/test_unit.py`**: File Unit Test (Pytest). Kiểm thử trực tiếp các hàm trong `business_logic.py` mà không cần chạy Flask hay kết nối Database.
- **`tests/test_integration.py`**: File Integration Test (Pytest). Kết hợp `flask.test_client` và một database tạm thời để kiểm thử quy trình thực tế khi gọi vào các Endpoints (Từ tạo, đọc, sửa, xóa).
- **`postman/collection.json` & `environment.json`**: Cấu hình các request Postman dùng để tự động test API (kịch bản end-to-end cho API). `environment.json` cung cấp biến môi trường (như URL server).
- **`locustfile.py`**: File cấu hình mô phỏng người dùng của Locust. Định nghĩa các hành vi mà user ảo sẽ thực hiện khi "tấn công" server của bạn (VD: Lấy danh sách, thêm và xóa liên tục).

---

## 🚀 Hướng Dẫn Cài Đặt

1. **Di chuyển vào thư mục dự án**:
   ```cmd
   cd "d:\Direc of code\2526II_INT3505_1\Week8\HW"
   ```

2. **Cài đặt các thư viện Python**:
   ```cmd
   pip install -r requirements.txt
   ```

3. **Cài đặt Newman** (Yêu cầu phải có Node.js):
   ```cmd
   npm install -g newman
   ```

---

## 🏃 Hướng Dẫn Khởi Chạy & Kiểm Thử

### Bước 1: Khởi động Flask API (System Under Test)
Bạn cần bật API lên trước khi chạy Postman hoặc Locust. (Đối với Pytest thì không cần bật API vì nó có client ảo).
Mở một terminal mới và chạy:
```cmd
python app.py
```
*Server sẽ chạy tại `http://localhost:5000`.*

### Bước 2: Chạy Cấp độ 1 & 2 - Unit & Integration Test (Pytest)
Mở một terminal khác và chạy lệnh sau để thực thi toàn bộ test bằng Pytest:
```cmd
python -m pytest tests/ -v
```
*(Nếu thành công, bạn sẽ thấy kết quả `PASSED` màu xanh cho 100% các test cases).*

### Bước 3: Chạy Cấp độ 3 - API Automation Test (Newman/Postman)
Với Server Flask đang chạy (ở Bước 1), bạn chạy lệnh sau trên terminal để Newman giả lập các requests:
```cmd
newman run postman/collection.json -e postman/environment.json
```
*(Bạn sẽ thấy một bảng báo cáo tóm tắt trên terminal về tỷ lệ request pass/fail).*

### Bước 4: Chạy Cấp độ 4 - Performance Test (Locust)
Với Server Flask đang chạy, bạn mở terminal và gõ:
```cmd
python -m locust -f locustfile.py
```
- Locust sẽ in ra thông báo nó đang chạy Web UI ở địa chỉ `http://localhost:8089`.
- Mở trình duyệt web, truy cập `http://localhost:8089`.
- Nhập số lượng **Users** (Ví dụ: `200`) và **Spawn rate** (Số user thêm vào mỗi giây, VD: `20`). Host điền `http://localhost:5000`.
- Nhấn **Start Swarming** và quan sát các biểu đồ để lấy kết quả thời gian phản hồi (Response Time), Thông lượng (RPS) và Tỷ lệ lỗi (Error Rate).
