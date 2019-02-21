from flask import Flask

from flask_mongoengine import MongoEngine
import os

from flask_cors import CORS

app = Flask(__name__)
import os

#configure s3
import boto.s3.connection
access_key = os.environ['S3_ACCESS_KEY']
secret_key = os.environ['S3_SECRET_KEY']


conn = boto.s3.connect_to_region(
        'us-west-1',
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        host = 's3.amazonaws.com',
        #is_secure=False,               # uncomment if you are not using ssl
        #calling_format = boto.s3.connection.OrdinaryCallingFormat(),
        )


MENLOHACKS_BUCKET_NAME = 'menlohacksiv'
MENLOHACKS_PASSBOOK_KEY_FILENAME = 'pass.pem'


bucket = conn.get_bucket(MENLOHACKS_BUCKET_NAME)
key = bucket.get_key(MENLOHACKS_PASSBOOK_KEY_FILENAME)

dir = os.path.dirname(__file__)
path = 'secure/' + MENLOHACKS_PASSBOOK_KEY_FILENAME
filename = os.path.join(dir, path)

key.get_contents_to_filename(filename)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']


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