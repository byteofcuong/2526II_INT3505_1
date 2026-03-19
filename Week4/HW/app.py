from flask import Flask, send_from_directory, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import os

app = Flask(__name__)

SWAGGER_URL = '/api/docs'
API_URL = '/openapi.yaml' 

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "API Quản lý Sách"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/openapi.yaml')
def send_openapi():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'openapi.yaml')

books = [
    {"id": 1, "title": "Đắc Nhân Tâm", "author": "Dale Carnegie", "year": 1936},
    {"id": 2, "title": "Nhà Giả Kim", "author": "Paulo Coelho", "year": 1988}
]

@app.route('/books', methods=['GET'])
def get_books():
    return jsonify(books), 200


if __name__ == '__main__':
    print("*" * 50)
    print(f"http://localhost:5000{SWAGGER_URL}")
    print("*" * 50)
    app.run(debug=True, port=5000)
