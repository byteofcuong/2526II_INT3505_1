from flask import Flask, jsonify

app = Flask(__name__)

# ==========================================
# CORE BUSINESS LOGIC (Single Source of Truth)
# Chỉ duy trì một luồng logic xử lý dữ liệu duy nhất (mới nhất).
# ==========================================
def get_core_users():
    # Giả lập truy vấn Database ở cấu trúc mới nhất (V2)
    return [
        {"id": 1, "name": "Alice", "role": "admin", "email": "alice@demo.com"}, 
        {"id": 2, "name": "Bob", "role": "user", "email": "bob@demo.com"}
    ]

# ==========================================
# V2 ENDPOINT (Dùng trực tiếp Core Logic)
# ==========================================
@app.route('/api/v2/users', methods=['GET'])
def get_users_v2():
    users = get_core_users()
    return jsonify({
        "version": "v2", 
        "users": users
    })

# ==========================================
# V1 ADAPTER / CONTRACT BRIDGE (Cầu nối tương thích)
# ==========================================
@app.route('/api/v1/users', methods=['GET'])
def get_users_v1():
    # Bước 1: Gọi Core Logic (sẽ trả về cấu trúc V2 phức tạp)
    core_users = get_core_users()
    
    legacy_users = [user["name"] for user in core_users]
    
    return jsonify({
        "version": "v1", 
        "users": legacy_users
    })

if __name__ == '__main__':
    print("Running Adapter (Contract Bridge) Architecture on port 5014...")
    print("V1: http://localhost:5014/api/v1/users")
    print("V2: http://localhost:5014/api/v2/users")
    app.run(port=5014, debug=True)
