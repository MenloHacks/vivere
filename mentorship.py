from vivere import app
from flask_mongoengine import MongoEngine
from models import MentorTicket
from flask import request
import datetime
from authentication import current_user
from utils import success_data_jsonify, error_response

@app.route('/mentorship/create', methods=['POST'])
def create_ticket():
    pass

@app.route('/mentorship/tickets')
def get_tickets():
    if 'start' in request.args:
        start = int(request.args['start'])
    else:
        start = 0

    if 'count' in request.args:
        count = int(request.args['count'])
    else:
        count = 20



    current_time = datetime.datetime.now()
    expiry_time = current_time - datetime.timedelta(seconds=MentorTicket.EXPIRATION_TIME)

    response = {}

    user = current_user()
    if start == 0 and user is not None:
        list = []
        user_tickets = MentorTicket.objects(time_created__gte=expiry_time, claimed_by=None, created_by=user).order_by('-time_created').skip(
            start).limit(count)

        for t in user_tickets:
            list.append(t.dictionary_representation())

        response['user_created'] = list

    tickets  = MentorTicket.objects(time_created__gte=expiry_time, claimed_by=None, created_by__ne=user).order_by('time_created').skip(start).limit(count)

    tickets_list = []
    for t in tickets:
        tickets_list.append(t.dictionary_representation())

    response['queue'] = tickets_list

    return success_data_jsonify(response)



@app.route('/mentorship/claim', methods=['POST'])
def claim_ticket():
    if 'ticket_id' in request.json:
        id = request.json['ticket_id']
        ticket = MentorTicket.objects(id=id)

        if ticket is None:
            return error_response('No ticket exists with specified ID', code=404)

        user = current_user()

        if user is None:
            return error_response("No current user logged in", code=401)

        if user.is_mentor == False:
            return error_response('User is not a mentor', code=403)

        ticket.claimed_by = user
        ticket.save()

    else:
        return error_response('Missing parameter ticket_id', code=400)

@app.route('/mentorship/reopen', methods=['POST'])
def open_ticket():
    pass


