from flask import Flask, jsonify, request
from .utils import calculate_discount

app = Flask(__name__)

# Giả lập Database trong RAM (Array)
products = [
    {"id": 1, "name": "Core Desktop", "price": 1000},
    {"id": 2, "name": "Gaming Mouse", "price": 50}
]
next_id = 3

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(products), 200

@app.route('/products/<int:prod_id>', methods=['GET'])
def get_product(prod_id):
    prod = next((p for p in products if p['id'] == prod_id), None)
    if not prod:
        return jsonify({"error": "Không tìm thấy sản phẩm"}), 404
    return jsonify(prod), 200

@app.route('/products', methods=['POST'])
def create_product():
    global next_id
    data = request.json
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({"error": "Thiếu dữ liệu bắt buộc (name, price)"}), 400
    
    new_product = {
        "id": next_id,
        "name": data['name'],
        "price": data['price']
    }
    products.append(new_product)
    next_id += 1
    return jsonify(new_product), 201

@app.route('/products/<int:prod_id>', methods=['PUT'])
def update_product(prod_id):
    data = request.json
    prod = next((p for p in products if p['id'] == prod_id), None)
    if not prod:
        return jsonify({"error": "Không tìm thấy sản phẩm"}), 404
    
    prod['name'] = data.get('name', prod['name'])
    prod['price'] = data.get('price', prod['price'])
    return jsonify(prod), 200

@app.route('/products/<int:prod_id>', methods=['DELETE'])
def delete_product(prod_id):
    global products
    prod = next((p for p in products if p['id'] == prod_id), None)
    if not prod:
        return jsonify({"error": "Không tìm thấy sản phẩm"}), 404
    
    products = [p for p in products if p['id'] != prod_id]
    return jsonify({"message": "Đã xoá sản phẩm"}), 200

@app.route('/apply-discount', methods=['POST'])
def apply_discount():
    data = request.json
    try:
        new_price = calculate_discount(data['price'], data['discount'])
        return jsonify({"new_price": new_price}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
