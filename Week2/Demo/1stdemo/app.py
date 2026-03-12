from flask import Flask, jsonify, request, make_response, url_for
from functools import wraps

app = Flask(__name__)

# Cấu hình API Key giả lập (Trong thực tế sẽ lưu ở DB hoặc Env)
VALID_API_KEY = "secret-123"

# Giả lập Database trong bộ nhớ (In-memory)
books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "status": "available"},
    {"id": 2, "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "status": "available"},
    {"id": 3, "title": "Refactoring", "author": "Martin Fowler", "status": "borrowed"}
]

# RÀNG BUỘC: STATELESS (XÁC THỰC QUA HEADER)
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Server không dùng Session, mà kiểm tra Header trong MỖI request
        api_key = request.headers.get('X-API-KEY')
        if api_key and api_key == VALID_API_KEY:
            return f(*args, **kwargs)
        
        # Nếu không có key hoặc sai key, trả về 401 Unauthorized
        return make_response(jsonify({
            "status": "error",
            "message": "Unauthorized: Bạn cần cung cấp API Key hợp lệ trong Header 'X-API-KEY'"
        }), 401)
    return decorated_function

# --- HELPER FUNCTION: TẠO HATEOAS LINKS ---
def get_book_links(book_id):
    """Tạo các liên kết điều hướng cho một cuốn sách cụ thể"""
    return {
        "self": url_for('get_book', book_id=book_id, _external=True),
        "update": url_for('update_book', book_id=book_id, _external=True),
        "delete": url_for('delete_book', book_id=book_id, _external=True)
    }

# --- PHẦN 1: ĐẢM BẢO CHUẨN CLIENT-SERVER QUA ERROR HANDLERS ---
# Bất kể lỗi gì xảy ra, Server đều trả về cấu trúc JSON nhất quán.

@app.errorhandler(404)
def not_found(error):
    """Xử lý lỗi không tìm thấy tài nguyên (URL sai hoặc ID không tồn tại)"""
    return make_response(jsonify({
        "status": "error",
        "message": "Resource not found"
    }), 404)

@app.errorhandler(405)
def method_not_allowed(error):
    """Xử lý lỗi dùng sai phương thức HTTP (VD: Dùng GET cho route chỉ nhận POST)"""
    return make_response(jsonify({
        "status": "error",
        "message": "Method not allowed"
    }), 405)

@app.errorhandler(500)
def internal_server_error(error):
    """Xử lý lỗi hệ thống"""
    return make_response(jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500)


# --- PHẦN 2: CÁC API ENDPOINTS ---

@app.route('/')
def home():
    # Ngay cả trang chủ cũng trả về JSON thay vì String/HTML
    return jsonify({
        "api_name": "Smart Book API",
        "version": "2.0",
        "constraints_satisfied": ["Client-Server"]
    })

# 1. Lấy danh sách toàn bộ sách
@app.route('/books', methods=['GET'])
@require_api_key
def get_all_books():
    # Thêm links cho từng cuốn sách trong danh sách
    data_with_links = []
    for book in books:
        book_copy = book.copy()
        book_copy['_links'] = get_book_links(book['id'])
        data_with_links.append(book_copy)

    # Trả về một object bọc ngoài (envelope) để Client dễ mở rộng sau này
    return jsonify({
        "status": "success",
        "data": books,
        "total": len(books)
    })

# 2. Lấy thông tin chi tiết 1 cuốn sách
@app.route('/books/<int:book_id>', methods=['GET'])
@require_api_key
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if book:
        return jsonify({"status": "success", "data": book})
    return not_found(None)

# 3. Thêm một cuốn sách mới
@app.route('/books', methods=['POST'])
@require_api_key
def add_book():
# Kiểm tra dữ liệu đầu vào từ Client
    if not request.json or 'title' not in request.json:
        return make_response(jsonify({
            "status": "error", 
            "message": "Missing required field: title"
        }), 400)

    data = request.json
    new_book = {
        "id": len(books) + 1,
        "title": data.get("title"),
        "author": data.get("author"),
        "status": "available"
    }
    books.append(new_book)

    # Trả về kèm link của chính tài nguyên vừa tạo
    response_data = new_book.copy()
    response_data['_links'] = get_book_links(new_book["id"])
    return jsonify({"status": "success", "data": response_data}), 201

# 4. Cập nhật thông tin sách
@app.route('/books/<int:book_id>', methods=['PUT'])
@require_api_key
def update_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return not_found(None)
    
    book.update(request.json)
    res = book.copy()
    res['_links'] = get_book_links(book_id)
    return jsonify({"status": "success", "data": res})

@app.route('/books/<int:book_id>', methods=['DELETE'])
@require_api_key
def delete_book(book_id):
    global books
    original_length = len(books)
    books = [b for b in books if b['id'] != book_id]
    
    if len(books) < original_length:
        return jsonify({"status": "success", "message": f"Deleted book {book_id}"})
    return not_found(None)

if __name__ == '__main__':
    app.run(debug=True, port=5000)