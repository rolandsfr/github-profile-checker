import os
from typing import TypedDict, Union
import secrets
from lib import routes
from threading import Thread

# GitHub OAuth application information
CLIENT_ID = "25b12301715160d278b8"
SCOPES = ["repo", "read:user"]


class Credentials(TypedDict):
    username: str
    password: str


class User:
    def __init__(self):
        self.authorize()

    @staticmethod
    def _cache_user(self) -> Union[None, bool]:
        try:
            os.mkdir("./_cache")
            file = open("data.json", "w")

        except FileExistsError:
            return False

    @staticmethod
    def authorize():
        kwargs = {'host': '127.0.0.1', 'port': 8000, 'threaded': True, 'use_reloader': False, 'debug': False}
        flask_thread = Thread(target=routes.app.run, daemon=True, kwargs=kwargs).start()

        scope = "%20".join(SCOPES)
        redirect_uri = "http://localhost:8000/cb"
        state = secrets.token_hex(16)
        auth_link = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope={scope}\
        &state={state}&redirect_uri={redirect_uri}&allow_signup=false"
        print(f"Please, log into your github account using {auth_link} link")


    def get_props(self):
        pass


def init_app():
    print('Welcome to the GitHub profile checker!\n')
    user = User()


init_app()
