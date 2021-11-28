import os
import json

# Local modules
from src.utils.constants import HOME_DIR


def load_data():
    if not os.path.exists(f"{HOME_DIR}/gpc-data/profiles.json"):
        raise FileNotFoundError("File does not exist!")

    with open(f"{HOME_DIR}/gpc-data/profiles.json", "r") as file:
        return json.load(file)


def get_authorized_profile():
    contents = load_data()
    return contents["authorized"]


def get_saved_profiles():
    contents = load_data()
    return contents["profiles"]


def write_profile(name: str, authorized: str = ""):
    file = open(f"{HOME_DIR}/gpc-data/profiles.json", "r+")
    contents = json.load(file)

    if not authorized:
        authorized_profile = contents["authorized"]
        if not name == authorized_profile["name"]:
            contents["profiles"].append(name)
            profiles_list = list(dict.fromkeys(contents["profiles"]))
            contents["profiles"] = profiles_list
    else:
        if name in contents["profiles"]:
            contents["profiles"].remove(name)

        contents["authorized"]["name"] = name
        contents["authorized"]["token"] = authorized

    file.seek(0)
    file.write(json.dumps(contents))
    file.close()


def create_data_dir():
    if not os.path.exists(f"{HOME_DIR}/gpc-data/profiles.json"):
        os.mkdir(f"{HOME_DIR}/gpc-data")
        file = open(f"{HOME_DIR}/gpc-data/profiles.json", "w")
        json.dump({"profiles": [], "authorized": {"name": None, "token": None}}, file)
        file.close()
