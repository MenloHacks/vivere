import flask_admin as admin
from flask_admin.contrib.mongoengine import ModelView
import flask_login as login
import os

from configuration import *
from werkzeug.contrib.fixers import ProxyFix

app.wsgi_app = ProxyFix(app.wsgi_app)

from views import *


from admin_login_manager import *
admin = admin.Admin(app, 'MenloHacks Vivere', index_view=SecureAdminIndexView(), base_template='my_master.html')

from models import Announcement, Event, EventLocation, MentorTicket


class SecureModelView(ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated and login.current_user.is_admin

    # Add views
admin.add_views(SecureModelView(Announcement))
admin.add_view(SecureModelView(Event))
admin.add_views(SecureModelView(EventLocation))
admin.add_views(SecureModelView(User))
admin.add_views(SecureModelView(MentorTicket))


# if __name__ == '__main__':
#     app.run()


