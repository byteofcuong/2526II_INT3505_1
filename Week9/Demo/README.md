# API Versioning, Deprecation & Breaking Changes Demo

Đây là một project Flask nhỏ để minh họa cách quản lý phiên bản API (Versioning), cách cảnh báo người dùng khi API cũ chuẩn bị bị xóa (Deprecation) và cách xử lý khi thay đổi cấu trúc dữ liệu làm ảnh hưởng đến client (Breaking Changes).

## Các khái niệm được Demo:
1. **API Versioning (Các chiến lược)**: 
   - **URL Path (Phổ biến nhất)**: Phân tách URL bằng `/v1/` và `/v2/` để duy trì đồng thời 2 phiên bản.
   - **Custom Header**: Sử dụng một header tự định nghĩa như `X-API-Version: 2` để yêu cầu một phiên bản cụ thể từ server (endpoint không đổi).
   - **Query Parameter**: Sử dụng tham số trên URL như `?version=2` (ít phổ biến hơn ở môi trường thực tế nhưng đơn giản).
2. **Deprecation**: Tại v1, server sử dụng thư viện `warnings` của Python để ghi log và trả về HTTP Header `Deprecation: true` kèm `Warning` để nhắc nhở client chuyển sang dùng v2.
3. **Breaking Changes (Thay đổi có khả năng gây lỗi client)**:
   - Trong `v1`: Object user có dạng `{"id": 1, "name": "Nguyen Van A"}`
   - Trong `v2`: Object user bị đổi cấu trúc thành `{"user_id": 1, "first_name": "Nguyen", "last_name": "Van A"}`. Client đang gọi v1 nếu chuyển sang v2 mà không cập nhật lại code đọc dữ liệu sẽ bị lỗi (do không tìm thấy trường `id` hay `name` nữa).
   - Ngoài ra v2 cũng bọc payload kết quả vào trong một object chứa mảng `"data": [...]` thay vì trả về list trực tiếp như v1.

## Danh sách 5 Endpoints:

### Phiên bản V1 (Đang bị Deprecated)
- `GET /api/v1/users` : Lấy danh sách users theo format cũ.
- `GET /api/v1/users/<id>` : Lấy thông tin 1 user theo format cũ.

### Phiên bản V2 (Phiên bản mới nhất)
- `GET /api/v2/users` : Lấy danh sách users (format mới).
- `GET /api/v2/users/<id>` : Lấy thông tin 1 user (format mới).
- `POST /api/v2/users` : Tạo một user mới (yêu cầu gửi body JSON theo format mới chứa `first_name`, `last_name`).

## Cách chạy thử:

1. Cài đặt Flask nếu chưa có:
```bash
pip install flask
```

2. Chạy ứng dụng:
```bash
python app.py
```

3. Thử nghiệm trên Terminal (với cURL):

**Test v1 (xem header cảnh báo):**
```bash
curl -i http://127.0.0.1:5000/api/v1/users
```
*(Lưu ý header `Deprecation: true` trong kết quả)*

**Test v2:**
```bash
curl -i http://127.0.0.1:5000/api/v2/users
```
*(Lưu ý cấu trúc JSON trả về khác hoàn toàn)*

**Test tạo User mới bằng v2:**
```bash
curl -X POST http://127.0.0.1:5000/api/v2/users \
     -H "Content-Type: application/json" \
     -d "{\"first_name\": \"Le\", \"last_name\": \"Van C\", \"email\": \"c@example.com\"}"
```

**Test Versioning qua Header:**
```bash
# Lấy v1 (mặc định nếu không truyền hoặc truyền 1)
curl -i http://127.0.0.1:5000/api/header/users

# Lấy v2 (truyền header X-API-Version: 2)
curl -i -H "X-API-Version: 2" http://127.0.0.1:5000/api/header/users
```

**Test Versioning qua Query Parameter:**
```bash
# Lấy v1
curl -i http://127.0.0.1:5000/api/query/users?version=1

# Lấy v2
curl -i http://127.0.0.1:5000/api/query/users?version=2
```
