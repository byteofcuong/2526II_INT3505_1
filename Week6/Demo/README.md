## HƯỚNG DẪN TEST POSTMAN:

### Bước 1: Login
- POST http://127.0.0.1:5000/login
- Body (JSON): {"username": "user1", "password": "123"}
- Nhận kết quả: `access_token` trên màn hình JSON. Bạn bấm tab "Cookies" của Postman sẽ thấy `csrf_refresh_token` và `refresh_token_cookie` đang bị ẩn (HttpOnly).
- Copy `access_token` để xài.

### Bước 2: Request tài nguyên bảo vệ
- GET http://127.0.0.1:5000/protected
- Tab Authorization -> Type: Bearer Token -> Paste `access_token` vào.
- Test Route Admin: GET http://127.0.0.1:5000/admin -> Sẽ báo lỗi "Lỗi 403 cấm vào".

### Bước 3: Đợi 1 phút Token hết hạn
- Vẫn dùng Bearer token trên, gửi lại GET /protected. 
- Sẽ thấy thông báo lỗi chuẩn "Token đã hết hạn 1 phút".

### Bước 4: Rotating Refresh Token
- POST http://127.0.0.1:5000/refresh
- Không cần Authorization header, vì Postman TỰ ĐỘNG gửi theo HttpOnly Cookie từ bước đăng nhập!
- Nhận `access_token` mới tinh.
- Nhìn ở tab Cookie hệ thống cũng báo được set một cookie Refresh Token vòng tròn mới.

### Bước 5: Logout
- POST http://127.0.0.1:5000/logout với header là token hiện tại. Token ngay lập tức bị liệt vào Blacklist.