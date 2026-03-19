from flask import request, jsonify, make_response
from functools import wraps
import jwt
from config import SECRET_KEY

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
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return make_response(jsonify({'message': 'Token đã hết hạn! Vui lòng đăng nhập lại.'}), 401)
        except jwt.InvalidTokenError:
            return make_response(jsonify({'message': 'Token không hợp lệ!'}), 401)

        return f(current_user_id, *args, **kwargs)
    return decorated
