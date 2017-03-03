from flask import Flask

from flask_mongoengine import MongoEngine
import os

from flask_cors import CORS

app = Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

if 'SECRET_KEY' in os.environ:
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
else:
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