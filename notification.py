import pusher
import os
from constants import ALL_DEVICES_APNS, MENTOR_UPDATE, ANNOUNCEMENT_UPDATE, EVENT_UPDATE

pusher_client = pusher.Pusher(os.environ['pusher_app_id'], os.environ['pusher_key'], os.environ['pusher_secret'])


def send_notification(title, body, channel_name):
    alert_payload = {
        'body': body
    }
    if title is not None and len(title) > 0:
        alert_payload['title'] = title

    payload = {
        'apns': {
            'aps': {
                'alert': alert_payload
            }
        }}


    pusher_client.notify([channel_name], payload)


def send_event_update(event):
    pusher.trigger(EVENT_UPDATE, u'save', event.dictionary_representation())

def send_announcement_update(announcement):
    pusher.trigger(ANNOUNCEMENT_UPDATE, u'save', announcement.dictionary_representation())

def send_mentor_update(ticket):
    pusher.trigger(MENTOR_UPDATE, u'save', ticket.dictionary_representation())




def broadcast_apns(announcement):
    send_notification(announcement.title, announcement.contents, ALL_DEVICES_APNS)



