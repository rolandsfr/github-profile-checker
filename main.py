# Standard libs
import json
import os
from typing import TypedDict

# 3rd party libs
import requests
from polling import poll

# Local modules
from lib import exceptions


# GitHub OAuth application information
CLIENT_ID = "7579f4898d37ace4fe68"
SCOPES = ["repo", "read:user"]


class ProfileResult(TypedDict):
    isAuthorized: bool
    reference: str


def get_profile(name):
    if not os.path.exists("./data/profiles.json"):
        raise FileNotFoundError("File does not exist!")

    file = open("data/profiles.json", "r")
    contents = json.load(file)
    authorized_user = contents["authorized"]
    result: ProfileResult = {
        "isAuthorized": False,
        "reference": ""
    }

    if name not in contents["profiles"] and name not in authorized_user:
        return None
    else:
        if name not in authorized_user:
            result['reference'] = name
        else:
            result['reference'] = authorized_user[list(authorized_user.keys())[0]]
            result['isAuthorized'] = True

    return result


class Summary:
    def __init__(self, name):
        pass


class DeepSummary(Summary):
    def __init__(self):
        pass

class Profiles:
    def __init__(self):
        self.collection = []

    def __poll_device(self, device_code, interval: int):
        request_url = f"https://github.com/login/oauth/access_token?client_id={CLIENT_ID}&device_code={device_code}&grant_type=urn:ietf:params:oauth:grant-type:device_code"
        request_headers = {"Accept": "application/json"}

        def test_response(polling_response):
            return "access_token" in polling_response.json()

        return poll(lambda: requests.get(request_url, headers=request_headers), step=interval, timeout=9000,
                    check_success=test_response)

    @staticmethod
    def __write_profile(name: str, authorized: str = ""):
        if not os.path.exists("./data/profiles.json"):
            os.mkdir("data")
            file = open("data/profiles.json", "w")
            json.dump({"profiles": [], "authorized": False}, file)
            file.close()

        file = open("data/profiles.json", "r+")
        contents = json.load(file)

        if not len(authorized):
            authorized_profile = contents["authorized"]
            if authorized_profile and name not in authorized_profile:
                contents["profiles"].append(name)
                profiles_list = list(dict.fromkeys(contents["profiles"]))
                contents["profiles"] = profiles_list

        else:
            if name in contents["profiles"]:
                contents["profiles"].remove(name)

            contents["authorized"] = {name: authorized}

        file.seek(0)
        file.write(json.dumps(contents))
        file.close()

    def set_authorized_user(self):
        scope = "%20".join(SCOPES)
        response = requests.post(f"https://github.com/login/device/code?client_id={CLIENT_ID}&scope={scope}",
                                 headers={"Accept": "application/json"})

        user_code = response.json()["user_code"]
        device_code = response.json()["device_code"]
        interval = response.json()["interval"]
        successful = False

        print(f"Please, open https://github.com/login/device and enter the code '{user_code}'")

        while not successful:
            try:
                authorized = self.__poll_device(device_code, interval)
                access_token = authorized.json()["access_token"]
                user_data = requests.get("https://api.github.com/user", headers={"Authorization": f"token {access_token}"}).json()
                username = user_data["login"]
                self.__write_profile(username, access_token)

                print(f"You have successfully authorized as {username}")
                successful = True
            except Exception:
                print("An error occurred during authorization. Try authorizing with the given code again.")

    def create_summary(self, data):
        pass

    def get(self, name: str):
        pass

    def clear(self):
        pass


def init_app():
    profiles = Profiles()
    # profiles.set_authorized_user()


if __name__ == "__main__":
    init_app()

