def calculate_discount(price: float, discount_percent: float) -> float:
    """Hàm tính toán độc lập để chạy Unit Test"""
    if price < 0 or discount_percent < 0 or discount_percent > 100:
        raise ValueError("Lỗi: Giá học phần trăm giảm giá không hợp lệ!")
    return price * (1 - discount_percent / 100)
