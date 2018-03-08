import csv
import os
import time
import urllib

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

            username = row["email"]

            user_id = row['id']
            username_dictionary[user_id] = {
                "application": row["application"],
                "profile": row["profile"],
                "username": username
            }

    with open(profile_location, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for user_row in username_dictionary:
                if username_dictionary[user_row]["profile"] == row["phone number"]:
                    if row["is menlo"] == '1':
                        username_dictionary[user_row]["is_menlo"] = True
                    else:
                        username_dictionary[user_row]["is_menlo"] = False

    with open(application_location, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for user_row in username_dictionary:
                if username_dictionary[user_row]["application"] == row["id"]:
                    if username_dictionary[user_row]["is_menlo"]:

                        liability = row['liability form']
                        photo_form = row['photo form']

                        testfile = urllib.URLopener()
                        testfile.retrieve(liability, "form")
                        os.system("lp form -d Neighborhood")

                        time.sleep(10)



if __name__ == "__main__":
    generate_db()