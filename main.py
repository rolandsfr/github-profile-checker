import json
import os
from typing import  Union
import requests
from polling import poll

# GitHub OAuth application information
CLIENT_ID = "7579f4898d37ace4fe68"
SCOPES = ["repo", "read:user"]


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
            contents["profiles"].append(name)
            contents["profiles"] = list(dict.fromkeys(contents["profiles"]))
        else:
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

        print(f"Please, open https://github.com/login/device and enter the code '{user_code}'")

        try:
            authorized = self.__poll_device(device_code, interval)
            access_token = authorized.json()["access_token"]
            user_data = requests.get("https://api.github.com/user", headers={"Authorization": f"token {access_token}"}).json()
            username = user_data["login"]
            self.__write_profile(username, access_token)

            print(f"You have successfully authorized as {username}")
        except Exception:
            print("An error occurred during authorization. Please, try running the cli again.")

    def create_summary(self, data):
        pass

    def get(self, name: str):
        pass

    def clear(self):
        pass


def init_app():
    profiles = Profiles()
    profiles.set_authorized_user()


if __name__ == "__main__":
    init_app()

