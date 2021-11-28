# Standard libs
import json

# 3rd party libs
import polling
import requests
from polling import poll
from click import group, echo, argument, option

# Local modules
from src.analyzers.repos_analyzer import analyze_repos
from src.analyzers.account_analyzer import map_profile_vitals
from src.utils.fs_manip import (
    load_data,
    get_authorized_profile,
    get_saved_profiles,
    write_profile,
    create_data_dir,
)
from src.savers.csv_saver import save_to_scv
from src.savers.md_saver import save_to_md
from src.utils.constants import HOME_DIR

# GitHub OAuth application information
CLIENT_ID = "7579f4898d37ace4fe68"
SCOPES = ["repo", "read:user", "admin:org"]


def is_valid_profile(username):
    return (
        "message" not in requests.get(f"https://api.github.com/users/{username}").json()
    )


def generate_summary_for_unauthorized(name, csv: bool, verbose: bool):
    repos = requests.get(f"https://api.github.com/users/{name}/repos").json()
    if (
        not isinstance(repos, list)
        and "message" in repos.keys()
        and repos["documentation_url"]
        == "https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"
    ):
        raise ValueError(
            "You have been rate limited. Wait out an hour or use the `gpc analyze` "
            "for an authorized user "
        )

    echo(f"Analyzing GitHub profile for {name}")
    if verbose:
        echo("  - Starting to fetch...")

    repos_summary = analyze_repos(repos, verbose)

    if verbose:
        echo("\t - Checking for missing credentials")

    user_profile = requests.get(f"https://api.github.com/users/{name}").json()
    account_summary = map_profile_vitals(user_profile, repos)
    summary = {**repos_summary, "profile": account_summary}

    if verbose:
        extension = ".csv" if csv else ".md"
        file_name = f"summary_{name}{extension}"
        echo(f"  - Saving the summary to {HOME_DIR}/gpc-data/{file_name}")

    save = save_to_scv if csv else save_to_md
    save(summary, name)
    echo(f"Summary for the {name} profile has been generated!")


def poll_device(device_code, interval: int):
    request_url = (
        f"https://github.com/login/oauth/access_token?client_id={CLIENT_ID}&device_code={device_code}"
        f"&grant_type=urn:ietf:params:oauth:grant-type:device_code"
    )
    request_headers = {"Accept": "application/json"}

    def test_response(polling_response):
        return "access_token" in polling_response.json()

    return poll(
        lambda: requests.get(request_url, headers=request_headers),
        step=interval,
        timeout=9000,
        check_success=test_response,
    )


# Setting up the CLI itself
@group()
def cli():
    create_data_dir()


@cli.group()
def profile():
    """Offers manipulation with locally saved profiles"""
    pass


@profile.command()
@argument("username")
def add(username):
    """Locally saves the profile user is interested in"""
    if is_valid_profile(username):
        write_profile(username)
    else:
        echo(
            f"GitHub user with the {username} username is not found. Please, verify the username."
        )


@profile.command()
@argument("name", required=False)
@option(
    "--wipe", "--w", is_flag=True, help="Wipe out all the locally saved profile names."
)
def remove(name, wipe):
    # TODO: Create visual selection for this
    """Removes a profile from local 'saved' list"""
    profiles = get_saved_profiles()
    with open(f"{HOME_DIR}/gpc-data/profiles.json", "r+") as file:
        contents = json.load(file)
        if name and name in profiles and not wipe:
            contents["profiles"].remove(name)
        elif wipe:
            profiles_length = len(contents["profiles"])

            if not profiles_length:
                echo("There are no profiles to remove.")
            else:
                echo(f"{profiles_length} profiles have been removed.")
            contents["profiles"] = []

        else:
            echo("User is not saved locally, thus you cannot remove them.")
            return

        file.truncate(0)
        file.seek(0)
        file.write(json.dumps(contents))


