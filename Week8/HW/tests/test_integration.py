import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import init_db, get_db_connection

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            init_db() # Clear DB before each test
        yield client

def test_add_equipment_and_get(client):
    # 1. POST
    new_eq = {
        "code": "EQ-9999",
        "name": "Test Laptop",
        "type": "Laptop",
        "install_date": "2024-05-01"
    }
    response = client.post('/equipments', json=new_eq)
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    eq_id = data["id"]

    # 2. GET by ID
    response_get = client.get(f'/equipments/{eq_id}')
    assert response_get.status_code == 200
    eq_data = response_get.get_json()
    assert eq_data['code'] == "EQ-9999"
    assert eq_data['name'] == "Test Laptop"

def test_update_equipment(client):
    # Create first
    response = client.post('/equipments', json={
        "code": "EQ-8888",
        "name": "Old Name",
        "type": "Desktop",
        "install_date": "2024-01-01"
    })
    eq_id = response.get_json()["id"]

    # Update
    update_data = {
        "name": "New Name",
        "maintenance_date": "2025-01-01"
    }
    response_put = client.put(f'/equipments/{eq_id}', json=update_data)
    assert response_put.status_code == 200

    # Verify Update
    response_get = client.get(f'/equipments/{eq_id}')
    data = response_get.get_json()
    assert data['name'] == "New Name"
    assert data['maintenance_date'] == "2025-01-01"

def test_delete_equipment(client):
    # Create first
    response = client.post('/equipments', json={
        "code": "EQ-7777",
        "name": "To Delete",
        "type": "Printer",
        "install_date": "2024-01-01"
    })
    eq_id = response.get_json()["id"]

    # Delete
    response_del = client.delete(f'/equipments/{eq_id}')
    assert response_del.status_code == 200

    # Verify Delete
    response_get = client.get(f'/equipments/{eq_id}')
    assert response_get.status_code == 404
