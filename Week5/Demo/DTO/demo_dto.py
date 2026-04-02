from dto import db_member_entity, to_member_dto
import json


print("\nDữ liệu gốc trong Database (Entity/Model):")
print(json.dumps(db_member_entity, indent=2))

print("\nDữ liệu trả về cho Client (DTO):")
safe_data = to_member_dto(db_member_entity)
print(json.dumps(safe_data, indent=2))
