import os
import json


def load_data():
    if not os.path.exists("./data/profiles.json"):
        raise FileNotFoundError("File does not exist!")

    with open("data/profiles.json", "r") as file:
        return json.load(file)


def get_authorized_profile():
    contents = load_data()
    return contents["authorized"]