@profile.command("listall")
def list_all():
    """List all currently saved GitHub profiles"""
    saved_profiles = get_saved_profiles()
    if not len(saved_profiles):
        echo("You currently have no saved profiles.")
        return

    echo("You have the following profiles saved:")
    for profile_name in saved_profiles:
        echo(f"  - {profile_name}")


@cli.command("login")
def authorize():
    """Authorize user through GitHub OAuth for deeper analysis."""
    scope = "%20".join(SCOPES)
    response = requests.post(
        f"https://github.com/login/device/code?client_id={CLIENT_ID}&scope={scope}",
        headers={"Accept": "application/json"},
    )

    user_code = response.json()["user_code"]
    device_code = response.json()["device_code"]
    interval = response.json()["interval"]

    echo(
        f"Please, open https://github.com/login/device and enter the code '{user_code}'"
    )

    try:
        authorized = poll_device(device_code, interval)
        access_token = authorized.json()["access_token"]
        user_data = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {access_token}"},
        ).json()
        username = user_data["login"]
        write_profile(username, access_token)

        echo(f"You have been successfully authorized as {username}")

    except AssertionError:
        echo("An error occurred during authorization. Please, try again.")
    except polling.TimeoutException:
        echo("Your device code has expired. Generate another one using `gpc login`.")


@cli.command()
@argument("name", required=False)
@option(
    "--fromlist",
    "--fl",
    is_flag=True,
    help="Generate summaries for all the locally saved profiles.",
)
@option("--csv", is_flag=True, help="Display the generated summary in a .csv file.")
def analyze(name, fromlist, csv):
    """Create a summary for the given profile(s)."""
    if not fromlist:
        saved_profiles = get_saved_profiles()

        if name:
            if name not in saved_profiles:
                write_profile(name)

            try:
                generate_summary_for_unauthorized(name, csv, True)
            except Exception as e:
                echo(str(e))

        else:
            authorized_profile = get_authorized_profile()
            if not authorized_profile["name"]:
                echo("Please, login first using `gpc login`")
                return

            token = authorized_profile["token"]
            name = authorized_profile["name"]

            repos = requests.get(
                "https://api.github.com/user/repos",
                headers={"Authorization": f"token {token}"},
            ).json()

            if (
                not isinstance(repos, list)
                and "message" in repos.keys()
                and repos["message"] == "Bad credentials"
            ):
                echo(
                    "Your access token is not valid. Please login again using `gpc login`"
                )
                return

            echo(f"Analyzing GitHub profile for {name}")
            echo("  - Starting to fetch...")

            repos_summary = analyze_repos(repos, True)

            echo("\t - Checking for missing credentials")
            user_profile = requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {token}"},
            ).json()
            account_summary = map_profile_vitals(user_profile, repos)
            summary = {**repos_summary, "profile": account_summary}

            extension = ".csv" if csv else ".md"
            file_name = f"summary_{name}{extension}"
            echo(f"  - Saving the summary to {HOME_DIR}/gpc-data/{file_name}")

            save = save_to_scv if csv else save_to_md
            save(summary, name)

            echo(f"Summary for the {name} profile has been generated!")
    else:
        data = load_data()
        all_profiles = data["profiles"]
        profiles_length = len(all_profiles)

        if not profiles_length:
            echo(
                "You do not have any profiles saved. Run 'gpc analyze', 'gpc analyze <profilename>' or 'gpc profile"
                "add <profilename> to use the --fromlist flag'"
            )
            return

        if profiles_length > 7:
            echo(
                f"Cannot analyze {profiles_length} profiles due to the GitHub api rate limits. Try again with less"
                f"profiles added."
            )
            return

        if profiles_length >= 5:
            echo(
                f"WARNING: {profiles_length * 3} requests to the github api were made. Keep in mind that the GitHub"
                f"api's rate limit for unauthorized users is 60 requests per hour."
            )

        for profile_name in all_profiles:
            try:
                generate_summary_for_unauthorized(profile_name, csv, False)
                print("")
            except Exception as e:
                echo(str(e))
                return
