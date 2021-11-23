import re

import requests
from main import get_authorized_profile


def analyze(repos):
    # GitHub repos without org repos or forks
    personal_repos = list(filter(lambda x: not x["fork"] and x["owner"]["type"] == "User", repos))
    org_repos = list(filter(lambda x: not x["fork"] and x["owner"]["type"] == "Organization", repos))

    similar = similar_repos_in_arr(personal_repos)
    print(similar)
    for repo in personal_repos:
        summary = analyze_unit(repo)
        print(summary)

    analyze_from_orgs(org_repos)


def find_index(criteria, arr):
    for i in range(0, len(arr)):
        if criteria(arr[i]):
            return i

    return None


def analyze_from_orgs(org_repos):
    orgs = []

    for i in range(0, len(org_repos)):
        org_repo_names = []

        for j in range(0, len(orgs)):
            org_repo_names.append(orgs[j]["name"])

        if org_repos[i]["owner"]["login"] not in org_repo_names:
            orgs.append({"name": org_repos[i]["owner"]["login"], "repos": []})

        for j in range(0, len(orgs)):
            if org_repos[i]["name"] not in orgs[j]["repos"] and org_repos[i]["owner"]["login"] == orgs[j]["name"]:
                orgs[j]["repos"].append({"name": org_repos[i]["name"], "id": i})

    for org in orgs:
        similar = similar_repos_in_arr(org["repos"])

        for repo in org["repos"]:
            repo = org_repos[find_index(lambda x: x["name"] == repo["name"], org_repos)]
            print(analyze_unit(repo))


def camel_case_split(identifier):
    return re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', identifier)).split()


def analyze_unit(repo):
    summary = {"repo_name": repo["name"]}
    # checking for readmes
    filenames = get_repo_filenames(repo)
    summary["readme_present"] = "readme.md" in filenames

    # other trivial stuff
    summary["license"] = bool(repo["license"])
    summary["description"] = bool(repo["description"])
    summary["homepage"] = bool(repo["homepage"])
    summary["empty"] = not bool(len(filenames))

    # checking for repo naming convention
    camel_case_detected = len(camel_case_split(repo["name"])) > 1
    other_symbols_detected = len(re.split("_| | ", repo["name"])) > 1

    summary["naming"] = {
        "camelcase": camel_case_detected,
        "other": other_symbols_detected
    }

    return summary


def get_repo_filenames(repo):
    profile = get_authorized_profile()
    token = profile["token"]
    headers = {"Authorization": f"token {token}"} if token else {}
    username = repo["owner"]["login"]
    repo_name = repo["name"]
    files = requests.get(f"https://api.github.com/repos/{username}/{repo_name}/contents",
                         headers=headers).json()

    return [] if "message" in files else list(map(lambda file: file["name"].lower(), files))


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
    if len(repos) < 2:
        return []

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
