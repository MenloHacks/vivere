import pusher
import os
from constants import ALL_DEVICES_APNS, MENTOR_UPDATE, ANNOUNCEMENT_UPDATE, EVENT_UPDATE

pusher_client = pusher.Pusher(os.environ['pusher_app_id'], os.environ['pusher_key'], os.environ['pusher_secret'])


def send_notification(message, channel_name):
    alert_payload = {
        'body': message
    }

    payload = {
        'apns': {
            'aps': {
                'alert': alert_payload
            }
        }}


    pusher_client.notify([channel_name], payload)


def send_event_update(event):
    pusher_client.trigger(EVENT_UPDATE, u'save', event.dictionary_representation())

def send_announcement_update(announcement):
    pusher_client.trigger(ANNOUNCEMENT_UPDATE, u'save', announcement.dictionary_representation())

def send_mentor_update(ticket):
    pusher_client.trigger(MENTOR_UPDATE, u'save', ticket.dictionary_representation())




def broadcast_apns(announcement):
    send_notification(announcement.message, ALL_DEVICES_APNS)



