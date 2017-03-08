from configuration import app
from flask_mongoengine import MongoEngine
from models import MentorTicket
from flask import request
import datetime
from authentication import current_user
from utils import success_data_jsonify, error_response, invalid_format
import bson
import threading
from notification import send_mentor_expiration



def mark_expired():
    current_time = datetime.datetime.utcnow()
    expiry_time = current_time - datetime.timedelta(seconds=MentorTicket.EXPIRATION_TIME)
    #in case we miss it for some reason
    expiry_time_cutoff = expiry_time - datetime.timedelta(minutes=2)

    expired_tickets = MentorTicket.objects(time_complete=None, time_opened__lt=expiry_time, time_opened__gte=expiry_time_cutoff,
                                           claimed_by=None).order_by('-time_created')

    list = []
    for t in expired_tickets:
        list.append(t.dictionary_representation())

    if len(list) > 0:
        send_mentor_expiration(list)

    threading.Timer(60, mark_expired).start()


mark_expired()

@app.route('/mentorship/create', methods=['POST'])
def create_ticket():
    json = request.get_json()
    if json is None:
        return invalid_format()

    if 'description' not in json:
        return error_response(title="No description provided",
                              message="Please enter a brief description of the problem you are having",
                              code=400)

    if 'location' not in json:
        return error_response(title="No location provided",
                              message="Please tell the mentor where you are currently set up",
                              code=400)

    if 'contact' not in json:
        return error_response(title="No contact information provided",
                              message="Please provide a way for the mentor to contact you",
                              code=400)

    user = current_user()
    if user is None:
        return error_response(title="No user is currently logged in",
                              message="In order to create a ticket, you must be logged in",
                              code=401)

    description = json['description']
    location = json['location']
    contact = json['contact']

    if len(description) == 0:
        return error_response(title="Ticket description is blank",
                              message="Please enter a brief description of the problem you are having",
                              code=400)
    if len(location) == 0:
        return error_response(title="Location is blank",
                              message="Please tell the mentor where you are currently set up",
                              code=400)
    if len(contact) == 0:
        return error_response(title="Contact information is blank",
                              message="Please provide a way for the mentor to contact you",
                              code=400)

    ticket = MentorTicket()

    ticket.description = description
    ticket.location = location
    ticket.contact = contact
    ticket.time_created = datetime.datetime.utcnow()
    ticket.time_opened = datetime.datetime.utcnow()

    ticket.created_by = user

    ticket.save()

    return success_data_jsonify(ticket.dictionary_representation(), code=201)

@app.route('/mentorship/user/queue')
def get_user_tickets():
    user = current_user()
    if user is None:
        return error_response(title="No user is currently logged in",
                              message="In order to create a ticket, you must be logged in",
                              code=401)
    else:
        current_time = datetime.datetime.utcnow()
        expiry_time = current_time - datetime.timedelta(seconds=MentorTicket.EXPIRATION_TIME)

        open_tickets = MentorTicket.objects(time_opened__gte=expiry_time, claimed_by=None, created_by=user, time_opened__ne=None, time_complete=None).order_by('-time_created')
        closed_tickets = MentorTicket.objects(time_complete__ne=None, created_by=user).order_by('-time_created')
        expired_tickets = MentorTicket.objects(time_complete=None, created_by=user, time_opened__lt=expiry_time, claimed_by=None).order_by('-time_created')
        in_progress_tickets = MentorTicket.objects(time_complete=None, created_by=user, claimed_by__ne=None).order_by('-time_created')

        tickets = {}


        list = []
        for t in open_tickets:
            list.append(t.dictionary_representation())

        tickets['open'] = list

        list = []
        for t in in_progress_tickets:
            list.append(t.dictionary_representation())


        tickets['in_progress'] = list

        list = []
        for t in expired_tickets:
            list.append(t.dictionary_representation())


        tickets['expired'] = list

        list = []
        for t in closed_tickets:
            list.append(t.dictionary_representation())



        tickets['closed'] = list




        response = {}


        response['tickets'] = tickets
        response['categories'] = ['open', 'in_progress', 'expired', 'closed']


        return success_data_jsonify(response)


@app.route('/mentorship/user/claimed')
def claimed_tickets():
    user = current_user()
    if user is None:
        return error_response(title="No user is currently logged in",
                              message="In order to create a ticket, you must be logged in",
                              code=401)
    else:
        claimed_tickets = MentorTicket.objects(time_complete=None, claimed_by=user).order_by('time_created')

        list = []
        for t in claimed_tickets:
            list.append(t.dictionary_representation())

        return success_data_jsonify(list)




