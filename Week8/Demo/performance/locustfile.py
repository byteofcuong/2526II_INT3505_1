from locust import HttpUser, task, between

class AppTestUser(HttpUser):
    # Mỗi user (châu chấu) sẽ mô phỏng hành vi lướt tốn từ 1 đến 3 giây
    wait_time = between(1, 3)

    @task(4) # Trọng số 4: Hành động này diễn ra rất thường xuyên (90% là người ta chỉ xem)
    def view_products(self):
        self.client.get("/products")

    @task(1) # Trọng số 1: Ít người tạo mới hơn
    def create_fake_product(self):
        self.client.post("/products", json={
            "name": "Sản phẩm do Locust tự đẻ ra",
            "price": 99.99
        })
        
# Hướng dẫn chạy: Mở terminal chạy lệnh:
# locust -f locustfile.py
# Rồi vào web: http://localhost:8089 để gắn số lượng Users (Bầy châu chấu)
