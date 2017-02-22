
import datetime

from flask import Flask
from flask import request
from flask import jsonify

import flask_admin as admin
from flask_mongoengine import MongoEngine
from flask_admin.form import rules
from flask_admin.contrib.mongoengine import ModelView

from utils import  *

# Create application
app = Flask(__name__)


# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'
app.config['MONGODB_SETTINGS'] = {'DB': 'testing'}

# Create models
db = MongoEngine()
db.init_app(app)


EVENT_START_TIME = datetime.datetime(year=2017, month=3, day=18, hour=2)
EVENT_END_TIME = datetime.datetime(year=2017, month=3, day=19, hour=0)

class Location(db.Document):
    LOCATION_IMAGE_PATH = 'location/image/'
    name = db.StringField()
    map = db.FileField()

    is_primary_location = db.BooleanField()

    def dictionary_representation(self):
        if request is not None and request.url_root:
            return {
                'name' : self.name,
                'map' : request.url_root + self.LOCATION_IMAGE_PATH + str(self.id)
            }
        else:
            return {
                'name' : self.name
            }

    def __unicode__(self):
        return self.name


# Define mongoengine documents
class Event(db.Document):
    start_time = db.DateTimeField()
    end_time = db.DateTimeField()

    short_description = db.StringField()
    long_description = db.StringField()

    location = db.ReferenceField(Location, required=False)

    def dictionary_representation(self):
        return {
            'start_time' : self.start_time.isoformat(),
            'end_time' : self.end_time.isoformat(),
            'short_description' : self.short_description,
            'long_description' : self.long_description,
            'location' : self.location.dictionary_representation()
        }


    def __unicode__(self):
        return self.long_description


class Announcement(db.Document):
    title = db.StringField()
    contents = db.StringField()
    time = db.DateTimeField(default=datetime.datetime.now())

    def dictionary_representation(self):
        return {
            'title' : self.title,
            'contents' : self.contents,
            'time' :  self.time.isoformat()
        }

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


from flask import make_response
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


if __name__ == '__main__':
    # Create admin
    admin = admin.Admin(app, 'MenloHacks Vivere')

    # Add views
    admin.add_views(ModelView(Announcement))
    admin.add_view(ModelView(Event))
    admin.add_views(ModelView(Location))

    # Start app
    app.run(debug=True)