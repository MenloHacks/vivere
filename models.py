from flask_mongoengine import MongoEngine
from vivere import db

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