from flask import Flask, Blueprint

# Khởi tạo Blueprint cho từng phiên bản
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api_v2 = Blueprint('api_v2', __name__, url_prefix='/api/v2')

# Parallel Running các API có format khác nhau
@api_v1.route('/users')
def get_users_v1():
    return {"version": "v1", "data": ["Nguyen", "Tran"]}

@api_v2.route('/users')
def get_users_v2():
    return {"version": "v2", "data": [{"name": "Nguyen"}, {"name": "Tran"}]}

app = Flask(__name__)
app.register_blueprint(api_v1)
app.register_blueprint(api_v2)

if __name__ == '__main__':
    app.run()

    