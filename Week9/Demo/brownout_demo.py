from flask import Flask, Blueprint, jsonify
import datetime

v1_blueprint = Blueprint('v1', __name__, url_prefix='/api/v1')

@v1_blueprint.before_request
def check_brownout_schedule():
    now = datetime.datetime.now()

    # Tắt API v1 vào mỗi sáng Thứ Hai (weekday 0), từ 02:00 - 04:00 AM
    if now.weekday() == 0 and 2 <= now.hour <= 4:
        return jsonify({
            "error": "API_V1_DEPRECATED_BROWNOUT",
            "message": "V1 is currently down for scheduled brownout. Please migrate to V2.",
            "migration_guide": "https://api.uet.vn/v2/docs"
        }), 503 # HTTP 503 (Service Unavailable)

# API Logic
@v1_blueprint.route('/users')
def get_users_v1():
    return jsonify({"message": "Danh sách user (v1) - Gọi ngoài khung giờ Brownout nên vẫn chạy!"})

app = Flask(__name__)
app.register_blueprint(v1_blueprint)

if __name__ == '__main__':
    app.run()
