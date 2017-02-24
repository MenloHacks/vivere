from flask import Flask

from flask_mongoengine import MongoEngine
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