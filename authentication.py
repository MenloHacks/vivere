import flask_login as login
from configuration import app
from models import User
import os

from flask import request, send_file

from utils import error_response, success_data_jsonify, invalid_format
from flask import request
from constants import AUTHORIZATION_HEADER_FIELD, ADMIN_HEADER_FIELD
from passbook.models import Pass, Barcode, EventTicket, Location, BarcodeFormat
from configuration import MENLOHACKS_PASSBOOK_KEY_FILENAME
import datetime
import hashlib



@app.route('/user/ticket/<username>')
def get_ticket_admin(username):
    if ADMIN_HEADER_FIELD not in request.headers:
        return error_response(title="No password",
                              message='To check in a user, please provide the admin password',
                              code=401)
    password = request.headers[ADMIN_HEADER_FIELD]

    if password != os.environ['ADMIN_PASSWORD']:
        return error_response(title="Invalid password",
                              message='To check in a user, please provide the admin password',
                              code=401)

    user = User.objects(username=username).first()
    if user is None:
        return error_response(title="No user",
                              message='A user does not exist with this username',
                              code=404)

    return generate_pass(user)

@app.route('/get_users')
def get_users():
    if ADMIN_HEADER_FIELD not in request.headers:
        return error_response(title="No password",
                              message='To check in a user, please provide the admin password',
                              code=401)
    password = request.headers[ADMIN_HEADER_FIELD]

    if password != os.environ['ADMIN_PASSWORD']:
        return error_response(title="Invalid password",
                              message='To check in a user, please provide the admin password',
                              code=401)

    users = User.objects(checked_in=True)
    return success_data_jsonify([user.name for user in users])



@app.route('/user/ticket')
def get_ticket():
    user = current_user()
    if user is None:
        return error_response(title="No user is currently logged in",
                              message="In get your ticket, you must be logged in",
                              code=401)
    return generate_pass(user)


def generate_pass(user):
    cardInfo = EventTicket()
    cardInfo.addPrimaryField('name', user.name, 'Name')
    cardInfo.addHeaderField('header', 'March 10-11, 2018', 'Menlo School')

    if user.school:
        cardInfo.addSecondaryField('loc', user.school, 'School')
    cardInfo.addSecondaryField('email', user.username, 'Email')

    organizationName = 'MenloHacks'
    passTypeIdentifier = 'pass.com.menlohacks.menlohacksiii'
    teamIdentifier = 'YWVU2284UC'

    passfile = Pass(cardInfo,
                    passTypeIdentifier=passTypeIdentifier,
                    organizationName=organizationName,
                    teamIdentifier=teamIdentifier)

    passfile.labelColor = 'rgb(255,255,255)'
    passfile.foregroundColor = 'rgb(255,255,255)'

    passfile.relevantDate = '2018-03-10T10:00-01:00'

    latitude = 37.453240
    longitude = -122.191278

    location = Location(latitude, longitude)
    location.distance = 600

    passfile.serialNumber = hashlib.sha256(user.username).hexdigest()
    passfile.locations = [location]
    passfile.barcode = Barcode(message=user.username, format=BarcodeFormat.QR)

    dir = os.path.dirname(__file__)

    passfile.addFile('icon.png', open(os.path.join(dir, 'passbook/icon.png'), 'r'))
    passfile.addFile('icon@2x.png', open(os.path.join(dir, 'passbook/icon@2x.png'), 'r'))
    passfile.addFile('icon@3x.png', open(os.path.join(dir, 'passbook/icon@3x.png'), 'r'))

    passfile.addFile('logo.png', open(os.path.join(dir, 'passbook/logo.png'), 'r'))
    passfile.addFile('logo@2x.png', open(os.path.join(dir, 'passbook/logo@2x.png'), 'r'))
    passfile.addFile('logo@3x.png', open(os.path.join(dir, 'passbook/logo@3x.png'), 'r'))

    passfile.addFile('background.png', open(os.path.join(dir, 'passbook/background.png'), 'r'))
    passfile.addFile('background@2x.png', open(os.path.join(dir, 'passbook/background@2x.png'), 'r'))
    passfile.addFile('background@3x.png', open(os.path.join(dir, 'passbook/background@3x.png'), 'r'))

    key_path = 'secure/' + MENLOHACKS_PASSBOOK_KEY_FILENAME

    key_filename = os.path.join(dir, key_path)
    cert_filename = os.path.join(dir, 'passbook/certificate.pem')
    wwdr_filename = os.path.join(dir, 'passbook/WWDR.pem')

    password = os.environ['PASSBOOK_PASSWORD']


    file = passfile.create(cert_filename, key_filename, wwdr_filename, password)
    file.seek(0)



    return send_file(file, as_attachment=True,
                     attachment_filename='pass.pkpass',
                     mimetype='application/vnd.apple.pkpass')




@app.route('/user/checkin', methods=['POST'])
def check_in_user():
    json = request.get_json()
    if json is None:
        return invalid_format()

    if ADMIN_HEADER_FIELD not in request.headers:
        return error_response(title="No password",
                              message='To check in a user, please provide the admin password',
                              code=401)

    if 'username' not in json:
        return error_response(title="No username provided",
                              message='To check in a user, please provide the username of the user to check in',
                              code=400)

    username = json['username']
    password = request.headers[ADMIN_HEADER_FIELD]

    if os.environ['ADMIN_PASSWORD'] != password:
        return error_response(title="Invalid password",
                              message='To check in a user, please provide the correct shared password',
                              code=401)

    user = User.objects(username=username).first()
    if user is None:
        return error_response(title="User does not exist",
                              message='The specified user does not exist.',
                              code=404)

    if user.checked_in:
            return error_response(title="Already checked in",
                                  message='The user specified is already checked in. Please see an organizer.',
                                  code=409)

    user.check_in_times.append(datetime.datetime.now())
    user.checked_in = True
    user.save()

    return success_data_jsonify(user.check_in_dictionary_representation(), code=200)

@app.route('/user/checkout', methods=['POST'])
def check_out_user():
    json = request.get_json()
    if json is None:
        return invalid_format()

    if ADMIN_HEADER_FIELD not in request.headers:
        return error_response(title="No password",
                              message='To check in a user, please provide the admin password',
                              code=401)

    if 'username' not in json:
        return error_response(title="No username provided",
                              message='To check in a user, please provide the username of the user to check in',
                              code=400)

    username = json['username']
    password = request.headers[ADMIN_HEADER_FIELD]

    if os.environ['ADMIN_PASSWORD'] != password:
        return error_response(title="Invalid password",
                              message='To check in a user, please provide the correct shared password',
                              code=401)

    user = User.objects(username=username).first()
    if user is None:
        return error_response(title="User does not exist",
                              message='The specified user does not exist.',
                              code=404)

    if not user.checked_in:
            return error_response(title="Never checked in",
                                  message='The user specified never checked in. Please see an organizer.',
                                  code=409)

    user.check_out_times.append(datetime.datetime.now())
    user.checked_in = False
    user.save()
    return success_data_jsonify(user.check_in_dictionary_representation(), code=200)




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
    if request is None:
        return None
    if AUTHORIZATION_HEADER_FIELD in request.headers:
        token = request.headers[AUTHORIZATION_HEADER_FIELD]
        return User.verify_auth_token(token)
    return None


