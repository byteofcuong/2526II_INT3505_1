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

---

## 3. Sinh code (Code Generation) bài bản cho RAML

Hệ sinh thái sinh code của RAML hiện yếu hơn OpenAPI rất nhiều. Giải pháp đúng đắn và thực tiễn nhất là làm theo 2 bước: chuyển đổi cấu trúc RAML sang chuẩn OpenAPI, sau đó mới tiến hành sinh source code bằng thư viện của OpenAPI.

Dưới đây là các lệnh cụ thể bạn cần chạy trực tiếp trên terminal (bạn chạy lệnh theo từng bước để hiểu bản chất nhé):

**Bước 1: Chuyển đổi file RAML sang bản đồ OpenAPI 3.0**
Sử dụng công cụ `oas-raml-converter` để dịch file `api.raml` thành `openapi.yaml`. Tính chất của PowerShell trên Windows có một "cú lừa" là tự đổi chuẩn encode, nên hãy copy lệnh dưới đây thật cẩn thận:

*(⚠️ **Lưu ý quan trọng**: Công cụ sinh code của Java chỉ đọc được chuẩn `UTF-8`. Nếu dùng ký hiệu `>` mặc định trong PowerShell, nó sẽ tạo file `UTF-16LE` và gây ra lỗi `special characters are not allowed`! Bắt buộc phải dùng `Out-File -Encoding utf8` trên Windows).*

```bash
# 👉 Nếu bạn dùng Windows (PowerShell):
npx oas-raml-converter --from RAML --to OAS30 api.raml | Out-File -Encoding utf8 openapi.yaml

# 👉 Nếu bạn dùng Mac/Linux (hoặc Git Bash):
npx oas-raml-converter --from RAML --to OAS30 api.raml > openapi.yaml
```

**Bước 2: Sinh Source Code bằng sức mạnh của OpenAPI Generator**
Bây giờ có `openapi.yaml` rồi, bạn chỉ việc dùng CLI sinh ra ngôn ngữ gì cũng được. Ví dụ sinh ra Python Client vào thư mục `/code-generation/python-client`:

```bash
npx @openapitools/openapi-generator-cli generate -i openapi.yaml -g python -o ./code-generation/python-client
```

*(Nếu bạn muốn code Java hay Nodejs thì chỉ việc thay `-g python` bằng `-g java` là xong!)*
