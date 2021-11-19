import os
from typing import TypedDict, Union
import requests
from polling import poll

# GitHub OAuth application information
CLIENT_ID = "7579f4898d37ace4fe68"
SCOPES = ["repo", "read:user"]


class Credentials(TypedDict):
    username: str
    password: str


class AuthorizedUser:
    def __init__(self):
        self.authorize(self)

    @staticmethod
    def _cache_user(self) -> Union[None, bool]:
        try:
            os.mkdir("./_cache")
            file = open("data.json", "w")

        except FileExistsError:
            return False

    def __poll_device(self, device_code, interval: int):
        request_url = f"https://github.com/login/oauth/access_token?client_id={CLIENT_ID}&device_code={device_code}&grant_type=urn:ietf:params:oauth:grant-type:device_code"
        request_headers = {"Accept": "application/json"}

        res = poll(lambda: "access_token" in requests.post(request_url, headers=request_headers).json(),
                    step=interval, timeout=9000)

        if(res):
            print(requests.post(request_url, headers=request_headers).json())
            return requests.post(request_url, headers=request_headers).json()["access_token"]

    @staticmethod
    def authorize(self):
        scope = "%20".join(SCOPES)
        response = requests.post(f"https://github.com/login/device/code?client_id={CLIENT_ID}&scope={scope}",
        headers={"Accept": "application/json"})

        user_code = response.json()["user_code"]
        device_code = response.json()["device_code"]
        interval = response.json()["interval"]

        print(f"Please, open https://github.com/login/device and enter the code '{user_code}'")

        authorized = self.__poll_device(device_code, interval)
        if authorized:
            print(authorized)

def init_app():
    print('Welcome to the GitHub profile checker!\n')
    user = AuthorizedUser()


init_app()
