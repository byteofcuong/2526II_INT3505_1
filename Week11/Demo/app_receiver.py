import time
import hmac
import hashlib
import json
import queue
import threading
from flask import Flask, request, jsonify

# Initialize the Receiver Flask application
app = Flask(__name__)

# Shared signing secret key to verify signatures
SHARED_SECRET = "super_secret_signing_key"

# In-memory structures to simulate Redis cache for Idempotency and Background Task Queue
PROCESSED_EVENTS = set()
PROCESSED_LOCK = threading.Lock()
INGESTION_QUEUE = queue.Queue()

# =============================================================================
# DEFENSIVE WEBHOOK RECEIVER PATTERN
# =============================================================================
@app.route("/webhook/order-paid", methods=["POST"])
def webhook_order_paid():
    """
    POST /webhook/order-paid
    
    PATTERN DEMONSTRATED: 4-Step Defensive Webhook Receiver
    
    Protects downstream systems from signature forgery, replay attacks, duplicate processing,
    and denial of service (DoS) by executing four defensive isolation layers.
    """
    
    # -------------------------------------------------------------------------
    # STEP 1: Signature & Integrity Verification
    # -------------------------------------------------------------------------
    timestamp = request.headers.get("X-Webhook-Timestamp")
    received_signature = request.headers.get("X-Webhook-Signature")
    
    if not timestamp or not received_signature:
        return jsonify({
            "error": "Unauthorized",
            "message": "Authentication signatures are missing from the headers."
        }), 401
        
    # Replay Attack Prevention: Validate that request time does not exceed skew window (5 minutes)
    try:
        request_time = int(timestamp)
        current_time = int(time.time())
        if abs(current_time - request_time) > 300:
            return jsonify({
                "error": "Unauthorized",
                "message": "Signature timestamp has expired. Replay attack blocked."
            }), 401
    except ValueError:
        return jsonify({
            "error": "BadRequest",
            "message": "Malformed header X-Webhook-Timestamp."
        }), 400

    # Obtain raw bytes payload to verify precise transmission integrity
    raw_payload_bytes = request.get_data()
    raw_payload_str = raw_payload_bytes.decode("utf-8")
    
    # Reconstruct signature payload matching sender's format: timestamp + . + raw_json
    signature_payload = f"{timestamp}.{raw_payload_str}".encode("utf-8")
    
    # Compute the expected digest using SHA-256 HMAC
    expected_signature = hmac.new(
        SHARED_SECRET.encode("utf-8"),
        signature_payload,
        hashlib.sha256
    ).hexdigest()
    
    # timing-attack safe comparison to avoid side-channel information leakage
    if not hmac.compare_digest(expected_signature, received_signature):
        return jsonify({
            "error": "Unauthorized",
            "message": "Cryptographic signature validation failed. Access denied."
        }), 401

    # -------------------------------------------------------------------------
    # STEP 2: Idempotency Verification (De-duplication Check)
    # -------------------------------------------------------------------------
    try:
        payload = json.loads(raw_payload_str)
    except json.JSONDecodeError:
        return jsonify({
            "error": "BadRequest",
            "message": "Malformed JSON payload structure."
        }), 400
        
    event_id = payload.get("event_id")
    if not event_id:
        return jsonify({
            "error": "BadRequest",
            "message": "Missing unique tracking identity event_id."
        }), 400
        
    with PROCESSED_LOCK:
        if event_id in PROCESSED_EVENTS:
            # Event was already handled successfully. Acknowledge with 200 OK
            # to prevent client retries but avoid double execution.
            print(f"[Webhook Receiver] Idempotency Match: Event ID {event_id} already ingested. Skipping execution.")
            return jsonify({
                "status": "ignored",
                "message": f"Event {event_id} has already been successfully processed by the system."
            }), 200
            
        # Add to the set of successfully processed transactions
        PROCESSED_EVENTS.add(event_id)

    # -------------------------------------------------------------------------
    # STEP 3: Async Ingestion Queue Handoff
    # -------------------------------------------------------------------------
    # Handoff the event to an internal thread-safe queue. This decouples the network-level
    # HTTP server thread from heavy downstream business operations (e.g. databases, email).
    INGESTION_QUEUE.put(payload)
    print(f"[Webhook Receiver] [Success] Event {event_id} ingested. Payload Data: {payload['data']}")

    # -------------------------------------------------------------------------
    # STEP 4: Fast Acknowledge Response
    # -------------------------------------------------------------------------
    # Respond immediately with 202 Accepted status. The connection is released in milliseconds
    # keeping HTTP thread pools clear and highly responsive.
    return jsonify({
        "status": "accepted",
        "event_id": event_id,
        "message": "Event has been securely accepted and queued for downstream background operations."
    }), 202

if __name__ == "__main__":
    # Running receiver service on port 5001
    app.run(host="0.0.0.0", port=5001, debug=True)
