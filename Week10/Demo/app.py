import logging
import json
import time
import random
from datetime import datetime, timezone
from flask import Flask, request, jsonify, has_request_context

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

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

# 1. Security Headers (Flask-Talisman)
Talisman(app, force_https=False) # force_https=False để cho phép test local HTTP

# 2. Rate Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# 3. Prometheus Metrics (RED: Rate, Errors, Duration)
REQUEST_COUNT = Counter(
    'request_total', 
    'Total number of requests', 
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'request_latency_seconds', 
    'Request latency', 
    ['method', 'endpoint']
)

# 4. Circuit Breaker (Manual wrapper)
class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=10):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"
        
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit is OPEN. Request rejected.")
                
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            raise e

breaker = CircuitBreaker()

# Cấu hình logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logHandler = logging.StreamHandler()
logHandler.setFormatter(JSONFormatter())
logger.addHandler(logHandler)

app.logger.handlers = [logHandler]
app.logger.setLevel(logging.INFO)

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.handlers = [logHandler]
werkzeug_logger.setLevel(logging.INFO)

# Database ảo (In-memory)
tasks = []
task_id_counter = 1

@app.before_request
def before_request():
    request.start_time = time.time()
    if request.path != '/metrics':
        app.logger.info("Handling request")

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time') and request.path != '/metrics':
        resp_time = time.time() - request.start_time
        REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
        REQUEST_LATENCY.labels(request.method, request.path).observe(resp_time)
    return response

@app.route('/metrics')
@limiter.exempt
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks), 200

@app.route('/tasks', methods=['POST'])
@limiter.limit("5 per minute")
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
@limiter.limit("5 per minute")
def delete_task(task_id):
    global tasks
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        app.logger.warning(f"Task not found for deletion: {task_id}")
        return jsonify({"error": "Task not found"}), 404
        
    tasks = [t for t in tasks if t['id'] != task_id]
    app.logger.info(f"Task deleted: {task_id}")
    
    return '', 204

# Simulated external service call
def external_service_call():
    # 50% chance to fail
    if random.random() < 0.5:
        raise Exception("Simulated external service failure")
    return "External service responded successfully"

@app.route('/external', methods=['GET'])
def call_external():
    try:
        result = breaker.call(external_service_call)
        return jsonify({
            "message": result,
            "circuit_state": breaker.state
        }), 200
    except Exception as e:
        app.logger.error(f"External service failed: {e}")
        return jsonify({
            "error": str(e),
            "circuit_state": breaker.state
        }), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
