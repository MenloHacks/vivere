
import datetime

from flask import Flask

import flask_admin as admin
from flask_mongoengine import MongoEngine
from flask_admin.contrib.mongoengine import ModelView
import os

app = Flask(__name__)
# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'
app.config['MONGODB_SETTINGS'] = {'DB': 'testing'}

# Create models
if 'MONGODB_URI' in os.environ:
    db = MongoEngine(os.environ['MONGODB_URI'])
else:
    db = MongoEngine()

db.init_app(app)



from views import *




if __name__ == '__main__':
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



    app.run(debug=True)

