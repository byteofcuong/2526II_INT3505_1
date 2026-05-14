from flask import Flask, Blueprint, jsonify

app = Flask(__name__)

# V1 (Legacy)
v1_blueprint = Blueprint('v1', __name__, url_prefix='/api/v1')

@v1_blueprint.route('/users', methods=['GET'])
def get_users_v1():
    # V1 có thể giữ nguyên code cũ, import thư viện cũ
    return jsonify({"version": "v1", "users": ["Alice", "Bob"]})

# V2 (Sandbox/New)
v2_blueprint = Blueprint('v2', __name__, url_prefix='/api/v2')

@v2_blueprint.route('/users', methods=['GET'])
def get_users_v2():
    # V2 có thể viết lại toàn bộ logic, dùng thư viện mới, model mới
    return jsonify({
        "version": "v2", 
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"}, 
            {"id": 2, "name": "Bob", "role": "user"}
        ]
    })

app.register_blueprint(v1_blueprint)
app.register_blueprint(v2_blueprint)

if __name__ == '__main__':
    print("Running Parallel via Flask Blueprint on port 5013...")
    print("V1: http://localhost:5013/api/v1/users")
    print("V2: http://localhost:5013/api/v2/users")
    app.run(port=5013, debug=True)
