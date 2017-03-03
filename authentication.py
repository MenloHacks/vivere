from flask_login import  LoginManager
from configuration import app
from models import User

from flask import request

from utils import error_response, success_data_jsonify
from flask import request
from constants import AUTHORIZATION_HEADER_FIELD


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

    user = User.objects(username=username).first()
    if user is not None:
        return error_response(message='A user already exists with this username', code=400)

    user = User()
    user.username = username
    user.set_password(password)
    user.name = name
    user.save()

    token = user.generate_auth_token()

    return success_data_jsonify({'token' : token}, code=201)

@app.route('/user/login', methods=['POST'])
def login():
    try:
        request.get_json()
    except:
        return error_response('Invalid format')

    if 'username' in request.json:
        username = request.json['username']
    else:
        error_response(message='Missing parameter username', code=400)

    if 'password' in request.json:
        password = request.json['password']
    else:
        return error_response(message='Missing parameter password', code=400)


    user = User.objects(username=username).first()

    if user is None:
        return error_response(message="No user exists with this username", code=404)

    if User.validate_login(user.hashed_password, password):
        token = user.generate_auth_token()
        return success_data_jsonify({'name' : user.name,
                                     'token' : token})
    else:
        return error_response(message='Invalid password', code=401)


from flask import render_template, url_for

@app.route('/admin/login',methods=['GET','POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('login.html')
    # return redirect(url_for('index'))


def current_user():
    if AUTHORIZATION_HEADER_FIELD in request.headers:
        token = request.headers[AUTHORIZATION_HEADER_FIELD]
        return User.verify_auth_token(token)
    return None

@login_manager.user_loader
def load_user(username):

    user = User.objects(username=username).first()
    if not user:
        return None
    else:
        return user