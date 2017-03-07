from models import Announcement, Event, EventLocation, User
from constants import EVENT_END_TIME, EVENT_START_TIME, HACKING_START_TIME, HACKING_END_TIME
from utils import error_response, success_data_jsonify

from configuration import app
from flask import Flask, request, make_response
import datetime
import os
import bson


# Flask views

@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'

@app.route('/times')
def get_times():
    return success_data_jsonify({
        'event_start_time' : EVENT_START_TIME.isoformat(),
        'event_end_time' : EVENT_END_TIME.isoformat(),
        'hacking_start_time' : HACKING_START_TIME.isoformat(),
        'hacking_end_time' : HACKING_END_TIME.isoformat()
    })


@app.route('/' + EventLocation.LOCATION_IMAGE_PATH + '<location_id>')
def serve_location_image(location_id):
    if not bson.objectid.ObjectId.is_valid(location_id):
        return error_response(title="Invalid Location",
                              message="The location you provided is not a valid location",
                              code=400)
    location = Location.objects(id=location_id).first()
    if location is None:
        return error_response(title="Location not found",
                              message="",
                              code=404)
    else:
        response = make_response(location.map.read())
        response.mimetype = location.map.content_type
        return response


@app.route('/maps')
def get_maps():
    locations = EventLocation.objects(rank__gt=0).order_by('rank')
    list = []

    for l in locations:
        list.append(l.dictionary_representation())

    return success_data_jsonify(list)



@app.route('/announcements')
def get_announcements():


    if 'since_date' in request.args:
        cutoff = datetime.datetime.strptime(request.args['since_date'], "%Y-%m-%dT%H:%M:%S")
    else:
        cutoff = datetime.datetime.fromtimestamp(0)

    announcements = Announcement.objects(time__lte=datetime.datetime.utcnow(), time__gt=cutoff).order_by('-time')

    list = []
    for a in announcements:
        list.append(a.dictionary_representation())
    return success_data_jsonify(list)



@app.route('/events')
#shouldn't be too many so I'll send them all at once.
def get_events():
    events = Event.objects().order_by('start_time')
    list = []
    for a in events:
        list.append(a.dictionary_representation())
    return success_data_jsonify(list)


@app.route('/twilio/announcement', methods=['POST'])
def create_announcement():
    APPROVED_NUMBERS = ['+16502136962', '+16506531870', '+16505752753', '+16507431787']
    body = request.form['Body']
    from_number = request.form['From']
    account_sid = request.form['AccountSid']
    if from_number in APPROVED_NUMBERS and account_sid == os.environ['TWILIO_SID']:
        a = Announcement()
        a.message = body
        a.time = datetime.datetime.utcnow()
        a.save()
    return success_data_jsonify({})


from authentication import *
from mentorship import *