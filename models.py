from flask_mongoengine import MongoEngine
from configuration import db, app

from flask import request
import datetime
from notification import send_announcement_update, send_event_update, send_mentor_update, broadcast_apns

class Location(db.Document):
    LOCATION_IMAGE_PATH = 'location/image/'
    name = db.StringField()

    map = db.FileField()
    rank = db.IntField(default=-1)



    def dictionary_representation(self):
        if request is not None and request.url_root:
            map_url = request.url_root + self.LOCATION_IMAGE_PATH + str(self.id)
            map_url = map_url.replace('http', 'https')
            dictionary = {
                'name' : self.name,
                'map' : map_url,
                'id' : str(self.id)
            }
        else:
            dictionary = {
                'name' : self.name,
                'id' : str(self.id)
            }
        if self.rank > 0:
            dictionary['rank'] = self.rank
            dictionary['is_primary'] = True
        else:
            dictionary['is_primary'] = False
        return dictionary

    def __unicode__(self):
        return self.name



class Event(db.Document):
    start_time = db.DateTimeField(default=datetime.datetime.now())
    end_time = db.DateTimeField(default=datetime.datetime.now())

    short_description = db.StringField()
    long_description = db.StringField()

    location = db.ReferenceField(Location, required=False)

    def save(self):
        send_event_update(event=self)
        super(Event, self).save()

    def dictionary_representation(self):
        return {
            'start_time' : self.start_time.isoformat(),
            'end_time' : self.end_time.isoformat(),
            'short_description' : self.short_description,
            'long_description' : self.long_description,
            'location' : self.location.dictionary_representation(),
            'id' : str(self.id)
        }


    def __unicode__(self):
        return self.long_description


class Announcement(db.Document):
    message = db.StringField()
    time = db.DateTimeField(default=datetime.datetime.now())

    push_notification_sent = db.BooleanField(default=False)


    def save(self):
        if self.push_notification_sent == False:
            broadcast_apns(self)
            self.push_notification_sent = True
        send_announcement_update(announcement=self)
        super(Announcement, self).save()

    def dictionary_representation(self):
        return {
            'message' : self.message,
            'time' :  self.time.isoformat(),
            'id': str(self.id)
        }

    def __unicode__(self):
        return self.title


from passlib.hash import django_pbkdf2_sha256
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

class User(db.Document):
    username = db.StringField(unique=True)
    hashed_password = db.StringField()

    name = db.StringField()
    school = db.StringField()

    photo_form_url = db.StringField()
    liability_form_url = db.StringField()

    dietary_restrictions = db.StringField()

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
        self.hashed_password = django_pbkdf2_sha256.using(rounds=3000).hash(password)

    def generate_auth_token(self, expiration = 108000):
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
        return django_pbkdf2_sha256.verify(password, password_hash)

    def __unicode__(self):
        return self.username

class MentorTicket(db.Document):

    EXPIRATION_TIME = 1800 #automatically expire after 30 minutes.

    description = db.StringField()
    location = db.StringField()
    contact = db.StringField()


    claimed_by = db.ReferenceField(User, required=False)
    created_by = db.ReferenceField(User)

    time_created = db.DateTimeField(default=datetime.datetime.now())
    time_opened = db.DateTimeField(default=datetime.datetime.now())
    time_claimed = db.DateTimeField()
    time_complete = db.DateTimeField()

    def save(self):
        send_mentor_update(ticket=self)
        super(MentorTicket, self).save()

    def dictionary_representation(self):
        current_time = datetime.datetime.now()
        expiry_time = self.time_opened + datetime.timedelta(seconds=MentorTicket.EXPIRATION_TIME)

        dictionary = {
            'description' : self.description,
            'location' : self.location,
            'contact' : self.contact,
            'claimed' : self.claimed_by  != None,
            'expired' : current_time > expiry_time,
            'time_created' : self.time_created.isoformat(),
            'id' : str(self.id),
        }

        if self.time_complete is None:
            dictionary['time_complete'] = None
        else:
            dictionary['time_complete'] = self.time_complete.isoformat()




        return dictionary







