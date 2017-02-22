from flask_mongoengine import MongoEngine
from vivere import db, app

from flask import request
import datetime

class Location(db.Document):
    LOCATION_IMAGE_PATH = 'location/image/'
    name = db.StringField()

    map = db.FileField()
    rank = db.IntField(default=-1)



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


import bcrypt
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

class User(db.Document):
    username = db.StringField(unique=True)
    hashed_password = db.StringField()

    name = db.StringField()

    is_admin = db.BooleanField(default=False)



    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def set_password(self, password):
        self.hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(14))

    def generate_auth_token(self, expiration = 3600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'username': self.username })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but ex
            # pired
        except BadSignature:
            return None # invalid token

        user = User.objects(username=data['username']).first()
        return user

    @staticmethod
    def validate_login(password_hash, password):
        return bcrypt.hashpw(password.encode('utf8'), password_hash.encode('utf8')) == password_hash

