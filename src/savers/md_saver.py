# Standard libs
import io

# 3rd party libs
from pytablewriter import MarkdownTableWriter

# Local modules
from src.utils.constants import HOME_DIR
from src.utils.data_structute_manip import find_index
from src.savers.common import head_columns, get_suggestion


def save_to_md(merged_summary, profile_name):
    with open(f"{HOME_DIR}/gpc-data/summary_{profile_name}.md", "w") as file:
        issues = {}

        for summary_type in merged_summary.keys():
            value_matrix = []
            if not len(merged_summary[summary_type]):
                continue
            if summary_type == "plain":
                file.write("## Regular repositories\n")
                file.write(
                    "<p>All your personal repositories (non-forked <b>and</b> not a part"
                    " of any organization)</p>\n\n"
                )
            elif summary_type == "with_orgs":
                file.write("## Organization repositories\n")
                file.write(
                    "<p>All the repositories that are part of your organizations</p>\n\n"
                )
            elif summary_type == "profile":
                file.write("## Profile analysis\n")
                file.write(
                    "<p>Important pieces that might be missing in your public developer GitHub profile</p>\n\n"
                )

            target_index = find_index(
                lambda target_type: summary_type == target_type["name"], head_columns
            )

            if summary_type != "profile":
                headers = list(
                    map(lambda col: col["name"], head_columns[target_index]["columns"])
                )

                for entry in merged_summary[summary_type]:
                    values_row = []
                    for criteria in head_columns[target_index]["columns"]:
                        unit = criteria["associated"]
                        value = entry[unit]

                        if unit == "is_empty":
                            value = not value

                        elif unit == "naming":
                            value = (
                                not value["camelcase"]
                                and not value["other_unsupported"]
                            )

                        if type(value) is bool and not unit == "organization":
                            if not value:
                                if unit in issues.keys():
                                    issues[unit] += 1
                                else:
                                    issues[unit] = 1

                            value = "Yes" if value else "<mark>No</mark>"

                        elif isinstance(value, list):
                            if len(value):
                                if unit in issues.keys():
                                    issues[unit] += 1
                                else:
                                    issues[unit] = 1

                        if unit == "similar":
                            value = (
                                "<mark>" + ", ".join(value) + "</mark>"
                                if len(value)
                                else str(None)
                            )

                        values_row.append(value)

                    value_matrix.append(values_row)
            else:
                headers = head_columns[target_index]["columns"]
                for entry in merged_summary[summary_type].keys():
                    value_matrix.append(
                        [
                            entry.replace("_", " "),
                            "Yes"
                            if merged_summary[summary_type][entry]
                            else "<mark>No</mark>",
                        ]
                    )

            writer = MarkdownTableWriter(
                headers=headers,
                value_matrix=value_matrix,
            )
            writer.stream = io.StringIO()
            writer.write_table()
            writer.stream = file
            writer.write_table()

        if not len(list(issues.keys())):
            return

        # Offering suggestions
        file.write("## Suggestions\n")
        file.write(
            "### Here are the issues that have been detected in the profile and how to fix them.\n\n"
        )

        # Covering every issue in detail
        for issue in issues.keys():
            file.write(get_suggestion(issue, issues[issue]) + "\n\n")
