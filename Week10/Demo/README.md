# Demo Task List API với JSON Logging

Đây là một ứng dụng Python Flask cung cấp các API endpoint cơ bản để quản lý một "Danh sách công việc" (Task List) và ghi log theo định dạng JSON có cấu trúc.

## Yêu cầu
- Python 3.x
- Pip (Python package manager)

## Cài đặt

1. Đi đến thư mục chứa ứng dụng:
   ```bash
   cd "d:\Direc of code\2526II_INT3505_1\Week10\Demo"
   ```

2. (Tùy chọn) Tạo và kích hoạt môi trường ảo (virtual environment):
   ```bash
   python -m venv venv
   # Nếu dùng Windows:
   venv\Scripts\activate
   # Nếu dùng macOS/Linux:
   source venv/bin/activate
   ```

3. Cài đặt các thư viện yêu cầu:
   ```bash
   pip install -r requirements.txt
   ```

## Khởi chạy ứng dụng

Chạy ứng dụng Flask bằng lệnh:
```bash
python app.py
```
Ứng dụng sẽ chạy tại địa chỉ `http://127.0.0.1:5000/`.

## Các Endpoints (API)

| Phương thức | Đường dẫn | Mô tả |
| --- | --- | --- |
| `GET` | `/health` | Kiểm tra trạng thái của API |
| `GET` | `/tasks` | Lấy danh sách tất cả các công việc |
| `POST` | `/tasks` | Tạo một công việc mới |
| `GET` | `/tasks/<id>` | Lấy thông tin chi tiết một công việc |
| `PUT` | `/tasks/<id>` | Cập nhật một công việc đã có |
| `DELETE` | `/tasks/<id>` | Xóa một công việc |

## Hướng dẫn Kiểm tra (Testing)

Bạn có thể sử dụng **cURL**, **Postman**, hoặc **Thunder Client** để kiểm tra các API. Dưới đây là các lệnh cURL mẫu (chạy trong Command Prompt hoặc PowerShell):

### 1. Kiểm tra Health
```bash
curl -X GET http://127.0.0.1:5000/health
```

### 2. Tạo công việc mới (POST /tasks)
```bash
curl -X POST http://127.0.0.1:5000/tasks -H "Content-Type: application/json" -d "{\"title\": \"Học Flask\", \"completed\": false}"
```

### 3. Lấy danh sách công việc (GET /tasks)
```bash
curl -X GET http://127.0.0.1:5000/tasks
```

### 4. Lấy chi tiết công việc (GET /tasks/<id>)
*(Ví dụ với id = 1)*
```bash
curl -X GET http://127.0.0.1:5000/tasks/1
```

### 5. Cập nhật công việc (PUT /tasks/<id>)
```bash
curl -X PUT http://127.0.0.1:5000/tasks/1 -H "Content-Type: application/json" -d "{\"title\": \"Học Flask nâng cao\", \"completed\": true}"
```

### 6. Xóa công việc (DELETE /tasks/<id>)
```bash
curl -X DELETE http://127.0.0.1:5000/tasks/1
```

## Xem Log

Mỗi khi bạn gọi các API trên, ứng dụng sẽ tự động ghi log ra terminal dưới dạng JSON, sử dụng module native `logging` của Python thay vì format mặc định. Các log này đảm bảo chứa các thông tin:
- `timestamp`: Thời gian log
- `level`: Mức độ log (INFO, WARNING, ...)
- `message`: Nội dung log
- `method`: HTTP Method (GET, POST, ...)
- `path`: Đường dẫn API

Ví dụ log in ra ở terminal:
```json
{"timestamp": "2026-05-14T12:00:00+00:00", "level": "INFO", "message": "Handling request", "method": "GET", "path": "/tasks"}
{"timestamp": "2026-05-14T12:00:00+00:00", "level": "INFO", "message": "Task created with id: 1", "method": "POST", "path": "/tasks"}
```
