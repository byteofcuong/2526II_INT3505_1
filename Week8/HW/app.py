from flask import Flask, request, jsonify
from database import get_db_connection, init_db
from business_logic import validate_equipment_code, calculate_maintenance_date
import sqlite3

app = Flask(__name__)

# Initialize DB on startup
with app.app_context():
    init_db()

@app.route('/equipments', methods=['GET'])
def get_equipments():
    conn = get_db_connection()
    equipments = conn.execute('SELECT * FROM equipments').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in equipments]), 200

@app.route('/equipments', methods=['POST'])
def add_equipment():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    code = data.get('code')
    name = data.get('name')
    eq_type = data.get('type')
    install_date = data.get('install_date')

    if not all([code, name, eq_type, install_date]):
        return jsonify({'error': 'Missing required fields'}), 400

    if not validate_equipment_code(code):
        return jsonify({'error': 'Invalid equipment code format. Must be EQ-XXXX'}), 400

    try:
        maintenance_date = calculate_maintenance_date(eq_type, install_date)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO equipments (code, name, type, install_date, maintenance_date) VALUES (?, ?, ?, ?, ?)',
            (code, name, eq_type, install_date, maintenance_date)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': new_id, 'message': 'Equipment added successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Equipment code already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/equipments/<int:id>', methods=['GET'])
def get_equipment(id):
    conn = get_db_connection()
    equipment = conn.execute('SELECT * FROM equipments WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if equipment is None:
        return jsonify({'error': 'Equipment not found'}), 404
        
    return jsonify(dict(equipment)), 200

@app.route('/equipments/<int:id>', methods=['PUT'])
def update_equipment(id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400
        
    conn = get_db_connection()
    equipment = conn.execute('SELECT * FROM equipments WHERE id = ?', (id,)).fetchone()
    
    if equipment is None:
        conn.close()
        return jsonify({'error': 'Equipment not found'}), 404
        
    # Example: update maintenance_date manually or other info
    new_maintenance_date = data.get('maintenance_date', equipment['maintenance_date'])
    new_name = data.get('name', equipment['name'])
    
    conn.execute('UPDATE equipments SET name = ?, maintenance_date = ? WHERE id = ?',
                 (new_name, new_maintenance_date, id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Equipment updated successfully'}), 200

@app.route('/equipments/<int:id>', methods=['DELETE'])
def delete_equipment(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM equipments WHERE id = ?', (id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    if rows_affected == 0:
        return jsonify({'error': 'Equipment not found'}), 404
        
    return jsonify({'message': 'Equipment deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
