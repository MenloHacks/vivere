import flask_admin as admin
from flask_admin.contrib.mongoengine import ModelView
import os

from configuration import *

from views import *

admin = admin.Admin(app, 'MenloHacks Vivere')

from models import Announcement, Event, EventLocation, MentorTicket

    # Add views
admin.add_views(ModelView(Announcement))
admin.add_view(ModelView(Event))
admin.add_views(ModelView(EventLocation))
admin.add_views(ModelView(User))
admin.add_views(ModelView(MentorTicket))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

