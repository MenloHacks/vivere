from flask import Flask

from flask_mongoengine import MongoEngine
import os

from flask_cors import CORS

app = Flask(__name__)


import boto.s3.connection
access_key = os.environ['S3_ACCESS_KEY']
secret_key = os.environ['h3bJOmACI8vq1Ks4lO5oM6BipH+TNfCGDxtzaoEK']



conn = boto.connect_s3(
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        host = 's3.amazonaws.com',
        #is_secure=False,               # uncomment if you are not using ssl
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
        )

bucket = conn.get_bucket('secure.menlohacks')
key = bucket.get_key('menlohacks-passbook-key.pem')

import os
dir = os.path.dirname(__file__)
filename = os.path.join(dir, 'secure/menlohacks-passbook-key.pem')

key.get_contents_to_filename(filename)

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