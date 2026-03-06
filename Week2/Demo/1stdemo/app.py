from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

# Giả lập Database trong bộ nhớ (In-memory)
books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "status": "available"},
    {"id": 2, "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "status": "available"},
    {"id": 3, "title": "Refactoring", "author": "Martin Fowler", "status": "borrowed"}
]

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
def get_all_books():
    # Trả về một object bọc ngoài (envelope) để Client dễ mở rộng sau này
    return jsonify({
        "status": "success",
        "data": books,
        "total": len(books)
    })

# 2. Lấy thông tin chi tiết 1 cuốn sách
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if book:
        return jsonify({"status": "success", "data": book})
    return not_found(None)

# 3. Thêm một cuốn sách mới
@app.route('/books', methods=['POST'])
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
    return jsonify(new_book), 201

# 4. Cập nhật thông tin sách
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return not_found(None)
    
    data = request.json
    book.update(data)
    return jsonify(book)

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    original_length = len(books)
    books = [b for b in books if b['id'] != book_id]
    
    if len(books) < original_length:
        return jsonify({"status": "success", "message": f"Deleted book {book_id}"})
    return not_found(None)

if __name__ == '__main__':
    app.run(debug=True, port=5000)