import re
from datetime import datetime, timedelta

def validate_equipment_code(code):
    """
    Validates if the equipment code is valid.
    Format should be 'EQ-' followed by 4 digits. Example: EQ-0001
    """
    if not code:
        return False
    return bool(re.match(r'^EQ-\d{4}$', code))

def calculate_maintenance_date(equipment_type, install_date_str):
    """
    Calculates the next maintenance date based on equipment type.
    - 'Laptop': 6 months (180 days)
    - 'Desktop': 12 months (365 days)
    - 'Printer': 3 months (90 days)
    - Others: 1 month (30 days)
    """
    try:
        install_date = datetime.strptime(install_date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid date format. Expected YYYY-MM-DD")
    
    if equipment_type.lower() == 'laptop':
        days_to_add = 180
    elif equipment_type.lower() == 'desktop':
        days_to_add = 365
    elif equipment_type.lower() == 'printer':
        days_to_add = 90
    else:
        days_to_add = 30
        
    maintenance_date = install_date + timedelta(days=days_to_add)
    return maintenance_date.strftime("%Y-%m-%d")
