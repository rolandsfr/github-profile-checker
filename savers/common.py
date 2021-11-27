common_fields = [
    {"name": "Repository name", "associated": "repo_name"},
    {"name": "Readme", "associated": "readme_present"},
    {"name": "License", "associated": "license"},
    {"name": "Description", "associated": "description"},
    {"name": "Homepage", "associated": "homepage"},
    {"name": "Non-empty repository", "associated": "is_empty"},
    {"name": "Standard naming convention", "associated": "naming"},
    {"name": "Similar repositories", "associated": "similar"}
]

head_columns = [
    {"name": "plain", "columns": common_fields},
    {"name": "with_orgs", "columns": [*common_fields, {"name": "Organization", "associated": "organization"}]},
    {"name": "profile", "columns": [
        "Criteria",
        "Present"
    ]}
]