import re

import requests
from main import get_authorized_profile


def analyze(repos):
    # GitHub repos without org repos or forks
    personal_repos = list(filter(lambda x: not x["fork"] and x["owner"]["type"] == "User", repos))
    similar = similar_repos_in_arr(personal_repos)
    print(similar)
    for repo in personal_repos:
        analyze_unit(repo)


def analyze_unit(repo):
    summary = {"repo_name": repo["name"]}
    # checking for readmes
    filenames = get_repo_filenames(repo)
    summary["readme_present"] = "readme.md" in filenames
    summary["empty"] = not bool(len(filenames))


def get_repo_filenames(repo):
    profile = get_authorized_profile()
    token = profile["token"]
    headers = {"Authorization": f"token {token}"} if token else {}
    username = repo["owner"]["login"]
    repo_name = repo["name"]
    files = requests.get(f"https://api.github.com/repos/{username}/{repo_name}/contents",
                         headers=headers).json()

    return [] if "message" in files else list(map(lambda file: file["name"].lower(), files))


def camel_case_split(identifier):
    return re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', identifier)).split()


def get_keywords_from_repo_name(repo_name):
    keywords = re.split("- |_ |-", repo_name)
    camel_case_separated = camel_case_split(repo_name)
    if len(camel_case_separated) > 1:
        keywords = [*keywords, *camel_case_separated]

    return keywords


def has_common_keywords(kw1, kw2) -> bool:
    return bool(set(kw1) & set(kw2))


def get_all_similar_repos(similar):
    arr = set()
    for obj in similar:
        for repo in obj["similar_repos"]:
            arr.add(repo)

    return arr


def similar_repos_in_arr(repos):
    similar_repos = []
    for repo in repos:
        if repo["name"] in get_all_similar_repos(similar_repos):
            continue

        similar_repos.append({"name": repo["name"], "similar_repos": []})
        target_repo_id = repo["id"]
        target_repo_keywords = get_keywords_from_repo_name(repo["name"])

        target_object = {}
        for obj in similar_repos:
            if obj["name"] == repo["name"]:
                target_object = obj

        for i in range(0, len(repos)):
            current_listed_repo = repos[i]
            listed_repo_id = current_listed_repo["id"]
            if not target_repo_id == listed_repo_id:
                listed_repo_keywords = get_keywords_from_repo_name(current_listed_repo["name"])
                share_keywords = has_common_keywords(target_repo_keywords, listed_repo_keywords)

                if share_keywords:
                    target_object["similar_repos"].append(current_listed_repo["name"])
                    for k in range(0, len(similar_repos)):
                        if similar_repos[k]["name"] == current_listed_repo["name"]:
                            similar_repos[k]["similar_repos"].append(current_listed_repo["name"])

        for l in range(0, len(similar_repos)):
            if similar_repos[l]["name"] == repo["name"]:
                if not len(similar_repos[l]["similar_repos"]):
                    del similar_repos[l]

    return similar_repos
