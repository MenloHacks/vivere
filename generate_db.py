from models import User
import csv
import os

USER_FILENAME = 'users.csv'
PROFILE_FILENAME = 'profiles.csv'
APPLICATION_FILENAME = 'applications.csv'

def generate_db():
    dir = os.path.dirname(__file__)
    folder = 'secure/'

    user_path = folder + USER_FILENAME
    profile_path = folder + PROFILE_FILENAME
    applicaton_path = folder + APPLICATION_FILENAME

    username_dictionary = {}


    user_location = os.path.join(dir, user_path)
    profile_location = os.path.join(dir, profile_path)
    application_location = os.path.join(dir, applicaton_path)

    with open(user_location, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            username = row['username']
            user = User.objects(username=username).first()
            if user is None:
                user = User()

            password = row['password']

            user_id = row['id']
            username_dictionary[user_id] = username

            user.username = username
            user.hashed_password = password

            user.save()

    with open(profile_location, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:

            user_id = row['user_id']
            username = username_dictionary[user_id]

            user = User.objects(username=username).first()

            if user is None:
                break

            school = row['school']
            tshirt = row['t_shirt_size']

            user.school = school
            user.tshirt_size = tshirt

            user.save()

    with open(application_location, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_id = row['user_id']
            username = username_dictionary[user_id]

            user = User.objects(username=username).first()

            if user is None:
                break

            liability = row['form_url']
            photo_form = row['photo_form_url']

            user.liability_form_url = liability
            user.photo_form_url = photo_form

            user.save()
