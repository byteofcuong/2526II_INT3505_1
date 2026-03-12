from flask import Blueprint, jsonify, request

legacy_bp = Blueprint('legacy', __name__)

users = [
    {"id": 1, "name": "Nguyen Cuong", "role": "admin"},
    {"id": 2, "name": "Tran An", "role": "user"}
]

@legacy_bp.route('/addNewUser', methods=['GET'])
def add_user():
    """
    Lỗi: Tên có động từ 'add', dùng CamelCase.
    Lỗi: Dùng GET để tạo dữ liệu (Rất nguy hiểm vì GET có thể bị cache hoặc lưu log).
    """
    name = request.args.get('name')
    if name:
        new_id = len(users) + 1
        users.append({"id": new_id, "name": name})
        return f"User {name} đã được thêm thành công!"
    return "Thiếu tên rồi bạn ơi", 400


@legacy_bp.route('/get-all-users-in-database-api', methods=['GET'])
def get_all():
    return jsonify(users)


@legacy_bp.route('/getUser', methods=['POST'])
def get_one():
    user_id = request.json.get('id')
    user = next((u for u in users if u["id"] == user_id), None)
    
    if user:
        return {
            "status": "ok",
            "result": user
        }
    return {"status": "error", "msg": "Không thấy"}, 404