import requests
import time

BASE_URL = "http://127.0.0.0:5000/api/users"

def fetch_offset(offset, limit=50):
    url = f"http://127.0.0.1:5000/api/users/offset?offset={offset}&limit={limit}"
    start = time.time()
    res = requests.get(url).json()
    total_time = time.time() - start
    db_time = res.get('execution_time_seconds', 0)
    return total_time, db_time

def fetch_cursor(cursor, limit=50):
    url = f"http://127.0.0.1:5000/api/users/cursor?cursor={cursor}&limit={limit}"
    start = time.time()
    res = requests.get(url).json()
    total_time = time.time() - start
    db_time = res.get('execution_time_seconds', 0)
    return total_time, db_time

def run_benchmark():
    scenarios = [
        {"name": "Trang đầu (Offset 0)", "offset": 0, "cursor": 0},
        {"name": "Trang giữa (Offset 500,000)", "offset": 500_000, "cursor": 500_000},
        {"name": "Trang gần cuối (Offset 900,000)", "offset": 900_000, "cursor": 900_000},
        {"name": "Trang cuối cùng (Offset 999,950)", "offset": 999_950, "cursor": 999_950},
    ]

    with open("result.txt", "w", encoding="utf-8") as f:
        def pr(text):
            print(text)
            f.write(text + "\n")

        pr("="*60)
        pr(f"{'VẬN HÀNH':<30} | {'OFFSET-LIMIT (DB Time)':<25} | {'CURSOR-BASED (DB Time)':<25}")
        pr("="*60)

        for s in scenarios:
            # Chạy 3 lần lấy trung bình cho chắc chắn
            
            # Offset
            offset_db_times = []
            for _ in range(3):
                _, db_time = fetch_offset(s["offset"])
                offset_db_times.append(db_time)
            avg_offset_db = sum(offset_db_times) / 3 * 1000 # tính theo milliseconds
            
            # Cursor
            cursor_db_times = []
            for _ in range(3):
                _, db_time = fetch_cursor(s["cursor"])
                cursor_db_times.append(db_time)
            avg_cursor_db = sum(cursor_db_times) / 3 * 1000 # tính theo milliseconds
            
            pr(f"{s['name']:<30} | {avg_offset_db:>15.2f} ms | {avg_cursor_db:>15.2f} ms")
            
        pr("="*60)
        pr("Kết luận:")
        pr(" - Cursor-based: Thời gian lấy dữ liệu luôn ở mức tối ưu (O(1)) do sử dụng Index B-Tree đi thẳng đến ID.")
        pr(" - Offset/Limit: Thời gian thực thi tăng tuyến tính theo số lượng bản ghi bị bỏ qua (O(N)), càng về cuối càng chậm.")

if __name__ == "__main__":
    try:
        requests.get("http://127.0.0.1:5000/api/users/offset?offset=0&limit=1")
        run_benchmark()
    except requests.exceptions.ConnectionError:
        print("Lỗi: Không kết nối được với server. Hãy chắc chắn rằng bạn đã chạy 'python app.py' ở một terminal khác.")
