
import datetime

from flask import Flask

import flask_admin as admin
from flask_mongoengine import MongoEngine
from flask_admin.contrib.mongoengine import ModelView

app = Flask(__name__)
# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'
app.config['MONGODB_SETTINGS'] = {'DB': 'testing'}

# Create models
db = MongoEngine()
db.init_app(app)


from views import *


if __name__ == '__main__':
    # Create application

    # Create admin
    admin = admin.Admin(app, 'MenloHacks Vivere')

    from models import Announcement, Event, Location

    # Add views
    admin.add_views(ModelView(Announcement))
    admin.add_view(ModelView(Event))
    admin.add_views(ModelView(Location))



    app.run(debug=True)

