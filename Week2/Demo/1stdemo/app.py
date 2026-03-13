from flask import Flask, jsonify, request, make_response, url_for
from functools import wraps
import hashlib
import json
import jwt
import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = '15086677'

users = [
    {"id": 1, "username": "admin", "password": "password123"},
    {"id": 2, "username": "student", "password": "123"}
]

books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "status": "available"},
    {"id": 2, "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "status": "available"},
    {"id": 3, "title": "Refactoring", "author": "Martin Fowler", "status": "borrowed"}
]

# Xác thực JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]

        if not token:
            return make_response(jsonify({'message': 'Thiếu Token! Vui lòng đăng nhập.'}), 401)

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])

        except jwt.ExpiredSignatureError:
            return make_response(jsonify({'message': 'Token đã hết hạn! Vui lòng đăng nhập lại.'}), 401)
        except jwt.InvalidTokenError:
            return make_response(jsonify({'message': 'Token không hợp lệ!'}), 401)

        return f(*args, **kwargs)
    return decorated

def get_book_links(book_id):
    return {
        "self": url_for('get_book', book_id=book_id, _external=True),
        "update": url_for('update_book', book_id=book_id, _external=True),
        "delete": url_for('delete_book', book_id=book_id, _external=True)
    }

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({
        "status": "error",
        "message": "Resource not found"
    }), 404)

@app.errorhandler(405)
def method_not_allowed(error):
    return make_response(jsonify({
        "status": "error",
        "message": "Method not allowed"
    }), 405)

@app.errorhandler(500)
def internal_server_error(error):
    return make_response(jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500)


@app.route('/')
def home():
    return jsonify({
        "api_name": "Smart Book API",
        "version": "2.0",
        "constraints_satisfied": ["Client-Server"]
    })

# Login và tạo JWT token
@app.route('/login', methods=['POST'])
def login():
    auth_data = request.json
    if not auth_data or not auth_data.get('username') or not auth_data.get('password'):
        return make_response(jsonify({'message': 'Thiếu thông tin đăng nhập'}), 400)

    user = next((u for u in users if u['username'] == auth_data.get('username')), None)

    if user and user['password'] == auth_data.get('password'):

        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'message': 'Đăng nhập thành công', 'token': token})

    return make_response(jsonify({'message': 'Sai tài khoản hoặc mật khẩu'}), 401)

@app.route('/books', methods=['GET'])
@token_required
def get_all_books():
    data_with_links = []
    for book in books:
        book_copy = book.copy()
        book_copy['_links'] = get_book_links(book['id'])
        data_with_links.append(book_copy)

    content = jsonify({"status": "success", "data": data_with_links, "total": len(books)})

    response = make_response(content)
    response.headers['Cache-Control'] = 'public, max-age=60'
    return response

@app.route('/books/<int:book_id>', methods=['GET'])
@token_required
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return make_response(jsonify({"status": "error", "message": "Not found"}), 404)
    
    res_data = book.copy()
    res_data['_links'] = get_book_links(book_id)
    
    etag = hashlib.md5(json.dumps(res_data, sort_keys=True).encode()).hexdigest()
    if request.headers.get('If-None-Match') == etag:
        return make_response('', 304) 

    response = make_response(jsonify({"status": "success", "data": res_data}))
    response.set_etag(etag)
    response.headers['Cache-Control'] = 'public, max-age=120'
    return response

@app.route('/books', methods=['POST'])
@token_required
def add_book():
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

    response_data = new_book.copy()
    response_data['_links'] = get_book_links(new_book["id"])
    return jsonify({"status": "success", "data": response_data}), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
@token_required
def update_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return not_found(None)
    
    book.update(request.json)
    res = book.copy()
    res['_links'] = get_book_links(book_id)
    return jsonify({"status": "success", "data": res})

@app.route('/books/<int:book_id>', methods=['DELETE'])
@token_required
def delete_book(book_id):
    global books
    original_length = len(books)
    books = [b for b in books if b['id'] != book_id]
    
    if len(books) < original_length:
        return jsonify({"status": "success", "message": f"Deleted book {book_id}"})
    return not_found(None)

if __name__ == '__main__':
    app.run(debug=True, port=5000)