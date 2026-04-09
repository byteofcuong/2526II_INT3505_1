import os
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, set_refresh_cookies,
    unset_jwt_cookies, get_jwt
)

# Load biến môi trường
load_dotenv()

app = Flask(__name__)

# 1. CẤU HÌNH JWT (Tương ứng các ràng buộc về Token)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "mat-khau-bi-mat-sieucap-123456")
app.config["JWT_ALGORITHM"] = "HS256" # Chỉ định HS256 làm thuật toán mã hóa (Step 4)

# Cấu hình thời hạn
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=1)    # Hết hạn trong 1 phút
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(minutes=30)  # Hết hạn trong 30 phút

# Cấu hình định vị Token (Access Token truyền ở header, Refresh Token gửi qua Cookie)
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = False  # Demo: Cho phép HttpOnly cookie ở môi trường HTTP (localhost). Lên Product cần True
app.config["JWT_COOKIE_CSRF_PROTECT"] = False # Demo: Tạm tắt để dễ test Postman (Thực tế nên bật chống CSRF)

jwt = JWTManager(app)

# Blocklist in-memory để chứa chữ kí token (jti) đã bị thu hồi
# Cảnh báo: Trong ứng dụng thực tế, nên dùng Redis hoặc Database để lưu trữ.
BLOCKLIST = set()


# 2. XỬ LÝ LỖI CALLBACKS (Step 4)
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    # Kiểm tra jti của token đang nằm trong Blocklist không
    return jwt_payload["jti"] in BLOCKLIST

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "Token đã hết hạn 1 phút. Vui lòng gọi /refresh.", "error": "token_expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"msg": "Token bị lỗi chữ ký hoặc không hợp lệ.", "error": "invalid_token"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"msg": "Không tìm thấy token trong request Header.", "error": "authorization_required"}), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "Token đã bị thu hồi (Logged out / Revoked).", "error": "token_revoked"}), 401


# MOCK DATABASE
USERS = {
    "user1": {"password": "123", "role": "user", "scopes": ["read:items"]},
    "admin1": {"password": "admin", "role": "admin", "scopes": ["read:items", "write:items", "delete:items"]}
}


# ==========================================================
# 3. ENDPOINTS
# ==========================================================

@app.route("/login", methods=["POST"])
def login():
    """ Đăng nhập: Trả về Access trong Body Json, Refresh set vào Cookie """
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if username not in USERS or USERS[username]["password"] != password:
        return jsonify({"msg": "Username hoặc password sai"}), 401

    user_info = USERS[username]
    # Tạo custom claims (roles / scopes) theo yêu cầu 
    additional_claims = {
        "role": user_info["role"], 
        "scopes": user_info["scopes"]
    }

    access_token = create_access_token(identity=username, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=username)

    response = jsonify({
        "msg": "Đăng nhập thành công",
        "access_token": access_token
    })
    # Gán HttpOnly Cookie cho response chứa refresh token
    set_refresh_cookies(response, refresh_token)
    
    return response, 200


@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True) # Chỉ định function này ĐÒI HỎI refresh_token (nằm trong HTTP cookie)
def refresh():
    """ Kĩ thuật Refresh Token Rotation: Xoá thẻ cũ, cấp thẻ mới tránh thẻ tĩnh """
    identity = get_jwt_identity()
    old_jti = get_jwt()["jti"]
    
    # 1. Thu hồi JTI cũ (vào sổ đen)
    BLOCKLIST.add(old_jti)

    # 2. Cấp lại thông tin (Custom Claims)
    user_info = USERS[identity]
    additional_claims = {"role": user_info["role"], "scopes": user_info["scopes"]}

    # 3. Ký cặp Token mới
    new_access_token = create_access_token(identity=identity, additional_claims=additional_claims)
    new_refresh_token = create_refresh_token(identity=identity)

    # 4. Trả về cho client
    response = jsonify({
        "msg": "Làm mới (Refresh) token thành công, jti cũ bị block.",
        "access_token": new_access_token
    })
    set_refresh_cookies(response, new_refresh_token)

    return response, 200


@app.route("/protected", methods=["GET"])
@jwt_required() # Đòi hỏi Access Token (gửi qua Header: Authorization -> Bearer <token>)
def protected():
    """ Route bảo vệ cho user bất kỳ có valid token """
    current_user = get_jwt_identity()
    claims = get_jwt()  # Lấy chi tiết Payload của Token
    
    return jsonify({
        "msg": f"Truy cập lấy data thành công với username là {current_user}",
        "roles": claims.get("role"),
        "scopes": claims.get("scopes")
    }), 200


@app.route("/admin", methods=["GET"])
@jwt_required()
def admin_only():
    """ Route chỉ với ROLE: Admin """
    claims = get_jwt()
    # Kiểm tra authorization
    if claims.get("role") != "admin":
        return jsonify({"msg": "Lỗi 403 cấm vào. Chỉ có Admin mới được phép.", "error": "forbidden"}), 403
        
    return jsonify({"msg": "Chào mừng quản lý Admin!"}), 200


@app.route("/logout", methods=["POST"])
@jwt_required() # Cầm Access Token tới đây để báo log out
def logout():
    """ Logout thu hồi token bằng blacklist jti """
    token_jti = get_jwt()["jti"]
    
    # Set vào Blacklist để không xài lại Access Token cũ
    BLOCKLIST.add(token_jti)
    
    # Đồng thời báo browser xoá HttpOnly Cookie của RefreshToken
    response = jsonify({"msg": "Đã thu hồi access token cũ và xoá refresh. Đăng xuất thành công."})
    unset_jwt_cookies(response)
    return response, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
