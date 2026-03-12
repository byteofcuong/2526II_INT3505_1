from flask import request
from . import v1_bp
from .responses import wrap_response

users = [
    {"id": 1, "username": "nguyen_cuong", "email": "cuong@example.com"},
    {"id": 2, "username": "tran_an", "email": "an@example.com"}
]

@v1_bp.route('/users', methods=['GET'])
def get_users():
    return wrap_response(data=users)

@v1_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json
    if not data or 'username' not in data:
        return wrap_response(message="Thiếu thông tin username", status=400)
    
    new_user = {
        "id": len(users) + 1,
        "username": data['username'],
        "email": data.get('email', '')
    }
    users.append(new_user)
    return wrap_response(data=new_user, message="Tạo người dùng thành công", status=201)

@v1_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_detail(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return wrap_response(message="Không tìm thấy người dùng", status=404)
    return wrap_response(data=user)