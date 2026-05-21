import time
import json
import queue
import threading
import hmac
import hashlib
import uuid
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from flask import Flask, jsonify, request, Response, url_for

# Initialize the Flask application
app = Flask(__name__)

# =============================================================================
# 1. DATABASE PATTERN: Mock In-Memory Datastore
# =============================================================================
# In a production system, this would be a persistent relational or document database.
# Using sequential integer IDs for keyset (cursor-based) pagination allows us to
# demonstrate efficient keyset querying logic in-memory.
ORDERS_DB: Dict[int, Dict[str, Any]] = {
    1: {"id": 1, "item": "Wireless Mouse", "price": 25, "status": "PENDING"},
    2: {"id": 2, "item": "Mechanical Keyboard", "price": 85, "status": "PAID"},
    3: {"id": 3, "item": "USB-C Hub", "price": 45, "status": "PENDING"},
    4: {"id": 4, "item": "Noise Cancelling Headphones", "price": 150, "status": "PAID"},
    5: {"id": 5, "item": "UltraWide Monitor", "price": 350, "status": "PENDING"},
    6: {"id": 6, "item": "Ergonomic Office Chair", "price": 299, "status": "PENDING"},
}

# Webhook Constants
SHARED_SECRET = "super_secret_signing_key"
WEBHOOK_URL = "http://127.0.0.1:5001/webhook/order-paid"

# =============================================================================
# 2. EVENT-DRIVEN PATTERN: Server-Sent Events (SSE) Pub/Sub Engine
# =============================================================================
# Real-time event broadcasting using a pub/sub topology.
# Active SSE client connections hold their own thread-safe queue. A global thread lock
# protects access to the list of listeners during addition, removal, and dispatching.
LISTENERS: List[queue.Queue] = []
LISTENERS_LOCK = threading.Lock()

def broadcast_event(event_type: str, data: Dict[str, Any]):
    """
    Broadcasts a structured JSON event payload to all connected SSE clients.
    Implements standard Server-Sent Events wire format.
    """
    event_payload = {
        "event": event_type,
        "timestamp": time.time(),
        "data": data
    }
    # Formulating standard SSE packet:
    # "event: <type>\ndata: <json>\n\n"
    sse_message = f"event: {event_type}\ndata: {json.dumps(event_payload)}\n\n"
    
    with LISTENERS_LOCK:
        # Loop through a shallow copy of listeners to allow modifications during traversal
        for q in LISTENERS[:]:
            try:
                # Non-blocking write to avoid slow readers hanging the broadcast thread
                q.put_nowait(sse_message)
            except queue.Full:
                # Drop slow-reading client queues that overflowed their buffer
                LISTENERS.remove(q)

def simulate_background_events():
    """
    Background worker thread mimicking downstream microservice event producers
    (e.g., inventory updates, shipping state changes).
    Broadcasting simulated order creations helps visualize the SSE stream in real-time.
    """
    import random
    event_counter = 1
    sample_items = ["Smart Watch", "Type-C Cable", "Laptop Stand", "Gaming Mousepad"]
    
    while True:
        time.sleep(5)  # Yield an event every 5 seconds
        if not LISTENERS:
            continue
            
        simulated_order = {
            "id": 100 + event_counter,
            "item": random.choice(sample_items),
            "price": random.randint(15, 600),
            "status": random.choice(["PENDING", "PAID"])
        }
        
        broadcast_event("order_created", simulated_order)
        event_counter += 1

# Launching background event simulator as a daemon thread
simulator_thread = threading.Thread(target=simulate_background_events, daemon=True)
simulator_thread.start()


@app.route("/api/v1/orders/stream", methods=["GET"])
def stream_orders():
    """
    GET /api/v1/orders/stream
    
    PATTERN DEMONSTRATED: Event-Driven Server-Sent Events (SSE)
    
    Establishes a persistent, unidirectional HTTP connection for real-time streaming.
    Utilizes generator functions and thread-safe queues to yield real-time events.
    """
    # Initialize a queue for this persistent connection with a strict capacity
    client_queue = queue.Queue(maxsize=50)
    
    with LISTENERS_LOCK:
        LISTENERS.append(client_queue)
        
    def sse_generator():
        # Immediate handshake packet tells the client connection is successfully established
        yield f"event: handshake\ndata: {json.dumps({'message': 'Connected to real-time orders stream'})}\n\n"
        
        try:
            while True:
                try:
                    # Non-blocking or timed blocking queue retrieval
                    # Periodic timeout lets us send heartbeats to prevent proxy/browser timeout
                    message = client_queue.get(timeout=15.0)
                    yield message
                except queue.Empty:
                    # Connection keep-alive heartbeat
                    yield "event: heartbeat\ndata: {\"status\": \"alive\"}\n\n"
        except GeneratorExit:
            # Triggered gracefully when client closes or drops the TCP socket
            pass
        finally:
            # Clean up: remove the listener from active listeners list
            with LISTENERS_LOCK:
                if client_queue in LISTENERS:
                    LISTENERS.remove(client_queue)

    return Response(
        sse_generator(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Prevents intermediate proxy buffering (e.g. Nginx)
        }
    )


