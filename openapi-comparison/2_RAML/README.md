# RAML 1.0

Cần Node.js

npm install -g raml2html\
raml2html api.raml > docs.html


Mở file `docs.html` trong trình duyệt

---

## 2. Demo Mock Server và Test RAML

Để tạo server giả lập và test tự động cho file `.raml`, chúng ta dùng công cụ **osprey-mock-service** (tool kinh điển cho hệ sinh thái RAML).

**Bước 1:** Cài đặt và khởi động mock server (chạy ở port 4010)
```bash
npm install -g osprey-mock-service
osprey-mock-service -f api.raml -p 4010
```

**Bước 2:** Chạy script test
Giữ cửa sổ chạy server, mở một terminal mới và trỏ đến thư mục chứa file test `test_api.py` của OpenAPI, sau đó kiểm tra thử:
```bash
cd ../0_OpenAPI/code-generation
python test_api.py
```
*(Bạn cũng sẽ thấy output báo server RAML đã trả về mã HTTP 200/201 thành công cho 5 API giả lập)*
