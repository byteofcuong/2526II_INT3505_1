import requests

BASE_URL = "http://localhost:4010"

def test_get_books():
    r = requests.get(f"{BASE_URL}/books")
    print(f"GET /books -> {r.status_code}")

def test_add_book():
    r = requests.post(f"{BASE_URL}/books", json={
        "id": 1,
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "available": True
    })
    print(f"POST /books -> {r.status_code}")

def test_get_book():
    r = requests.get(f"{BASE_URL}/books/1")
    print(f"GET /books/1 -> {r.status_code}")

def test_borrow_book():
    r = requests.post(f"{BASE_URL}/loans", json={
        "id": 1,
        "memberId": 1,
        "bookId": 1,
        "dueDate": "2025-05-01",
        "status": "active"
    })
    print(f"POST /loans -> {r.status_code}")

def test_return_book():
    r = requests.post(f"{BASE_URL}/loans/1/return")
    print(f"POST /loans/1/return -> {r.status_code}")

if __name__ == "__main__":
    print("=== Testing Library API ===")
    test_get_books()
    test_add_book()
    test_get_book()
    test_borrow_book()
    test_return_book()
    print("=== Done ===")
