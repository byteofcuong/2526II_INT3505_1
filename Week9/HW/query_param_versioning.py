from flask import Flask, jsonify, request

app = Flask(__name__)

def get_version():
    # Lấy version từ query parameter, mặc định là '1'
    return request.args.get('version', '1')

@app.route('/api/users', methods=['GET'])
def get_users():
    version = get_version()
    if version == '2':
        return jsonify({"version": "v2", "users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]})
    return jsonify({"version": "v1", "users": ["Alice", "Bob"]})

@app.route('/api/products', methods=['GET'])
def get_products():
    version = get_version()
    if version == '2':
        return jsonify({"version": "v2", "products": [{"id": 101, "name": "Laptop", "price": 1000}, {"id": 102, "name": "Mouse", "price": 50}]})
    return jsonify({"version": "v1", "products": ["Laptop", "Mouse"]})

@app.route('/api/orders', methods=['GET'])
def get_orders():
    version = get_version()
    if version == '2':
        return jsonify({"version": "v2", "orders": [{"order_id": 1, "status": "shipped"}, {"order_id": 2, "status": "pending"}]})
    return jsonify({"version": "v1", "orders": [1, 2]})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    version = get_version()
    if version == '2':
        return jsonify({"version": "v2", "categories": [{"id": 1, "name": "Electronics"}, {"id": 2, "name": "Accessories"}]})
    return jsonify({"version": "v1", "categories": ["Electronics", "Accessories"]})

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    version = get_version()
    if version == '2':
        return jsonify({"version": "v2", "reviews": [{"id": 1, "rating": 5, "comment": "Good"}, {"id": 2, "rating": 2, "comment": "Bad"}]})
    return jsonify({"version": "v1", "reviews": ["Good", "Bad"]})

if __name__ == '__main__':
    print("Running Query Parameter Versioning on port 5002...")
    app.run(port=5002, debug=True)
