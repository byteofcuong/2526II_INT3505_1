from flask import Flask, jsonify

app = Flask(__name__)

new_core_db = [
    {"user_id": 1, "first_name": "Nguyen", "last_name": "A"},
    {"user_id": 2, "first_name": "Tran", "last_name": "B"}
]

# 1. API v2 trả về trực tiếp format mới
@app.route('/api/v2/users')
def get_users_v2():
    return jsonify({"data": new_core_db})

# 2. ADAPTER (Contract Bridge): Chuyển đổi V2 -> V1
def user_v2_to_v1_adapter(user_v2):
    return {
        "id": user_v2["user_id"],
        "name": f"{user_v2['first_name']} {user_v2['last_name']}"
    }

# 3. API v1 vẫn giữ nguyên Contract nhờ Adapter
@app.route('/api/v1/users')
def get_users_v1():
    # Client cũ không bị crash vì Adapter đã xử lý sự khác biệt
    users_v1 = [user_v2_to_v1_adapter(u) for u in new_core_db]
    return jsonify({"users": users_v1})

if __name__ == '__main__':
    app.run()