# =============================================================================
# 3. SECURE WEBHOOK DISPATCHER PATTERN (Phase 2)
# =============================================================================
def send_webhook_async(order_id: int, price: int):
    """
    PATTERN DEMONSTRATED: Secure Webhook Dispatcher
    
    Spawns a background thread (asynchronous non-blocking architecture) to send
    a cryptographically signed JSON event to a third-party microservice endpoint.
    Uses HMAC-SHA256 for integrity and authenticity verification.
    """
    def webhook_worker():
        # 1. Construct Webhook Payload
        payload = {
            "event_id": f"evt_{uuid.uuid4().hex}",
            "type": "order.payment_succeeded",
            "data": {
                "order_id": order_id,
                "price": price
            }
        }
        raw_json_payload = json.dumps(payload, separators=(',', ':'))
        
        # 2. Cryptographic Security Signing
        timestamp = str(int(time.time()))
        # Combine timestamp and raw json payload to prevent replay attacks
        signature_payload = f"{timestamp}.{raw_json_payload}".encode("utf-8")
        
        # Calculate HMAC signature using shared secret
        signature = hmac.new(
            SHARED_SECRET.encode("utf-8"),
            signature_payload,
            hashlib.sha256
        ).hexdigest()
        
        # 3. Dispatch Outbound HTTP Request
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=raw_json_payload.encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-Webhook-Timestamp": timestamp,
                "X-Webhook-Signature": signature
            },
            method="POST"
        )
        
        try:
            # Send payload using native Python socket client
            with urllib.request.urlopen(req, timeout=5.0) as response:
                response.read() # Consume response to release connection
        except urllib.error.URLError as e:
            # Prevent background thread failures from crashing the core Flask runtime
            print(f"[Webhook Security Dispatcher] Dispatch failed to {WEBHOOK_URL} for Order {order_id}: {e}")

    # Spawn thread in daemon mode to prevent shutting down blockers
    threading.Thread(target=webhook_worker, daemon=True).start()


# =============================================================================
# 4. HATEOAS HYPERMEDIA ENGINE
# =============================================================================
def generate_order_links(order: Dict[str, Any]) -> Dict[str, Any]:
    """
    PATTERN DEMONSTRATED: HATEOAS (Hypermedia As The Engine Of Application State)
    
    Generates dynamic resource actions and transition URLs based on the order's state.
    """
    order_id = order["id"]
    links = {
        "self": {
            "href": url_for("get_order", order_id=order_id, _external=True),
            "method": "GET",
            "rel": "self",
            "description": "Retrieve detailed metadata for this order."
        }
    }
    
    # State-based transition actions:
    # A transition link for payment is ONLY provided if the order status is PENDING.
    if order["status"] == "PENDING":
        links["pay"] = {
            "href": f"{request.url_root}api/v1/orders/{order_id}/pay",
            "method": "POST",
            "rel": "pay",
            "description": "Execute payment for this order (Transitions status PENDING -> PAID)."
        }
    elif order["status"] == "PAID":
        links["receipt"] = {
            "href": f"{request.url_root}api/v1/orders/{order_id}/receipt",
            "method": "GET",
            "rel": "receipt",
            "description": "Retrieve financial receipt for this payment."
        }
        
    return links


