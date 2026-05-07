from flask import Flask, jsonify, request
import warnings

app = Flask(__name__)

users_db = [
    {"id": 1, "name": "Nguyen Van A", "email": "a@example.com"},
    {"id": 2, "name": "Tran Thi B", "email": "b@example.com"}
]

# API VERSION 1 (Deprecated

@app.route('/api/v1/users', methods=['GET'])
def get_users_v1():
    """
    Lấy danh sách người dùng.
    API này đã bị DEPRECATED.
    """
    # 1. Ghi log cảnh báo ở server
    warnings.warn("Endpoint /api/v1/users is deprecated. Please use /api/v2/users", DeprecationWarning)
    
    response = jsonify({"users": users_db})
    
    # 2. Thêm header cảnh báo cho client biết API đã cũ
    response.headers['Deprecation'] = 'true'
    response.headers['Warning'] = '199 - "Deprecated API: This endpoint will be removed in the future. Use v2 instead."'
    return response

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user_v1(user_id):
    """
    Lấy thông tin một người dùng theo ID.
    API này đã bị DEPRECATED.
    """
    warnings.warn(f"Endpoint /api/v1/users/{user_id} is deprecated. Please use v2.", DeprecationWarning)
    
    user = next((u for u in users_db if u["id"] == user_id), None)
    if user:
        response = jsonify(user)
        response.headers['Deprecation'] = 'true'
        return response
    return jsonify({"error": "User not found"}), 404


# API VERSION 2 (Current)
# Mô phỏng BREAKING CHANGES
# 1. Trường 'id' đổi tên thành 'user_id'
# 2. Trường 'name' bị tách thành 'first_name' và 'last_name'
# 3. Response payload được bọc trong một object 'data'

def transform_user_to_v2(user):
    """Hàm helper để chuyển đổi dữ liệu từ DB (format v1) sang format v2"""
    name_parts = user["name"].split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""
    return {
        "user_id": user["id"],  # Breaking change: id -> user_id
        "first_name": first_name, # Breaking change: name -> first_name, last_name
        "last_name": last_name,
        "email": user["email"]
    }

@app.route('/api/v2/users', methods=['GET'])
def get_users_v2():
    """
    Lấy danh sách người dùng (Phiên bản mới).
    """
    v2_users = [transform_user_to_v2(u) for u in users_db]
    # Breaking change: bọc kết quả vào thuộc tính 'data'
    return jsonify({
        "data": v2_users, 
        "version": "v2",
        "meta": {"total": len(v2_users)}
    })

@app.route('/api/v2/users/<int:user_id>', methods=['GET'])
def get_user_v2(user_id):
    """
    Lấy thông tin một người dùng theo ID (Phiên bản mới).
    """
    user = next((u for u in users_db if u["id"] == user_id), None)
    if user:
        return jsonify({"data": transform_user_to_v2(user)})
    return jsonify({"error": "User not found"}), 404

@app.route('/api/v2/users', methods=['POST'])
def create_user_v2():
    """
    Tạo người dùng mới. Yêu cầu format theo v2 (truyền first_name, last_name).
    """
    data = request.get_json()
    if not data or not 'first_name' in data or not 'email' in data:
        return jsonify({"error": "Missing required fields (first_name, email)"}), 400
    
    new_id = max(u["id"] for u in users_db) + 1 if users_db else 1
    
    # Lưu vào database theo format cũ (giả lập DB chưa đổi schema)
    last_name = data.get('last_name', '')
    full_name = f"{data['first_name']} {last_name}".strip()
    
    new_user = {
        "id": new_id,
        "name": full_name,
        "email": data['email']
    }
    users_db.append(new_user)
    
    return jsonify({
        "message": "User created successfully",
        "data": transform_user_to_v2(new_user)
    }), 201

# VERSIONING BẰNG HEADER & QUERY PARAM

@app.route('/api/header/users', methods=['GET'])
def get_users_by_header():
    """
    Demo Versioning thông qua Custom Header: 'X-API-Version'
    """
    version = request.headers.get('X-API-Version', '1') # Mặc định là v1
    
    if version == '1':
        return jsonify({"users": users_db})
    elif version == '2':
        v2_users = [transform_user_to_v2(u) for u in users_db]
        return jsonify({"data": v2_users, "version": "v2"})
    return jsonify({"error": "Unsupported API Version"}), 400

@app.route('/api/query/users', methods=['GET'])
def get_users_by_query():
    """
    Demo Versioning thông qua Query Parameter: '?version=1'
    """
    version = request.args.get('version', '1') # Mặc định là v1
    
    if version == '1':
        return jsonify({"users": users_db})
    elif version == '2':
        v2_users = [transform_user_to_v2(u) for u in users_db]
        return jsonify({"data": v2_users, "version": "v2"})
    return jsonify({"error": "Unsupported API Version"}), 400

if __name__ == '__main__':
    print("Server is running at http://127.0.0.1:5000")
    print("Các chiến lược versioning demo:")
    print("1. URL (V1): http://127.0.0.1:5000/api/v1/users")
    print("   URL (V2): http://127.0.0.1:5000/api/v2/users")
    print("2. Header : http://127.0.0.1:5000/api/header/users (Kèm Header X-API-Version: 1 hoặc 2)")
    print("3. Query  : http://127.0.0.1:5000/api/query/users?version=1 hoặc ?version=2")
    app.run(debug=True, port=5000)
