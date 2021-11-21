# Standard libs
import json
import os
from typing import TypedDict
from click import group, echo, argument

# 3rd party libs
import requests
from polling import poll

# Local modules
from lib import exceptions


# GitHub OAuth application information
CLIENT_ID = "7579f4898d37ace4fe68"
SCOPES = ["repo", "read:user"]


def write_profile(name: str, authorized: str = ""):
    if not os.path.exists("./data/profiles.json"):
        os.mkdir("data")
        file = open("data/profiles.json", "w")
        json.dump({"profiles": [], "authorized": {"name": None, "token": None}}, file)
        file.close()

    file = open("data/profiles.json", "r+")
    contents = json.load(file)

    if not authorized:
        authorized_profile = contents["authorized"]
        if authorized_profile["name"] and not name == authorized_profile["name"]:
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


@group()
def cli():
    pass


@cli.group()
def profile():
    pass


@profile.command()
@argument("GitHub username")
def add(name):
    """Locally saves the profile user is interested in"""
    write_profile(name)


class ProfileResult(TypedDict):
    isAuthorized: bool
    reference: str


def load_data():
    if not os.path.exists("./data/profiles.json"):
        raise FileNotFoundError("File does not exist!")

    file = open("data/profiles.json", "r")
    return json.load(file)


def get_authorized_profile():
    contents = load_data()
    return contents["authorized"]


def get_saved_profiles(name):
    contents = load_data()
    return contents["profiles"]


class Repositories:
    def __init__(self, username):
        self.username = username

    def fetch_repos(self, headers):
        username = self.username
        repositories = requests.get(f"https://api.github.com/users/{username}/repos", headers=headers).json()
        # print(repositories)


class Summary:
    def __init__(self, profile: ProfileResult):
        self.profile = profile

    def generate(self):
        profile = self.profile
        repositories = Repositories("rolandsfr")
        headers = {"Authorization": "token " + profile['reference']} if profile['isAuthorized'] else {}
        # print(headers)
        repositories.fetch_repos(headers)


def clear():
    with open("data/profiles.json", "w+") as file:
        contents = json.load(file)
        contents["profiles"] = []
        json.dump(contents, file)


def poll_device(device_code, interval: int):
    request_url = f"https://github.com/login/oauth/access_token?client_id={CLIENT_ID}&device_code={device_code}" \
                  f"&grant_type=urn:ietf:params:oauth:grant-type:device_code"
    request_headers = {"Accept": "application/json"}

    def test_response(polling_response):
        return "access_token" in polling_response.json()

    return poll(lambda: requests.get(request_url, headers=request_headers), step=interval, timeout=9000,
                check_success=test_response)


@cli.command("login")
def authorize():
    """Authorizes user through GitHub OAuth for more deep profile analysis"""
    scope = "%20".join(SCOPES)
    response = requests.post(f"https://github.com/login/device/code?client_id={CLIENT_ID}&scope={scope}",
                             headers={"Accept": "application/json"})

    user_code = response.json()["user_code"]
    device_code = response.json()["device_code"]
    interval = response.json()["interval"]

    echo(f"Please, open https://github.com/login/device and enter the code '{user_code}'")

    try:
        authorized = poll_device(device_code, interval)
        access_token = authorized.json()["access_token"]
        user_data = requests.get("https://api.github.com/user",
                                 headers={"Authorization": f"token {access_token}"}).json()
        username = user_data["login"]
        write_profile(username, access_token)

        echo(f"You have been successfully authorized as {username}")

    except AssertionError:
        echo("An error occurred during authorization. Please, try again.")


if __name__ == "__main__":
    cli()
