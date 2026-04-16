# Demo Week 7: Triển khai Backend từ OpenAPI đến MongoDB

Quá trình triển khai theo 9 bước:

### [x] Bước 1: Chuẩn bị file openapi.yaml 
- **Mục tiêu:** Định nghĩa trước cấu trúc API (Contract-First Design) bao gồm các endpoint CRUD ("Product") và Schema Object.
- **Hành động:** Đã tạo bằng tay file `openapi.yaml`. File này hoạt động như một bản "bản vẽ kỹ thuật" cho toàn bộ phần mềm.

### [x] Bước 2: Sinh code Backend từ file OpenAPI
- **Mục tiêu:** Sử dụng công cụ OpenAPI Generator (thế hệ mới của Swagger Codegen) để đọc "bản vẽ" và tự động xếp gạch, tạo ra bộ khung thư mục mã nguồn Node.js (Express server). Giúp lập trình viên không cần mất công tạo khung rỗng.
- **Lệnh thực thi:**
  ```bash
  npx -y @openapitools/openapi-generator-cli generate -i openapi.yaml -g nodejs-express-server -o backend
  ```
- **Hành động:** Đã chạy lệnh và sinh thành công cấu trúc toàn bộ dự án tại thư mục `/backend`.

### [x] Bước 3: Cài đặt Node Dependencies
- **Mục tiêu:** Cài đặt các thư viện lõi (Express, parser,...) mà bộ Source code mới sinh ra yêu cầu. Dựa trên file `package.json` tự sinh.
- **Lệnh thực thi:** `cd backend` và `npm install`
- **Hành động:** Đã tải xong toàn bộ hàng trăm thư viện nền tảng vào thư mục `node_modules` bên trong `backend`.

### [x] Bước 4: Cài đặt mongoose
- **Mục tiêu:** Bổ sung thêm Driver cầu nối giữa Node.js và hệ cơ sở dữ liệu MongoDB.
- **Lệnh thực thi:** `npm install mongoose`
- **Hành động:** Đã cài đặt xong mongoose vào `package.json` của hệ thống.
### [x] Bước 5: Thiết lập MongoDB connection trong Server
- **Mục tiêu:** Giúp server khởi động có thể nối tới cơ sở dữ liệu.
- **Hành động:** Đã chỉnh sửa file `backend/index.js`, thêm hàm `mongoose.connect('mongodb://127.0.0.1:27017/product_db')` để đảm bảo kết nối trước khi nhận requests của khách hàng.

### [x] Bước 6: Xây dựng Mongoose Schema (Product)
- **Mục tiêu:** Quy định chặt chẽ cấu trúc dữ liệu lưu trong MongoDB khớp với bản thiết kế OpenAPI.
- **Hành động:** Đã tạo ra file `backend/models/Product.js`. Định nghĩa một Schema chuẩn gồm `name` và `price`. Biến `_id` sẽ tự động được gán bởi MongoDB.

### [x] Bước 7: Nối logic Mongoose vào Controller/Service do Swagger sinh
- **Mục tiêu:** Mảnh ghép cuối cùng, thay máu dữ liệu giả (Dummy Data) sinh mặc định bằng câu truy vấn database.
- **Hành động:** Đã mở file `backend/services/DefaultService.js`, import class Mongoose API `Product` vào. Đồng thời, thay thế 5 chỗ `resolve({...})` thành các logic `Product.find()`, `Product.create()`,... phù hợp theo từng Endpoints.

### [x] Bước 8: Start Server và check logs
- **Mục tiêu:** Vận hành phần mềm.
- **Hành động:** Chạy lệnh `npm start`. Màn hình Console log thông báo hai tín hiệu cực kỳ tốt: `Connected to MongoDB successfully` (Mongoose báo cáo) và `Listening on port 8080` (Node Express đã lên sóng).

### [x] Bước 9: Mở Swagger UI trên trình duyệt để kiểm thử
- **Mục tiêu:** Xác nhận logic thực tế với dữ liệu thật mà không cần code Front-end.
- **Hành động:** Project này Swagger Codegen đã đính kèm sẵn công cụ "Swagger UI". Bạn chỉ cần mở trình duyệt và gõ `http://localhost:8080/api-docs/` hoặc `http://localhost:8080/docs` (hoặc tuỳ framework sinh ra, thường sẽ tự host ở một doc-endpoint).
