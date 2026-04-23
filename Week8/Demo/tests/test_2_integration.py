def test_get_products(client):
    """Integration Test: Gọi API lấy toàn bộ sản phẩm và chắc chắn thành công."""
    response = client.get('/products')
    assert response.status_code == 200
    assert len(response.json) >= 2

def test_create_product_success(client):
    """Integration Test: Test tạo sản phẩm hợp lệ, kiểm tra xem DB giả lập có tăng được 1 ID không."""
    new_product = {"name": "Mechanical Keyboard", "price": 100}
    response = client.post('/products', json=new_product)
    
    assert response.status_code == 201
    assert response.json['name'] == "Mechanical Keyboard"
    assert response.json['id'] == 3 # ID tự tăng (giả định bắt đầu ở 3)

def test_create_product_missing_price(client):
    """Integration Test: Test trường hợp người dùng cố ý gửi thiếu trường 'price'."""
    new_product = {"name": "Keyboard Không Giá"}
    response = client.post('/products', json=new_product)
    
    assert response.status_code == 400
    assert "Thiếu dữ liệu bắt buộc" in response.json['error']
