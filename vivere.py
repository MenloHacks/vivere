from flask import Flask
from flask_superadmin import Admin, model
from mongoengine import *

# Create application
app = Flask(__name__)

# Create dummy secret key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

connect('menlohacks')
# db = MongoEngine(app)


# Defining MongoEngine Documents

class Event(Document):
    start_time = DateTimeField()
    end_time = DateTimeField()

    short_description = StringField()
    long_description = StringField()

    def __unicode__(self):
        return self.short_description




# Flask views
@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


if __name__ == '__main__':
    # Create admin
    admin = Admin(app)

    class EventModel(model.ModelAdmin):
        list_display = ('start_time', 'end_time', 'short_description', 'long_description')


    # Register the models
    admin.register(Event, EventModel)

    # Start app
    app.debug = True
    app.run()

