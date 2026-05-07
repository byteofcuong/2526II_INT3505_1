from flask import Flask, Blueprint, jsonify

v1_blueprint = Blueprint('v1', __name__, url_prefix='/api/v1')

@v1_blueprint.after_request
def add_sunset_warning(response):
    # Thông báo API đã cũ
    response.headers['Deprecation'] = 'true'

    # Ngày chính thức đóng API (Sunset Date)
    response.headers['Sunset'] = 'Fri, 31 Dec 2026 23:59:59 GMT'

    # Dẫn hướng tới tài liệu nâng cấp
    response.headers['Link'] = '<https://api.docs.com/v2>; rel="help"'

    # Warning Header cho Console logs
    response.headers['Warning'] = '299 - "This version is deprecated. Please migrate."'

    return response

@v1_blueprint.route('/users')
def get_users_v1():
    return jsonify({"message": "Danh sách user (v1)"})

app = Flask(__name__)
app.register_blueprint(v1_blueprint)

if __name__ == '__main__':
    app.run()
