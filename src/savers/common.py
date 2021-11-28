common_fields = [
    {"name": "Repository name", "associated": "repo_name"},
    {"name": "Readme", "associated": "readme_present"},
    {"name": "License", "associated": "license"},
    {"name": "Description", "associated": "description"},
    {"name": "Homepage", "associated": "homepage"},
    {"name": "Non-empty repository", "associated": "is_empty"},
    {"name": "Standard naming convention", "associated": "naming"},
    {"name": "Similar repositories", "associated": "similar"},
]

head_columns = [
    {"name": "plain", "columns": common_fields},
    {
        "name": "with_orgs",
        "columns": [
            *common_fields,
            {"name": "Organization", "associated": "organization"},
        ],
    },
    {"name": "profile", "columns": ["Criteria", "Present"]},
]


def get_suggestion(suggestion_type, amount):
    descriptions = {
        "readme_present": f" - {amount} repositories are missing a readme file. Make sure to add one in order to let "
        f"others know what the repository is about.",
        "license": f" - {amount} repositories are not licensed. Make sure to add your licences to protect your work.",
        "description": f" - {amount} repositories lack description. Add a brief description to your projects for a "
        f"better SEO.",
        "homepage": f" - {amount} repositories do not have an associated homepage. In case you have one and forgot to"
        f" add it, please do so.",
        "similar": f" - There are {amount} repositories to have been marked as similar. If they serve a"
        f" similar purpose, try inserting them into one 'general-purpose' repository with it's directories"
        f" corresponding to original similar repositories. Or as an alternative, group them using "
        f" organizations.",
        "is_empty": f" - There are {amount} empty repositories. Make sure to delete them if you no longer have a use"
        f" for them.",
        "naming": f" - {amount} repositories do not follow the preferable naming convention where every keyword is"
        f" separated with '-'. Avoid using camelCase or space to separate keywords.",
    }

    return descriptions[suggestion_type]
