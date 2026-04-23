# Hướng Dẫn Thực Hành: API Testing & Quality Assurance (Python Flask)

Xin chào các bạn, trong bài LAB ngày hôm nay của Tuần 8, chúng ta sẽ được làm quen với Quy trình bảo đảm chất lượng phần mềm - Quality Assurance (QA). Cụ thể, chúng ta sẽ tấn công thẳng vào tầng Backend (API) mà các bạn đã quen thuộc ở các bài trước.

## Yêu Cầu Chuẩn Bị
1. Cài đặt Python 3, Node.js (Và NPM).
2. Di chuyển Terminal vào thư mục `Week8\Demo` và cài các thư viện lõi:
```bash
pip install -r requirements.txt
npm install -g newman newman-reporter-htmlextra
```

---

## Bước 1: Khởi động Server Mục Tiêu (The Target)
Để có cái mà test, tôi đã viết sẵn cho các bạn một API siêu tốc giả lập Database trên RAM nằm ở `api_server/app.py`.
Mở một Terminal, khởi chạy và giữ nguyên nó:
```bash
cd api_server
python app.py
```
*(Server sẽ chạy tại http://localhost:5000)*

---

## Bước 2: Hiểu về Unit Test & Integration Test với Pytest
Hãy mở một cửa sổ Terminal THỨ HAI. Đây là lúc làm kĩ sư tự động:
```bash
pytest tests/
```
Gõ lệnh này xong bạn sẽ thấy Pytest tự động mò vào thư mục `tests/` để quét hàm `test_1_unit.py` (Đánh dấu TÍNH ĐÚNG ĐẮN của một hàm nhỏ bé) và `test_2_integration.py` (Đánh giá mức ĐỘ KHỚP của một tập hợp các linh kiện/API sinh ra mã 200). Đọc file code để hiểu cách viết test nhé.

---

## Bước 3: API Automation với Postman & Newman
Đừng click bằng tay! Giả sử sếp yêu cầu bạn Test 50 APIs một lần.
1. Khám phá file `postman_newman/collection.json` (bạn có thể Import nó vào Postman UI để xem). Trong đó tôi đã nhúng sẵn code **JavaScript** kiểm tra mã Status và độ trễ Response Time. 
2. Chạy báo cáo tự động bằng `newman`:
   - Hoặc click đúp file `run_newman.bat`
   - Hoặc tại Terminal gõ: 
     ```bash
     cd postman_newman
     newman run collection.json -r cli,htmlextra
     ```
3. Sau khi lệnh chạy xong, một thư mục `newman` sẽ được sinh ra ở đó. Click đúp mở file `.html` bên trong bằng Trình duyệt Google Chrome để thấy bản báo cáo xanh đỏ vô cùng ngầu dể gửi cho sếp!

---

## Bước 4: Kiểm Soát Sức Chịu Đựng của Hệ Thống (Performance/Load Test)
API của bạn chạy rất nhanh khi 1 người gọi, thế 10,000 người vào thì sao? Ta gọi đàn "Châu chấu" (Locust) tới để cắn thử!
1. Tại Terminal đang rảnh, chạy:
```bash
cd performance
locust -f locustfile.py
```
2. Mở trình duyệt truy cập: `http://localhost:8089`. Giao diện Locust cực kỳ bắt mắt sẽ hiện ra.
3. Nhập:
   - **Number of users**: `100` 
   - **Spawn rate**: `10`
   - **Host**: `http://127.0.0.1:5000`
4. Ấn nút `Start swarming` và cùng quan sát biểu đồ. API Flask của chúng ta sẽ chịu được số RPS (Request/Giây) là bao nhiêu trước khi nó sập?

> Cuối cùng, Bài tập (Homework) tuần này của bạn là tự phân tích 4 API còn lại (GET_id, PUT, DELETE) vào trong `collection.json` giống như trong file mẫu nhé! Chúc code vui!
