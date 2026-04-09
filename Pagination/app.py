from flask import Flask, request, jsonify
import sqlite3
import time

app = Flask(__name__)
DB_FILE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/users/offset', methods=['GET'])
def get_users_offset():
    """
    Endpoint theo dạng Offset-Limit Pagination
    """
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    start_time = time.time()
    
    conn = get_db_connection()
    # Nếu là trang cuối thường ứng dụng sẽ cần đếm số trang
    # Bỏ qua count ở đây để đo thuần thời gian lấy data
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY id LIMIT ? OFFSET ?', (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    
    execution_time = time.time() - start_time
    
    data = [dict(ix) for ix in rows]
    return jsonify({
        'data': data,
        'limit': limit,
        'offset': offset,
        'count': len(data),
        'execution_time_seconds': execution_time
    })

@app.route('/api/users/cursor', methods=['GET'])
def get_users_cursor():
    """
    Endpoint theo dạng Cursor-based Pagination
    """
    limit = int(request.args.get('limit', 50))
    # cursor chính là ID của user cuối cùng trong lần tải trước
    cursor_id = int(request.args.get('cursor', 0))
    
    start_time = time.time()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # Tận dụng B-Tree Index của PK id
    cursor.execute('SELECT * FROM users WHERE id > ? ORDER BY id LIMIT ?', (cursor_id, limit))
    rows = cursor.fetchall()
    conn.close()
    
    execution_time = time.time() - start_time
    
    data = [dict(ix) for ix in rows]
    return jsonify({
        'data': data,
        'limit': limit,
        'next_cursor': data[-1]['id'] if data else None,
        'count': len(data),
        'execution_time_seconds': execution_time
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
