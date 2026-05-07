from flask import Flask, jsonify

app = Flask(__name__)

# --- BÀI TOÁN: QUẢN LÝ CỬA HÀNG (STORE MANAGEMENT) ---
# 5 Endpoints: Users, Products, Orders, Categories, Reviews

# ==========================================
# VERSION 1 (Legacy Data Format - Dữ liệu dạng đơn giản)
# ==========================================

@app.route('/api/v1/users', methods=['GET'])
def get_users_v1():
    return jsonify({"version": "v1", "users": ["Alice", "Bob"]})

@app.route('/api/v1/products', methods=['GET'])
def get_products_v1():
    return jsonify({"version": "v1", "products": ["Laptop", "Mouse"]})

@app.route('/api/v1/orders', methods=['GET'])
def get_orders_v1():
    return jsonify({"version": "v1", "orders": [1, 2]})

@app.route('/api/v1/categories', methods=['GET'])
def get_categories_v1():
    return jsonify({"version": "v1", "categories": ["Electronics", "Accessories"]})

@app.route('/api/v1/reviews', methods=['GET'])
def get_reviews_v1():
    return jsonify({"version": "v1", "reviews": ["Good", "Bad"]})

# ==========================================
# VERSION 2 (New Data Format - Dữ liệu chi tiết hơn)
# ==========================================

@app.route('/api/v2/users', methods=['GET'])
def get_users_v2():
    return jsonify({"version": "v2", "users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]})

@app.route('/api/v2/products', methods=['GET'])
def get_products_v2():
    return jsonify({"version": "v2", "products": [{"id": 101, "name": "Laptop", "price": 1000}, {"id": 102, "name": "Mouse", "price": 50}]})

@app.route('/api/v2/orders', methods=['GET'])
def get_orders_v2():
    return jsonify({"version": "v2", "orders": [{"order_id": 1, "status": "shipped"}, {"order_id": 2, "status": "pending"}]})

@app.route('/api/v2/categories', methods=['GET'])
def get_categories_v2():
    return jsonify({"version": "v2", "categories": [{"id": 1, "name": "Electronics"}, {"id": 2, "name": "Accessories"}]})

@app.route('/api/v2/reviews', methods=['GET'])
def get_reviews_v2():
    return jsonify({"version": "v2", "reviews": [{"id": 1, "rating": 5, "comment": "Good"}, {"id": 2, "rating": 2, "comment": "Bad"}]})

if __name__ == '__main__':
    print("Running URI Path Versioning on port 5001...")
    app.run(port=5001, debug=True)
