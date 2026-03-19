from flask import Flask, jsonify, make_response
from routes import api_bp
from config import SECRET_KEY

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

app.register_blueprint(api_bp)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({
        "status": "error",
        "message": "Resource not found"
    }), 404)

@app.errorhandler(405)
def method_not_allowed(error):
    return make_response(jsonify({
        "status": "error",
        "message": "Method not allowed"
    }), 405)

@app.errorhandler(500)
def internal_server_error(error):
    return make_response(jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500)

if __name__ == '__main__':
    app.run(debug=True, port=5000)