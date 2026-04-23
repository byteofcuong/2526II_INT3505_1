import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from business_logic import validate_equipment_code, calculate_maintenance_date

def test_validate_equipment_code_valid():
    assert validate_equipment_code('EQ-1234') == True
    assert validate_equipment_code('EQ-0000') == True

def test_validate_equipment_code_invalid():
    assert validate_equipment_code('EQ-123') == False
    assert validate_equipment_code('eq-1234') == False
    assert validate_equipment_code('EQ1234') == False
    assert validate_equipment_code(None) == False

def test_calculate_maintenance_date_laptop():
    # Laptop is +180 days
    install_date = "2024-01-01"
    expected_date = "2024-06-29" # 2024 is a leap year (Feb 29 days)
    # Jan 31 + Feb 29 + Mar 31 + Apr 30 + May 31 + Jun 28 = 180 days. Wait, date calculation might vary slightly, let's use actual python behavior:
    # 180 days from 2024-01-01
    from datetime import datetime, timedelta
    expected = (datetime(2024, 1, 1) + timedelta(days=180)).strftime("%Y-%m-%d")
    assert calculate_maintenance_date('Laptop', install_date) == expected

def test_calculate_maintenance_date_invalid_format():
    with pytest.raises(ValueError, match="Invalid date format"):
        calculate_maintenance_date('Laptop', '01/01/2024')
