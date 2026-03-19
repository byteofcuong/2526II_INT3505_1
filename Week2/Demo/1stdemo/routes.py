from flask import Blueprint, jsonify, request, make_response, url_for
import hashlib
import json
import jwt
import datetime
from data import users, books
from auth import token_required
from config import SECRET_KEY

api_bp = Blueprint('api', __name__)

def get_book_links(book_id):
    return {
        "self": url_for('api.get_book', book_id=book_id, _external=True),
        "update": url_for('api.update_book', book_id=book_id, _external=True),
        "delete": url_for('api.delete_book', book_id=book_id, _external=True)
    }

@api_bp.route('/')
def home():
    return jsonify({
        "api_name": "Smart Book API",
        "version": "2.0",
        "constraints_satisfied": ["Client-Server"]
    })

@api_bp.route('/login', methods=['POST'])
def login():
    auth_data = request.json
    if not auth_data or not auth_data.get('username') or not auth_data.get('password'):
        return make_response(jsonify({'message': 'Thiếu thông tin đăng nhập'}), 400)

    user = next((u for u in users if u['username'] == auth_data.get('username')), None)

    if user and user['password'] == auth_data.get('password'):
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({'message': 'Đăng nhập thành công', 'token': token})

    return make_response(jsonify({'message': 'Sai tài khoản hoặc mật khẩu'}), 401)

@api_bp.route('/books', methods=['GET'])
@token_required
def get_all_books(current_user_id):
    data_with_links = []
    for book in books:
        book_copy = book.copy()
        book_copy['_links'] = get_book_links(book['id'])
        data_with_links.append(book_copy)

    content = jsonify({"status": "success", "data": data_with_links, "total": len(books)})

    response = make_response(content)
    response.headers['Cache-Control'] = 'public, max-age=60'
    return response

@api_bp.route('/books/<int:book_id>', methods=['GET'])
@token_required
def get_book(current_user_id, book_id):
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

@api_bp.route('/books', methods=['POST'])
@token_required
def add_book(current_user_id):
    if not request.json or 'title' not in request.json:
        return make_response(jsonify({"status": "error", "message": "Missing required field: title"}), 400)

    book_data = request.json
    new_book = {
        "id": len(books) + 1,
        "title": book_data.get("title"),
        "author": book_data.get("author"),
        "status": "available"
    }
    books.append(new_book)

    response_data = new_book.copy()
    response_data['_links'] = get_book_links(new_book["id"])
    return jsonify({"status": "success", "data": response_data}), 201

@api_bp.route('/books/<int:book_id>', methods=['PUT'])
@token_required
def update_book(current_user_id, book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return make_response(jsonify({
            "status": "error",
            "message": "Resource not found"
        }), 404)
    
    book.update(request.json)
    res = book.copy()
    res['_links'] = get_book_links(book_id)
    return jsonify({"status": "success", "data": res})

@api_bp.route('/books/<int:book_id>', methods=['DELETE'])
@token_required
def delete_book(current_user_id, book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if book:
        books.remove(book)
        return jsonify({"status": "success", "message": f"Deleted book {book_id}"})
    return make_response(jsonify({
        "status": "error",
        "message": "Resource not found"
    }), 404)
