import pytest
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api_server'))
from utils import calculate_discount

def test_calculate_discount_normal():
    """Unit Test: Kiểm tra hàm tính giảm giá ở điều kiện bình thường."""
    assert calculate_discount(100, 20) == 80.0
    assert calculate_discount(50, 0) == 50.0

def test_calculate_discount_invalid():
    """Unit Test: Kiểm tra hàm có văng lỗi đúng chuẩn nếu phần trăm âm không."""
    with pytest.raises(ValueError, match="Lỗi: Giá học phần trăm giảm giá không hợp lệ!"):
        calculate_discount(100, -10)
    
    with pytest.raises(ValueError):
        calculate_discount(100, 110)
