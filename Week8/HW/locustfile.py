import random
from locust import HttpUser, task, between

class EquipmentUser(HttpUser):
    # Wait time between tasks (simulates real user thinking time)
    wait_time = between(1, 3)

    @task(3)
    def get_equipments(self):
        """Simulate a user fetching the list of equipments. Weight=3 (more frequent)."""
        self.client.get("/equipments", name="Get All Equipments")

    @task(1)
    def add_and_delete_equipment(self):
        """Simulate adding a new equipment and then deleting it. Weight=1."""
        random_id = random.randint(10000, 99999)
        code = f"EQ-{random_id}"
        
        # 1. POST
        response = self.client.post("/equipments", json={
            "code": code,
            "name": "Load Test Device",
            "type": "Laptop",
            "install_date": "2024-01-01"
        }, name="Create Equipment")

        # 2. DELETE
        if response.status_code == 201:
            data = response.json()
            eq_id = data.get("id")
            if eq_id:
                self.client.delete(f"/equipments/{eq_id}", name="Delete Equipment")
