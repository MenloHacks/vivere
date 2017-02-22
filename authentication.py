from flask_login import  LoginManager
from vivere import app
from models import User

from flask import request

from utils import error_response, success_data_jsonify


login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/user/create', methods=['POST'])
def create_user():
    username = request.json['username']
    password = request.json['password']
    name = request.json['name']

    if username is None:
        return error_response(message='Missing parameter username', code=400)
    if password is None:
        return error_response(message='Missing parameter password', code=400)
    if name is None:
        return error_response(message='Missing parameter name', code=400)

    user = User()
    user.username = username
    user.set_password(password)
    user.name = name
    user.save()

    return success_data_jsonify({}, code=201)






@lm.user_loader
def load_user(username):
    user = User.objects(username=username).first()
    if not user:
        return None
    return user