# Demo: Sinh code và test từ OpenAPI spec

## 1. Khởi động mock server với Prism

npx @stoplight/prism-cli mock ../api.yaml

Server chạy tại `http://localhost:4010`

curl http://localhost:4010/books


---

## 2. Sinh server code với openapi-generator

npx @openapitools/openapi-generator-cli generate -i ../api.yaml -g python-flask -o ./generated-server

Code sinh ra nằm trong thư mục `generated-server/`

---

## 3. Chạy test tự động

pip install requests
python test_api.py

