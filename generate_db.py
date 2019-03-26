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
            username = row['email']
            user = User.objects(username=username).first()
            if user is None:
                user = User()
            if username == "mitsuka.kiyohara@menloschool.org" or username=="thomas.woodside@gmail.com":
                user.is_admin = True

            password = row['password']


            user_id = row['id']
            username_dictionary[user_id] = {
                "application": row["application"],
                "profile": row["profile"],
                "username": username
            }

            user.username = username
            user.hashed_password = password

            user.save()

    with open(profile_location, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for user_row in username_dictionary:
                if username_dictionary[user_row]["profile"] == row["phone number"]:
                    user = User.objects(username=username_dictionary[user_row]["username"]).first()

                    if user is None:
                        break

                    school = row['school']
                    tshirt = row['shirt size']
                    name = row['first name'] + " " + row['last name']

                    user.school = school
                    user.name = name
                    user.tshirt_size = tshirt

                    user.save()

    with open(application_location, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for user_row in username_dictionary:
                if username_dictionary[user_row]["application"] == row["id"]:
                    user = User.objects(username=username_dictionary[user_row]["username"]).first()

                    if user is None:
                        break

                    liability = row['liability form']
                    photo_form = row['photo form']

                    user.liability_form_url = liability
                    user.photo_form_url = photo_form

                    user.save()


if __name__ == "__main__":
    generate_db()
