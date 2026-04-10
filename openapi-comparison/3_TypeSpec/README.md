# TypeSpec

Cần Node.js 


npm install\
npm run build

Output nằm ở `generated/openapi.yaml`

---

## 2. Demo Mock Server và Test TypeSpec

**Điểm đặc biệt ăn tiền:** TypeSpec sinh ra không phải để tự mình làm thêm một hệ sinh thái mock hay code generation yếu ớt. Nhiệm vụ của nó là compile code TypeScript cực sạch gọn **ra một file chuẩn OpenAPI**, rồi mượn toàn bộ 100% sức mạnh hệ sinh thái của OpenAPI (như Prism hay OpenAPI-Generator).

**Bước 1:** Chạy mock server bằng Prism nhưng dùng chính file OpenAPI mà TypeSpec vừa sinh ra (chạy trên port 4010):
```bash
npx @stoplight/prism-cli mock generated/openapi.yaml -p 4010
```

**Bước 2:** Chạy script test
Mở một terminal mới và trỏ đến thư mục chứa file test `test_api.py`, sau đó chạy:
```bash
cd ../0_OpenAPI/code-generation
python test_api.py
```

---

## 3. Sinh code (Code Generation) cho TypeSpec

TypeSpec mang đậm triết lý "Hãy tận dụng hệ sinh thái có sẵn". Bản thân Microsoft và Typespec không muốn tự build lại toàn bộ các công cụ gen code cho hàng tá ngôn ngữ. Thay vào đó quá trình sinh code diễn ra thông minh như sau:

**Bước 1: Biên dịch TypeSpec sang OAS tiêu chuẩn**
Lệnh `npm run build` (tùy chỉnh trong `package.json` để chạy `tsp compile .`) sử dụng emitter `@typespec/openapi3`. Kết quả cho ra file `generated/openapi.yaml` vạch rõ các endpoint, schema cực kỳ clean đằng sau thư mục `generated`.

**Bước 2: Kế thừa 100% công cụ sinh code của OpenAPI**
Vì chúng ta đã có file `openapi.yaml` xịn, lúc này TypeSpec có thể tận dụng hoàn toàn engine sinh code vĩ đại của OpenAPI.

Dưới đây là phương pháp bài bản. Bạn hãy chạy liên tiếp 2 lệnh cụ thể này trực tiếp trên terminal để hiểu rõ luồng thực thi:

```bash
# 1. Compile mã TypeSpec để tóm gọn nó ra file openapi.yaml
npx tsp compile .

# 2. Dùng sức mạnh của OpenAPI Generator đẻ ra toàn bộ logic code Python Client
npx @openapitools/openapi-generator-cli generate -i generated/openapi.yaml -g python -o ./code-generation/python-client
```

Cách làm chuẩn mực này rất tường minh: Vừa có bộ mã spec DRY cực cao nhờ compiler của TypeSpec, lại lập tức kế thừa trọn vẹn khả năng sinh code >50 ngôn ngữ khác nhau nhờ hệ sinh thái openapi.
