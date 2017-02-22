from models import Announcement, Event, Location, User
from constants import EVENT_END_TIME, EVENT_START_TIME
from utils import error_response, success_data_jsonify

from vivere import app
from flask import Flask, request, make_response


# Flask views

@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'

@app.route('/times')
def get_times():
    return success_data_jsonify({
        'start' : EVENT_START_TIME.isoformat(),
        'end' : EVENT_END_TIME.isoformat()
    })


@app.route('/' + Location.LOCATION_IMAGE_PATH + '<location_id>')
def serve_location_image(location_id):
    success = True
    try:
        location = Location.objects(id=location_id).first()
    except:
        success = False

    if success == False:
        return error_response(message='Invalid object ID', code=400)

    if location is None:
        return error_response(message='Location not found', code=400)

    response = make_response(location.map.read())
    response.mimetype = location.map.content_type
    return response


@app.route('/maps')
def get_maps():
    locations = Location.objects(rank__gt=0).order_by('rank')
    list = []

    for l in locations:
        list.append(l.dictionary_representation())

    return success_data_jsonify(list)



@app.route('/announcements')
def get_announcements():
    if 'start' in request.args:
        start = int(request.args['start'])
    else:
        start = 0

    if 'count' in request.args:
        count = int(request.args['count'])
    else:
        count = 20

    announcements = Announcement.objects(time__lte=datetime.datetime.now()).order_by('-time').skip(start).limit(count)
    list = []
    for a in announcements:
        list.append(a.dictionary_representation())
    return success_data_jsonify(list)


@app.route('/events')
def get_events():
    if 'start' in request.args:
        start = int(request.args['start'])
    else:
        start = 0

    if 'count' in request.args:
        count = int(request.args['count'])
    else:
        count = 20

    events = Event.objects().order_by('-start_time').skip(start).limit(count)
    list = []
    for a in events:
        list.append(a.dictionary_representation())
    return success_data_jsonify(list)


from flask_login import  LoginManager

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


@app.route('/user/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    if username is None:
        return error_response(message='Missing parameter username', code=400)
    if password is None:
        return error_response(message='Missing parameter password', code=400)

    user = User.objects(username=username).first()

    if user is None:
        return error_response(message="No user exists with this username", code=404)

    if User.validate_login(user.hashed_password, password):
        token = user.generate_auth_token()
        return success_data_jsonify({'name' : user.name,
                                     'token' : token})
    else:
        return error_response(message='Invalid password', code=403)




@login_manager.user_loader
def load_user(username):

    user = User.objects(username=username).first()
    if not user:
        return None
    else:
        return user