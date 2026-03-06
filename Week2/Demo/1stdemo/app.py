from flask import Flask, jsonify, request

app = Flask(__name__)

# Giả lập Database trong bộ nhớ (In-memory)
books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "status": "available"},
    {"id": 2, "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "status": "available"},
    {"id": 3, "title": "Refactoring", "author": "Martin Fowler", "status": "borrowed"}
]

@app.route('/')
def home():
    return {
        "message": "Chào mừng bạn đến với Smart Book API!",
        "check_books_url": "/books"
    }

# 1. Lấy danh sách toàn bộ sách
@app.route('/books', methods=['GET'])
def get_all_books():
    return jsonify(books)

# 2. Lấy thông tin chi tiết 1 cuốn sách
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if book:
        return jsonify(book)
    return jsonify({"error": "Không tìm thấy sách"}), 404

# 3. Thêm một cuốn sách mới
@app.route('/books', methods=['POST'])
def add_book():
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
        return jsonify({"error": "Không tìm thấy sách"}), 404
    
    data = request.json
    book.update(data)
    return jsonify(book)

# 5. Xóa một cuốn sách
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    books = [b for b in books if b['id'] != book_id]
    return jsonify({"message": f"Đã xóa sách ID {book_id} thành công"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)