@app.route('/mentorship/queue')
def get_tickets():

    current_time = datetime.datetime.utcnow()
    expiry_time = current_time - datetime.timedelta(seconds=MentorTicket.EXPIRATION_TIME)

    tickets = MentorTicket.objects(time_opened__gte=expiry_time, claimed_by=None, time_complete=None).order_by('time_created')

    tickets_list = []
    for t in tickets:
        tickets_list.append(t.dictionary_representation())


    return success_data_jsonify(tickets_list)



@app.route('/mentorship/claim', methods=['POST'])
def claim_ticket():
    json = request.get_json()
    if json is None:
        return invalid_format()

    if 'id' in json:
        id = json['id']
        if len(id) == 0:
            return error_response(title="Ticket ID is blank",
                                  message="Please choose a ticket to claim.",
                                  code=404)

        if not bson.objectid.ObjectId.is_valid(id):
            return error_response(title="Invalid Ticket ID",
                                  message="The ticket ID provided is not a valid ID",
                                  code=400)

        ticket = MentorTicket.objects(id=id).first()

        if ticket is None:
            return error_response(title="Ticket does not exist",
                                  message="You cannot claim a ticket that does not exist.",
                                  code=404)

        user = current_user()

        if user is None:
            return error_response(title="No user is currently logged in",
                                  message="In order to claim a ticket, you must be logged in",
                                  code=401)

        if ticket.claimed_by is not None:
            return error_response(title="Ticket already claimed",
                                  message="Someone's already on this one. Try another?",
                                  code=409)

        ticket.claimed_by = user
        ticket.time_claimed = datetime.datetime.utcnow()
        ticket.save()

        return success_data_jsonify(ticket.dictionary_representation())

    else:
        return error_response(title="No ticket provided.",
                              message="Please choose a ticket to claim",
                              code=400)

@app.route('/mentorship/reopen', methods=['POST'])
def reopen_ticket():
    json = request.get_json()
    if json is None:
        return invalid_format()
    if 'id' not in json:
        return error_response(title="No ticket provided.",
                              message="Please choose a ticket to claim",
                              code=400)
    else:
        id = json['id']
        if not bson.objectid.ObjectId.is_valid(id):
            return error_response(title="Invalid Ticket ID",
                                  message="The ticket ID provided is not a valid ID",
                                  code=400)
        user = current_user()
        if user is None:
            return error_response(title="No user is currently logged in",
                                  message="In order to re-open a ticket, you must be logged in",
                                  code=401)

        ticket = MentorTicket.objects(id=request.json['id']).first()
        if ticket is None:
            return error_response(title="Cannot close this ticket",
                                  message="In order to close a ticket, you must either be the mentor or the mentee",
                                  code=403)

        current_time = datetime.datetime.utcnow()
        expiry_time = current_time - datetime.timedelta(seconds=MentorTicket.EXPIRATION_TIME)

        if ticket.claimed_by == None and ticket.time_complete == None and ticket.time_opened > expiry_time:
            return error_response(title="Cannot re-open this ticket",
                                  message="This ticket is currently open",
                                  code=403)

        if ticket.created_by == user or ticket.claimed_by == user:
            ticket.claimed_by = None
            ticket.time_complete = None
            ticket.time_opened = datetime.datetime.utcnow()
            ticket.save()
            return success_data_jsonify(ticket.dictionary_representation())
        else:
            return error_response(title="Cannot re-open this ticket",
                                  message="In order to re-open a ticket, you must either be the mentor or the mentee",
                                  code=403)

@app.route('/mentorship/close', methods=['POST'])
def close_ticket():
    json = request.get_json()
    if json is None:
        return invalid_format()
    if 'id' not in request.json:
        return error_response(title="No ticket ID provided",
                              message="Please specifiy a ticket to close",
                              code=401)
    else:
        id = json['id']
        if not bson.objectid.ObjectId.is_valid(id):
            return error_response(title="Invalid Ticket ID",
                                  message="The ticket ID provided is not a valid ID",
                                  code=400)
        user = current_user()

        if user is None:
            return error_response(title="No user is currently logged in",
                                  message="In order to close a ticket, you must be logged in",
                                  code=401)

        ticket = MentorTicket.objects(id=request.json['id']).first()
        if ticket is None:
            return error_response(title="Ticket does not exist",
                                  message="The specified ticket does not exist",
                                  code=404)

        if ticket.created_by == user or ticket.claimed_by == user:
            ticket.time_complete = datetime.datetime.utcnow()
            ticket.save()
            return success_data_jsonify(ticket.dictionary_representation())

        else:
            return error_response(title="Cannot close this ticket",
                                  message="In order to close a ticket, you must either be the mentor or the mentee",
                                  code=403)




