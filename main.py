# Standard libs
import json
import os
from typing import TypedDict
from click import group, echo, argument, option

# 3rd party libs
import requests
from polling import poll

# Local modules
from lib import reposAnalyzer

# GitHub OAuth application information
CLIENT_ID = "7579f4898d37ace4fe68"
SCOPES = ["repo", "read:user", "admin:org"]


def create_data_dir():
    if not os.path.exists("./data/profiles.json"):
        os.mkdir("data")
        file = open("data/profiles.json", "w")
        json.dump({"profiles": [], "authorized": {"name": None, "token": None}}, file)
        file.close()


def is_valid_profile(username):
    return "message" not in requests.get(f"https://api.github.com/users/{username}").json()


def write_profile(name: str, authorized: str = ""):
    file = open("data/profiles.json", "r+")
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


@group()
def cli():
    pass


@cli.group()
def profile():
    pass


@profile.command()
@argument("username")
def add(username):
    """Locally saves the profile user is interested in"""
    if is_valid_profile(username):
        write_profile(username)
    else:
        echo(f"GitHub user with the {username} username is not found. Please, verify the username.")


@profile.command()
@argument("name", required=False)
@option("--wipe", "--w", is_flag=True)
def remove(name, wipe):
    # TODO: Create visual selection for this
    """Removes a profile from saved list. If the -w flag is present, wipes out the whole list of saved profiles."""
    profiles = get_saved_profiles()
    with open("./data/profiles.json", "r+") as file:
        contents = json.load(file)
        if name and name in profiles and not wipe:
            contents["profiles"].remove(name)
        elif wipe:
            contents["profiles"] = []
        else:
            raise ValueError("User does is not locally saved, thus you cannot remove it")

        file.truncate(0)
        file.seek(0)
        file.write(json.dumps(contents))



def load_data():
    if not os.path.exists("./data/profiles.json"):
        raise FileNotFoundError("File does not exist!")

    with open("data/profiles.json", "r") as file:
        return json.load(file)


def get_authorized_profile():
    contents = load_data()
    return contents["authorized"]


def get_saved_profiles():
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
    def __init__(self, profile):
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

    print(response.json())
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


@cli.command()
@argument("name", required=False)
@option("--fromlist", "--fl", is_flag=True)
def analyze(name, fromlist):
    if not fromlist:
        if name in get_saved_profiles():
            repos = requests.get(f"https://api.github.com/users/{name}/repos").json()
            reposAnalyzer.analyze(repos)
        else:
            token = get_authorized_profile()["token"]
            repos = requests.get("https://api.github.com/user/repos", headers={"Authorization": f"token {token}"}).json()
            reposAnalyzer.analyze(repos)

    else:

        pass


if __name__ == "__main__":
    create_data_dir()
    cli()
