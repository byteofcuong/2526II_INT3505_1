import hashlib
import json
from functools import wraps
from flask import Flask, request, jsonify

app = Flask(__name__)

# Fake In-memory Database cho thư viện
books = [
    {'id': 1, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'year': 1925},
    {'id': 2, 'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'year': 1960}
]

# Một Master Token đơn giản để minh hoạ tính Stateless (không lưu session server)
API_TOKEN = "my-secret-token"

# --- HELPER FUNCTIONS ---

def require_auth(f):
    """
    Decorator dùng để kiểm tra Authentication.
    Minh hoạ tính Stateless:
    Mỗi request đều phải mang 'Authorization' header. 
    Server không hề biết trước tài khoản nào đang đăng nhập qua Cookie/Session.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        # Kiểm tra token dạng "Bearer <token>"
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized', 'message': 'Missing or invalid Authorization header. Expected "Bearer <token>"'}), 401
        
        token = auth_header.split(' ')[1]
        if token != API_TOKEN:
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

def generate_etag(data):
    """
    Sinh ETag dựa trên nội dung response.
    Giúp cho tính Cacheable của GET request.
    """
    # Ép sang string JSON ổn định (sort_keys=True) rồi băm bằng MD5
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.md5(data_str.encode('utf-8')).hexdigest()

def add_hateoas_links(book):
    """
    Minh hoạ tính Uniform Interface (HATEOAS).
    Thay vì để client phải tự ghép URL để tìm update, hay delete,
    Server sẽ nhúng thẳng những action object này vào response json.
    """
    base_url = f"/api/v1/books/{book['id']}"
    return {
        "self": base_url,
        "update": base_url,   # Call PUT to this URL
        "delete": base_url,   # Call DELETE to this URL
        "collection": "/api/v1/books" # Explore collection
    }

# --- 5 SCENARIOS (ENDPOINTS) ---

# Tình huống 1: Lấy danh sách (Client-Server & Cacheable thông qua Max-Age)
@app.route('/api/v1/books', methods=['GET'])
def get_books():
    """Lấy danh sách tất cả các sách"""
    # Uniform Interface: Response dạng application/json
    response = jsonify({
        'books': books, 
        'count': len(books)
    })
    
    # Demo Cacheable: Hướng dẫn client / Proxy có thể cache request này trong 60 giây
    response.headers['Cache-Control'] = 'public, max-age=60'
    return response, 200

# Tình huống 2: Lấy chi tiết sách (Uniform Interface & Cacheable thông qua ETag)
@app.route('/api/v1/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Lấy thông tin chi tiết một cuốn sách"""
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        # Uniform Interface: Status 404 chuẩn chỉ
        return jsonify({'error': 'Not Found', 'message': 'Book not found'}), 404
        
    # Tạo copy và nhúng HATEOAS (_links)
    output_book = book.copy()
    output_book['_links'] = add_hateoas_links(book)
    
    # Xử lý tính Cacheable ETag
    etag = generate_etag(output_book)
    if_none_match = request.headers.get('If-None-Match')
    
    # Nếu client gửi ETag cũ lên khớp với ETag hiện tại của book -> nghĩa là data chưa bị sửa gì
    # Ta tự tin trả về mã `304 Not Modified` ngay lập tức mà không load thêm body
    if if_none_match == etag:
        return '', 304

    # Response bình thường kèm thông tin ETag cho client lưu lần sau
    response = jsonify(output_book)
    response.set_etag(etag) 
    return response, 200

# Tình huống 3: Thêm sách mới (Stateless)
@app.route('/api/v1/books', methods=['POST'])
@require_auth  # Yêu cầu client cung cấp Auth token trong request
def create_book():
    """Tạo một cuốn sách mới"""
    data = request.get_json()
    if not data or 'title' not in data or 'author' not in data:
        return jsonify({'error': 'Bad Request', 'message': 'Title and author are required fields'}), 400
        
    new_id = max(b['id'] for b in books) + 1 if books else 1
    new_book = {
        'id': new_id,
        'title': data['title'],
        'author': data['author'],
        'year': data.get('year', None)
    }
    books.append(new_book)
    
    output_book = new_book.copy()
    output_book['_links'] = add_hateoas_links(new_book)
    
    # Uniform Interface: Response mã 201 Created kèm Header Location chỉ định nơi chứa tài nguyên mới
    response = jsonify(output_book)
    response.headers['Location'] = f"/api/v1/books/{new_id}"
    return response, 201

# Tình huống 4: Cập nhật sách (Stateless & Uniform Interface)
@app.route('/api/v1/books/<int:book_id>', methods=['PUT'])
@require_auth 
def update_book(book_id):
    """Cập nhật thông tin một cuốn sách (sử dụng PUT model update nguyên mảng)"""
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({'error': 'Not Found', 'message': 'Book not found'}), 404
        
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Bad Request', 'message': 'No JSON dictionary provided'}), 400
        
    # Cập nhật data
    book['title'] = data.get('title', book['title'])
    book['author'] = data.get('author', book['author'])
    book['year'] = data.get('year', book['year'])
    
    output_book = book.copy()
    output_book['_links'] = add_hateoas_links(book)
    
    # Uniform Interface: 200 OK
    return jsonify(output_book), 200

# Tình huống 5: Xóa sách (Stateless)
@app.route('/api/v1/books/<int:book_id>', methods=['DELETE'])
@require_auth
def delete_book(book_id):
    """Xóa một cuốn sách khỏi thư viện"""
    global books
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({'error': 'Not Found', 'message': 'Book not found'}), 404
        
    books = [b for b in books if b['id'] != book_id]
    
    # Uniform Interface: 204 No Content là cờ thành công tiêu chuẩn cho thao tác Xóa (Delete)
    # Vì ta không cần thiết phải trả về gì khi nội dung đã bay màu
    return '', 204

# Chạy server
if __name__ == '__main__':
    print("Library RESTful API Started!")
    app.run(host='0.0.0.0', port=5000, debug=True)
