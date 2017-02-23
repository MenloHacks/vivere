
import datetime

from flask import Flask

import flask_admin as admin
from flask_mongoengine import MongoEngine
from flask_admin.contrib.mongoengine import ModelView
import os

app = Flask(__name__)
# Create dummy secrey key so we can use sessions

app.config['SECRET_KEY'] = '123456790'

# Create models
if 'MONGODB_URI' in os.environ:
    app.config['MONGODB_SETTINGS'] = {
        'DB' : 'test', #remember to change this to prod.
        'host' : os.environ['MONGODB_URI']
    }
    db = MongoEngine()
else:
    app.config['MONGODB_SETTINGS'] = {'DB': 'testing'}
    db = MongoEngine()

db.init_app(app)



from views import *




    # Create application

    # Create admin
admin = admin.Admin(app, 'MenloHacks Vivere')

from models import Announcement, Event, Location, MentorTicket

    # Add views
admin.add_views(ModelView(Announcement))
admin.add_view(ModelView(Event))
admin.add_views(ModelView(Location))
admin.add_views(ModelView(User))
admin.add_views(ModelView(MentorTicket))


port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)

