from flask import Flask
from legacy_api import legacy_bp
from modern_api.v1 import v1_bp

app = Flask(__name__)

app.register_blueprint(legacy_bp, url_prefix='/old')
app.register_blueprint(v1_bp, url_prefix='/api/v1')

@app.route('/')
def index():
    return {
        "message": "Chào mừng bạn đến với Demo API Design Buổi 3!",
        "endpoints": {
            "legacy": "/old/get-all-users-in-database-api",
            "modern": "/api/v1/users"
        }
    }

if __name__ == '__main__':
    print("http://127.0.0.1:5000")
    app.run(debug=True, port=5000)