
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

class Location(db.Document):
    name = db.StringField()
    map = db.FileField()

    def __unicode__(self):
        return self.name


# Define mongoengine documents
class Event(db.Document):
    start_time = db.DateTimeField()
    end_time = db.DateTimeField()

    short_description = db.StringField()
    long_description = db.StringField()

    location = db.ReferenceField(Location, required=False)


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


if __name__ == '__main__':
    # Create admin
    admin = admin.Admin(app, 'MenloHacks Vivere')

    # Add views
    admin.add_views(ModelView(Announcement))
    admin.add_view(ModelView(Event))
    admin.add_views(ModelView(Location))

    # Start app
    app.run(debug=True)