import pytest
import sys, os

# Thêm đường dẫn để test có thể import được app API
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api_server'))
from app import app as flask_app

@pytest.fixture
def app():
    """Tạo một bản mẫu Flask App (Fixture) để dùng chung cho các test."""
    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app

@pytest.fixture
def client(app):
    """Tạo Test Client để gửi giả lập các request GET/POST mà không cần bật server sãn."""
    return app.test_client()
