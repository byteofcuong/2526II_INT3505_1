import logging
import json
from datetime import datetime, timezone
from flask import Flask, request, jsonify, has_request_context

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        # Thêm method và path nếu log được gọi trong context của một request
        if has_request_context():
            log_record["method"] = request.method
            log_record["path"] = request.path
        else:
            log_record["method"] = "-"
            log_record["path"] = "-"
            
        if hasattr(record, 'exc_info') and record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

app = Flask(__name__)

# Cấu hình logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logHandler = logging.StreamHandler()
logHandler.setFormatter(JSONFormatter())
logger.addHandler(logHandler)

# Override default Flask & werkzeug logging để in ra chuẩn JSON của chúng ta
app.logger.handlers = [logHandler]
app.logger.setLevel(logging.INFO)

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.handlers = [logHandler]
werkzeug_logger.setLevel(logging.INFO)


# Database ảo (In-memory)
tasks = []
task_id_counter = 1

@app.before_request
def log_request_info():
    app.logger.info("Handling request")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks), 200

@app.route('/tasks', methods=['POST'])
def create_task():
    global task_id_counter
    data = request.get_json()
    
    if not data or 'title' not in data:
        app.logger.warning("Invalid task creation request: Missing title")
        return jsonify({"error": "Title is required"}), 400
        
    new_task = {
        "id": task_id_counter,
        "title": data['title'],
        "completed": data.get('completed', False)
    }
    tasks.append(new_task)
    app.logger.info(f"Task created with id: {task_id_counter}")
    task_id_counter += 1
    
    return jsonify(new_task), 201

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        app.logger.warning(f"Task not found: {task_id}")
        return jsonify({"error": "Task not found"}), 404
        
    return jsonify(task), 200

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        app.logger.warning(f"Task not found for update: {task_id}")
        return jsonify({"error": "Task not found"}), 404
        
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid payload"}), 400
        
    task['title'] = data.get('title', task['title'])
    task['completed'] = data.get('completed', task['completed'])
    app.logger.info(f"Task updated: {task_id}")
    
    return jsonify(task), 200

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        app.logger.warning(f"Task not found for deletion: {task_id}")
        return jsonify({"error": "Task not found"}), 404
        
    tasks = [t for t in tasks if t['id'] != task_id]
    app.logger.info(f"Task deleted: {task_id}")
    
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
