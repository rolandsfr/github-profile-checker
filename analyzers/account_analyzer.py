def map_profile_vitals(profile, repos):
    has_personal_readme = profile["login"] in list(
        map(lambda repo: repo["name"], repos)
    )
    return {
        "blog": bool(profile["blog"]),
        "twitter": bool(profile["twitter_username"]),
        "bio": bool(profile["bio"]),
        "public_repos": bool(profile["public_repos"]),
        "readme": has_personal_readme,
    }
