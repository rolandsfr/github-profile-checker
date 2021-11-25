import csv

from utils.data_structute_manip import find_index


def save_to_scv(merged_summary, profile_name):
    with open(f"data/summary_{profile_name}.csv", "w") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=",")

        # determine columns
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
                "Presence"
            ]}
        ]

        for summary_type in merged_summary.keys():
            target_index = find_index(lambda target_type: target_type["name"] == summary_type, head_columns)

            if summary_type == "with_orgs" and not len(merged_summary["with_orgs"]):
                continue

            if not summary_type == "profile":
                cols = list(map(lambda col: col["name"], head_columns[target_index]["columns"]))
                csv_writer.writerow(cols)

                for entry in merged_summary[summary_type]:
                    row = []
                    for summary_unit in head_columns[target_index]["columns"]:
                        value = entry[summary_unit["associated"]]

                        # Tweaking certain properties
                        if summary_unit["associated"] == "is_empty":
                            value = not value
                        elif summary_unit["associated"] == "naming":
                            if not value["camelcase"] and not value["other_unsupported"]:
                                value = True
                            else:
                                value = False

                        elif summary_unit["associated"] == "similar":
                            value = "None" if not len(value) else ", ".join(value)

                        row.append(value)

                    csv_writer.writerow(row)
            else:
                cols = head_columns[target_index]["columns"]
                csv_writer.writerow(cols)

                for profile_entry in merged_summary["profile"].keys():
                    row = [profile_entry, merged_summary["profile"][profile_entry]]
                    csv_writer.writerow(row)

            csv_writer.writerow([])