# =============================================================================
# 5. API PATTERNS: Filtering, Keyset Pagination, and Collection HATEOAS
# =============================================================================
@app.route("/api/v1/orders", methods=["GET"])
def get_orders():
    """
    GET /api/v1/orders
    
    PATTERNS DEMONSTRATED:
    - Collection Filtering (status via query parameter)
    - Keyset (Cursor) Pagination (starting_after & limit parameters instead of offset)
    - Collection HATEOAS (self and dynamic next link)
    """
    # -------------------------------------------------------------------------
    # Filtering Pattern
    # -------------------------------------------------------------------------
    status_filter = request.args.get("status")
    
    # Extract orders sorted by ID to guarantee a stable sorted keyset
    all_sorted_orders = sorted(ORDERS_DB.values(), key=lambda x: x["id"])
    
    if status_filter:
        status_filter = status_filter.upper()
        all_sorted_orders = [o for o in all_sorted_orders if o["status"] == status_filter]

    # -------------------------------------------------------------------------
    # Keyset Pagination Pattern
    # -------------------------------------------------------------------------
    # Cursor pagination queries records relative to the last seen record ID (the cursor).
    # Parameter `starting_after` represents the last seen cursor.
    # Why Keyset over Offset? Offset pagination suffers from performance degradation
    # at scale O(N) and item skipping/duplication under high-concurrency mutation.
    # Keyset utilizes indexing (where id > cursor) resulting in O(log N) operations.
    
    limit_val = request.args.get("limit", default=2, type=int)
    limit_val = max(1, min(limit_val, 100))  # Safeguard boundary limit values
    
    starting_after = request.args.get("starting_after", type=int)
    
    # Apply keyset constraint
    paginated_results = all_sorted_orders
    if starting_after is not None:
        paginated_results = [o for o in all_sorted_orders if o["id"] > starting_after]
        
    # Check if a next page exists
    has_more = len(paginated_results) > limit_val
    
    # Extract only the records required for this page
    page_items = paginated_results[:limit_val]

    # Map records to include their individual stateful HATEOAS hyperlinks
    response_items = []
    for order in page_items:
        formatted_order = order.copy()
        formatted_order["_links"] = generate_order_links(order)
        response_items.append(formatted_order)

    # -------------------------------------------------------------------------
    # HATEOAS Collection Meta links
    # -------------------------------------------------------------------------
    meta = {
        "limit": limit_val,
        "size": len(response_items),
        "has_more": has_more
    }
    
    root_links = {
        "self": {
            "href": request.url,
            "method": "GET"
        }
    }
    
    # If more pages exist, construct the 'next' HATEOAS navigation link
    if has_more and len(response_items) > 0:
        # Keyset pagination uses the ID of the last item in the current batch as the cursor
        next_cursor = response_items[-1]["id"]
        
        # Build new query parameters while preserving the status filter if active
        next_params = {
            "limit": limit_val,
            "starting_after": next_cursor
        }
        if status_filter:
            next_params["status"] = status_filter
            
        from urllib.parse import urlencode
        next_query = urlencode(next_params)
        next_url = f"{request.base_url}?{next_query}"
        
        root_links["next"] = {
            "href": next_url,
            "method": "GET",
            "description": "Fetch the next sequential page of orders."
        }

    return jsonify({
        "data": response_items,
        "meta": meta,
        "_links": root_links
    })


# =============================================================================
# 6. CRUD PATTERN: Single Resource Read
# =============================================================================
@app.route("/api/v1/orders/<int:order_id>", methods=["GET"])
def get_order(order_id: int):
    """
    GET /api/v1/orders/<int:order_id>
    
    PATTERN DEMONSTRATED: CRUD Read
    
    Retrieves standard singular resource entity representation and appends hypermedia controls.
    """
    order = ORDERS_DB.get(order_id)
    if not order:
        return jsonify({
            "error": "OrderNotFound",
            "message": f"An order with ID {order_id} could not be found."
        }), 404
        
    response_data = order.copy()
    response_data["_links"] = generate_order_links(order)
    
    return jsonify(response_data)


# =============================================================================
# 7. BUSINESS LOGIC & STATE TRANSITION PATTERN (Phase 2 Update)
# =============================================================================
@app.route("/api/v1/orders/<int:order_id>/pay", methods=["POST"])
def pay_order(order_id: int):
    """
    POST /api/v1/orders/<int:order_id>/pay
    
    PATTERN DEMONSTRATED: CRUD Update & State Transition, Real-time SSE Broadcast, Secure Webhook Execution
    
    Executes business rules to transition an order's status from PENDING to PAID.
    Validates resource existences and blocks invalid duplicate payments.
    On success:
      - Persists state modifications to the store.
      - Dispatches a real-time event through Server-Sent Events to listeners.
      - Asynchronously dispatches a cryptographically signed webhook to third-party receiver.
    """
    order = ORDERS_DB.get(order_id)
    
    # 1. Validate resource existence
    if not order:
        return jsonify({
            "error": "OrderNotFound",
            "message": f"An order with ID {order_id} could not be found."
        }), 404
        
    # 2. Block invalid state transitions
    if order["status"] == "PAID":
        return jsonify({
            "error": "OrderAlreadyPaid",
            "message": f"Order with ID {order_id} has already been paid and cannot be processed again."
        }), 400
        
    # 3. Apply state transition
    order["status"] = "PAID"
    
    # 4. SSE Integration: Real-time broadcast
    sse_broadcast_payload = {
        "event": "order.updated",
        "order_id": order_id,
        "status": "PAID"
    }
    broadcast_event("order_updated", sse_broadcast_payload)
    
    # 5. Secure Webhook Integration: Async thread dispatch
    send_webhook_async(order_id, order["price"])
    
    # Construct standard enriched response payload
    response_data = order.copy()
    response_data["_links"] = generate_order_links(order)
    
    return jsonify({
        "message": f"Payment successfully processed for order {order_id}.",
        "data": response_data
    }), 200


# Launch the server
if __name__ == "__main__":
    # Running on default port 5000 as configured.
    # Set threaded=True to support multiple concurrent connections, which is required
    # for the Server-Sent Events stream endpoint to not block other standard REST requests.
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
