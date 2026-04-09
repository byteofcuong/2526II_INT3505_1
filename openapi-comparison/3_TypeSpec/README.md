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
