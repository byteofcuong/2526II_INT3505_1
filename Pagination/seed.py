import sqlite3
import random
import time
from datetime import datetime, timedelta

DB_FILE = 'database.db'
NUM_RECORDS = 1_000_000
BATCH_SIZE = 50_000

def create_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            created_at TIMESTAMP
        )
    ''')
    
    # Check if table already has data
    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]
    if count >= NUM_RECORDS:
        print(f"Bảng đã có {count} bản ghi")
        conn.close()
        return

    print("Đang tạo dữ liệu, vui lòng đợi...")
    start_time = time.time()
    
    # Generate base words for name to be somewhat random
    first_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
    last_names = ["An", "Bình", "Cường", "Dũng", "Em", "Phong", "Giang", "Hải", "Linh", "Minh", "Nam", "Oanh", "Phương", "Quân"]
    
    base_date = datetime.now() - timedelta(days=365)
    
    for i in range(0, NUM_RECORDS, BATCH_SIZE):
        batch_data = []
        for j in range(BATCH_SIZE):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            # Generate random time spanning the last year
            created_at = base_date + timedelta(minutes=random.randint(0, 500000))
            batch_data.append((name, created_at.strftime('%Y-%m-%d %H:%M:%S')))
            
        cursor.executemany('''
            INSERT INTO users (name, created_at)
            VALUES (?, ?)
        ''', batch_data)
        conn.commit()
        print(f"Đã insert {i + BATCH_SIZE} / {NUM_RECORDS} dòng...")
    
    conn.close()
    print(f"Hoàn thành trong {time.time() - start_time:.2f} giây.")

if __name__ == "__main__":
    create_database()
