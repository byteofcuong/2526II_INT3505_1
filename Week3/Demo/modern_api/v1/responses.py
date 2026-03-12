from flask import jsonify

def wrap_response(data=None, message="", status=200):
    success = True if status < 400 else False
    
    return jsonify({
        "success": success,
        "data": data,
        "message": message
    }), status