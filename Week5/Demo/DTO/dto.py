from flask import Flask, jsonify

app = Flask(__name__)

db_member_entity = {
    "id": 1,
    "full_name": "Nguyen Van A",
    "email": "a.nguyen@example.com",
    "password_hash": "$2b$12$eImiTXuWVxfM37uY4JANjQ==",
    "cccd_number": "001202003004"
}

def to_member_dto(entity):
    """
    Chỉ trích xuất những trường an toàn và cần thiết cho Client
    """
    return {
        "id": entity["id"],
        "name": entity["full_name"],
        "email": entity["email"]
    }

@app.route("/members/<int:member_id>", methods=["GET"])
def get_member(member_id):
    if member_id == db_member_entity["id"]:
        
        safe_data = to_member_dto(db_member_entity)
        
        return jsonify({
            "status": "success",
            "message": "Data mapped to DTO successfully",
            "data": safe_data
        }), 200
        
    return jsonify({"error": "Member not found"}), 404

if __name__ == "__main__":
    app.run(port=5001, debug=True)