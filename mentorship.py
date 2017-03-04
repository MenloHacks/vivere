from configuration import app
from flask_mongoengine import MongoEngine
from models import MentorTicket
from flask import request
import datetime
from authentication import current_user
from utils import success_data_jsonify, error_response

@app.route('/mentorship/create', methods=['POST'])
def create_ticket():
    if not 'description' in request.json:
        return error_response('Missing parameter description', code=400)

    if not 'location' in request.json:
        return error_response('Missing parameter location', code=400)

    if not 'contact' in request.json:
        return error_response('Missing parameter contact', code=400)

    user = current_user()
    if user is None:
        return error_response('No logged in user', code=401)

    ticket = MentorTicket()

    ticket.description = request.json['description']
    ticket.location = request.json['location']
    ticket.contact = request.json['contact']
    ticket.time_created = datetime.datetime.utcnow()
    ticket.time_opened = datetime.datetime.utcnow()

    ticket.created_by = user

    ticket.save()

    return success_data_jsonify(ticket.dictionary_representation(), code=201)

@app.route('/mentorship/user/queue')
def get_user_tickets():
    user = current_user()
    if user is None:
        return error_response('No logged in user', code=401)
    else:
        current_time = datetime.datetime.utcnow()
        expiry_time = current_time - datetime.timedelta(seconds=MentorTicket.EXPIRATION_TIME)

        open_tickets = MentorTicket.objects(time_opened__gte=expiry_time, claimed_by=None, created_by=user).order_by('-time_created')
        closed_tickets = MentorTicket.objects(time_complete__ne=None, created_by=user).order_by('-time_created')
        expired_tickets = MentorTicket.objects(time_complete=None, created_by=user, time_opened__lt=expiry_time, claimed_by=None).order_by('-time_created')
        in_progress_tickets = MentorTicket.objects(time_complete=None, created_by=user, claimed_by__ne=None).order_by('-time_created')

        response = {}

        list = []
        for t in open_tickets:
            list.append(t.dictionary_representation())
        response['open'] = list

        list = []
        for t in closed_tickets:
            list.append(t.dictionary_representation())
        response['closed'] = list

        list = []
        for t in expired_tickets:
            list.append(t.dictionary_representation())
        response['expired'] = list

        list = []
        for t in in_progress_tickets:
            list.append(t.dictionary_representation())
        response['in_progress'] = list

        return success_data_jsonify(response)


@app.route('/mentorship/user/claimed')
def claimed_tickets():
    user = current_user()
    if user is None:
        return error_response('No user is currently logged in', code=401)
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
    if 'id' in request.json:
        id = request.json['id']
        ticket = MentorTicket.objects(id=id).first()

        if ticket is None:
            return error_response('No ticket exists with specified ID', code=404)

        user = current_user()

        if user is None:
            return error_response("No current user logged in", code=401)

        if ticket.claimed_by is not None:
            return error_response('Ticket is already claimed', code=409)

        ticket.claimed_by = user
        ticket.time_claimed = datetime.datetime.utcnow()
        ticket.save()
        return success_data_jsonify(ticket.dictionary_representation())

    else:
        return error_response('Missing parameter ticket_id', code=400)

@app.route('/mentorship/reopen', methods=['POST'])
def reopen_ticket():
    if not 'id' in request.json:
        return error_response('Missing parameter id', code=400)
    else:
        user = current_user()
        if user is None:
            return error_response('No current user logged in', code=401)

        ticket = MentorTicket.objects(id=request.json['id']).first()
        if ticket is None:
            return error_response('No ticket with specified ID', code=404)

        if ticket.claimed_by == None and ticket.time_complete == None:
            return error_response('Ticket currently open.')

        if ticket.created_by == user or ticket.claimed_by == user:
            ticket.claimed_by = None
            ticket.time_complete = None
            ticket.time_opened = datetime.datetime.utcnow()
            ticket.save()
            return success_data_jsonify(ticket.dictionary_representation())
        else:
            return error_response('Invalid permissions', code=403)

@app.route('/mentorship/close', methods=['POST'])
def close_ticket():
    if not 'id' in request.json:
        return error_response('Missing parameter id', code=400)
    else:

        user = current_user()
        if user is None:
            return error_response('No current user logged in', code=401)

        ticket = MentorTicket.objects(id=request.json['id']).first()
        if ticket is None:
            return error_response('No ticket with specified ID', code=404)

        if ticket.created_by == user or ticket.claimed_by == user:
            ticket.time_complete = datetime.datetime.utcnow()
            return success_data_jsonify(ticket.dictionary_representation())

        else:
            return error_response('Invalid permissions', code=403)




