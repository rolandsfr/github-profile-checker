# standard libs
import re
from time import sleep

# 3rd party lbs
import requests

# local modules
from utils.fs_manip import get_authorized_profile
from utils.data_structute_manip import find_index


def analyze_repos(repos, verbose):
    # handle repos that are not part of any organizations
    org_repos = list(
        filter(lambda x: not x["fork"] and x["owner"]["type"] == "Organization", repos)
    )
    org_repo_names = list(map(lambda repo: repo["name"], org_repos))

    # GitHub repos without org repos or forks
    personal_repos = list(
        filter(
            lambda x: not x["fork"]
            and x["owner"]["type"] == "User"
            and x["name"] not in org_repo_names,
            repos,
        )
    )

    similar = similar_repos_in_arr(personal_repos)
    plain_summaries = []

    for index, repo_entry in enumerate(personal_repos):
        summary = analyze_unit(repo_entry)
        target_similarity = find_index(
            lambda target_repo: target_repo["name"] == repo_entry["name"], similar
        )

        if target_similarity:
            summary["similar"] = (
                similar[target_similarity]["similar_repos"] if len(similar) else []
            )
        else:
            summary["similar"] = []

        if verbose:
            repo_count = len(personal_repos)
            end = "\n" if index == repo_count - 1 else "\r"
            print(
                f"\t - Analyzed {index + 1}/{repo_count} personal repositories", end=end
            )

        plain_summaries.append(summary)

    # handle repos that are part of an organization
    org_repos_summaries: [] = analyze_from_orgs(org_repos, verbose)

    return {"plain": plain_summaries, "with_orgs": org_repos_summaries}


def analyze_from_orgs(org_repos, verbose):
    orgs = []
    summaries = []

    for i in range(0, len(org_repos)):
        org_repo_names = []

        for j in range(0, len(orgs)):
            org_repo_names.append(orgs[j]["name"])

        if org_repos[i]["owner"]["login"] not in org_repo_names:
            orgs.append({"name": org_repos[i]["owner"]["login"], "repos": []})

        for j in range(0, len(orgs)):
            if (
                org_repos[i]["name"] not in orgs[j]["repos"]
                and org_repos[i]["owner"]["login"] == orgs[j]["name"]
            ):
                orgs[j]["repos"].append({"name": org_repos[i]["name"], "id": i})

        if verbose:
            repo_count = len(org_repos)
            end = "\n" if i == repo_count - 1 else "\r"
            sleep(0.3)
            print(
                f"\t - Analyzed {i + 1}/{repo_count} organization repositories", end=end
            )

    for org in orgs:
        similar = similar_repos_in_arr(org["repos"])
        org_name = org["name"]

        for repo in org["repos"]:
            repo = org_repos[find_index(lambda x: x["name"] == repo["name"], org_repos)]
            summary = analyze_unit(repo, org_name)
            target_similarity = find_index(
                lambda target_repo: target_repo["name"] == repo["name"], similar
            )
            summary["similar"] = (
                similar[target_similarity]["similar_repos"] if len(similar) else []
            )
            summaries.append(summary)

    return summaries


def camel_case_split(identifier):
    return re.sub(
        "([A-Z][a-z]+)", r" \1", re.sub("([A-Z]+)", r" \1", identifier)
    ).split()


def analyze_unit(repo, org=None):
    summary = {"repo_name": repo["name"]}
    # checking for readmes
    filenames = get_repo_filenames(repo)
    summary["readme_present"] = "readme.md" in filenames

    # other trivial stuff
    summary["license"] = bool(repo["license"])
    summary["description"] = bool(repo["description"])
    summary["homepage"] = bool(repo["homepage"])
    summary["is_empty"] = not bool(len(filenames))
    if org:
        summary["organization"] = org

    # checking for repo naming convention
    camel_case_detected = len(camel_case_split(repo["name"])) > 1
    other_symbols_detected = len(re.split("_| ", repo["name"])) > 1

    summary["naming"] = {
        "camelcase": camel_case_detected,
        "other_unsupported": other_symbols_detected,
    }

    return summary


def get_repo_filenames(repo):
    profile = get_authorized_profile()
    token = profile["token"]
    headers = {"Authorization": f"token {token}"} if token else {}
    username = repo["owner"]["login"]
    repo_name = repo["name"]
    files = requests.get(
        f"https://api.github.com/repos/{username}/{repo_name}/contents", headers=headers
    ).json()

    return (
        []
        if "message" in files
        else list(map(lambda file: file["name"].lower(), files))
    )


def get_keywords_from_repo_name(repo_name):
    keywords = re.split("-|_ | ", repo_name)
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

    return list(arr)


def similar_repos_in_arr(repos):
    if len(repos) < 2:
        return []

    similar_repos = []
    for repo in repos:
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
                listed_repo_keywords = get_keywords_from_repo_name(
                    current_listed_repo["name"]
                )
                share_keywords = has_common_keywords(
                    target_repo_keywords, listed_repo_keywords
                )

                if share_keywords:
                    target_object["similar_repos"].append(current_listed_repo["name"])
                    for k in range(0, len(similar_repos)):
                        if similar_repos[k]["name"] == current_listed_repo["name"]:
                            similar_repos[k]["similar_repos"] = list(
                                set(similar_repos[k]["similar_repos"])
                            )

        for l in range(0, len(similar_repos)):
            if similar_repos[l]["name"] == repo["name"]:
                if not len(similar_repos[l]["similar_repos"]):
                    del similar_repos[l]

    return similar_repos
