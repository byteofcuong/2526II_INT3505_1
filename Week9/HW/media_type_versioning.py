from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

# Helper function để trả về response với đúng Content-Type
def create_versioned_response(data, version):
    response = make_response(jsonify(data))
    if version == '2':
        response.mimetype = 'application/vnd.company.v2+json'
    else:
        # V1 có thể dùng chuẩn chung hoặc chuẩn riêng của V1
        response.mimetype = 'application/vnd.company.v1+json'
    
    response.headers['Vary'] = 'Accept'
    return response

def get_version():
    accept_header = request.headers.get('Accept', '')
    if 'application/vnd.company.v2+json' in accept_header:
        return '2'
    return '1'

@app.route('/api/users', methods=['GET'])
def get_users():
    version = get_version()
    if version == '2':
        data = {"version": "v2", "users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
    else:
        data = {"version": "v1", "users": ["Alice", "Bob"]}
    return create_versioned_response(data, version)

@app.route('/api/products', methods=['GET'])
def get_products():
    version = get_version()
    if version == '2':
        data = {"version": "v2", "products": [{"id": 101, "name": "Laptop", "price": 1000}, {"id": 102, "name": "Mouse", "price": 50}]}
    else:
        data = {"version": "v1", "products": ["Laptop", "Mouse"]}
    return create_versioned_response(data, version)

@app.route('/api/orders', methods=['GET'])
def get_orders():
    version = get_version()
    if version == '2':
        data = {"version": "v2", "orders": [{"order_id": 1, "status": "shipped"}, {"order_id": 2, "status": "pending"}]}
    else:
        data = {"version": "v1", "orders": [1, 2]}
    return create_versioned_response(data, version)

@app.route('/api/categories', methods=['GET'])
def get_categories():
    version = get_version()
    if version == '2':
        data = {"version": "v2", "categories": [{"id": 1, "name": "Electronics"}, {"id": 2, "name": "Accessories"}]}
    else:
        data = {"version": "v1", "categories": ["Electronics", "Accessories"]}
    return create_versioned_response(data, version)

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    version = get_version()
    if version == '2':
        data = {"version": "v2", "reviews": [{"id": 1, "rating": 5, "comment": "Good"}, {"id": 2, "rating": 2, "comment": "Bad"}]}
    else:
        data = {"version": "v1", "reviews": ["Good", "Bad"]}
    return create_versioned_response(data, version)

if __name__ == '__main__':
    print("Running Media Type Versioning on port 5004...")
    app.run(port=5004, debug=True)
