# API Blueprint

Cần Node.js

npm install -g aglio\
aglio -i api.apib -o docs.html\
aglio -i api.apib --server

---

## Demo Mock Server và Test API Blueprint

Để tạo server giả lập và test tự động cho file `.apib`, chúng ta dùng công cụ **Drakov**.

**Bước 1:** Cài đặt Drakov và khởi động mock server (chạy ở port 4010)
```bash
npm install -g drakov
drakov -f api.apib -p 4010
```

**Bước 2:** Chạy script test
Giữ nguyên cửa sổ chạy Drakov, mở một terminal mới và trỏ đến thư mục chứa file test `test_api.py` của OpenAPI sau đó chạy:
```bash
cd ../0_OpenAPI/code-generation
pip install requests
python test_api.py
```

---

## Demo Sinh Code từ API Blueprint

**Convert API Blueprint**
```bash
npm install -g apib2swagger
apib2swagger -i api.apib -o swagger.json
```

**Dùng OpenAPI để đẻ ra code Backend**
```bash
npx @openapitools/openapi-generator-cli generate -i swagger.json -g python-flask -o ./generated-server
```

Mở http://localhost:3000

## Bê UI của Swagger lên máy cá nhân
```bash
npx swagger-ui-watcher swagger.json
```