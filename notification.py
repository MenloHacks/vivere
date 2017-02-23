import pusher
import os
from constants import ALL_DEVICES_APNS, ALL_DEVICES_UPDATE

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


def send_live_notif(event, payload):
    pusher_client.trigger(ALL_DEVICES_UPDATE, event, payload)


def broadcast_apns(announcement):
    send_notification(announcement.title, announcement.contents, ALL_DEVICES_APNS)



