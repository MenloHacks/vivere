from flask_login import  LoginManager
from configuration import app
from models import User

from flask import request

from utils import error_response, success_data_jsonify, invalid_format
from flask import request
from constants import AUTHORIZATION_HEADER_FIELD


login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/user/create', methods=['POST'])
def create_user():
    json = request.get_json()
    if json is None:
        return invalid_format()
    if 'username' not in json:
        return error_response(title="No email provided",
                              message="To create an account, please provide your email",
                              code=400)
    if 'password' not in json:
        return error_response(title="No password provided",
                              message="To create an account, please provide a password",
                              code=400)
    if 'name' not in json:
        return error_response(title="No name provided",
                              message="To create an account, please provide your full name",
                              code=400)

    username = request.json['username']
    password = request.json['password']
    name = request.json['name']

    if len(username) == 0:
        return error_response(title="Email is empty",
                              message="To create an account, please provide your email",
                              code=400)
    if len(password) == 0:
        return error_response(title="Password is empty",
                              message="To create an account, please provide a password",
                              code=400)
    if len(name) == 0:
        return error_response(title="Name is empty",
                              message="To create an account, please provide your full name",
                              code=400)

    user = User.objects(username=username).first()
    if user is not None:
        return error_response(title="User already exists",
                              message="A user with this email address already exists. If you already have an account, plesae login instead.",
                              code=400)

    user = User()
    user.username = username
    user.set_password(password)
    user.name = name
    user.save()

    token = user.generate_auth_token()

    return success_data_jsonify({'token' : token}, code=201)

@app.route('/user/login', methods=['POST'])
def login():
    json = request.get_json()
    if json is None:
        return invalid_format()

    if 'username' not in json:
        return error_response(title='No email provided',
                              message='To login, please provide an email',
                              code=400)

    if 'password' not in json:
        return error_response(title='No password provided',
                              message='To login, please provide your password',
                              code=400)

    username = json['username']
    password = json['password']

    if len(username) == 0:
        return error_response(title="Email is empty",
                              message="To login, please provide your email",
                              code=400)
    if len(password) == 0:
        return error_response(title="Password is empty",
                              message="To login, please provide a password",
                              code=400)

    user = User.objects(username=username).first()

    if user is None:
        return error_response(title="No user exists with the specified email",
                              message="If you mis-entered your email please try again. If you do not have an account, please find an organizer.",
                              code=400)

    if User.validate_login(user.hashed_password, password):
        token = user.generate_auth_token()

        dictionary = user.dictionary_representation()
        dictionary['token'] = token
        
        return success_data_jsonify(dictionary)
    else:
        return error_response(title="Invalid password",
                              message="The password you entered is not valid. If you forgot your password, please find an organizer.",
                              code=401)


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

@app.route('/')

@login_manager.user_loader
def load_user(username):

    user = User.objects(username=username).first()
    if not user:
        return None
    else:
        return user