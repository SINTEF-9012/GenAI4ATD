import math
import pandas as pd
import json
import common.utils as utils
import data_extraction.arcan.smell_tracker.get_diff as get_diff
import data_extraction.arcan.smell_tracker.get_commit_history as get_commit_history
import data_extraction.arcan.smell_tracker.generate_examples as generate_examples


def main(input_path: str, output_path: str, repo_path: str, language: str, only_last_ver=False, number_of_ver=1000,
         example=False):
    smell_characteristics_keep: list = ["vertexId", "ATDI", "Severity", "Size", "LOCDensity", "NumberOfEdge"]

    smell_characteristics = pd.read_csv(input_path + "smell-characteristics.csv", sep=',')

    smells_tracker: list = track_smells(smell_characteristics, smell_characteristics_keep, repo_path, language,
                                        number_of_ver)

    # if only_last_ver:
    #    smells_tracker = keep_only_last_ver(smell_characteristics, smells_tracker)

    if example:
        example_smell: list = generate_examples.generate_examples(smells_tracker)

        example_file = open(output_path + "_example.json", "w")
        example_file.write(json.dumps(example_smell))

    file = open(output_path + ".json", "w")
    file.write(json.dumps(smells_tracker))


def track_smells(smell_characteristics, smell_characteristics_keep, repo_path: str, language: str, number_of_ver: int):
    smells_tracker: list = []

    versions_analysed = 0

    old_version_id: str = ""

    for index, row in smell_characteristics.iterrows():
        if len(smells_tracker) != 0:
            for smell in smells_tracker:
                # check is the smell is already in the dict
                if row["smellType"] == smell["type"] and row["AffectedElements"] == smell["components_affected"]:
                    smell["characteristics_by_version"].append(
                        {
                            "versionId": row["versionId"],
                            "characteristics": write_characteristics(row, smell_characteristics_keep),
                            "ATDI_var": check_atdi_variation(row["ATDI"],
                                                             smell["characteristics_by_version"][-1]["characteristics"][
                                                                 "ATDI"],
                                                             row["versionId"],
                                                             smell["characteristics_by_version"][-1]["versionId"],
                                                             row["AffectedElements"], repo_path, language,
                                                             row["AffectedComponentType"])
                        }
                    )

                    break

        smells_tracker.append(
            {
                "type": row["smellType"],
                "components_affected": row["AffectedElements"],
                "type_components_affected": row["AffectedComponentType"],
                "characteristics_by_version": [
                    {
                        "versionId": row["versionId"],
                        "characteristics": write_characteristics(row, smell_characteristics_keep)
                    }
                ]
            }
        )

        if row["versionId"] != old_version_id:
            versions_analysed += 1

        old_version_id = row["versionId"]

        print(row["vertexId"])

        if versions_analysed == number_of_ver:
            break

    return smells_tracker


def keep_only_last_ver(smell_characteristics, smell_tracker: list):
    last_ver = smell_characteristics.tail(1)["versionId"].iat[0]
    smell_tracker_last_ver = []

    for s in smell_tracker:
        for c in s["characteristics_by_version"]:
            if c["versionId"] == last_ver:
                smell_tracker_last_ver.append(s)

    return smell_tracker_last_ver


def write_characteristics(row, smell_characteristics_keep):
    smell_characteristics: dict = {}

    for column in row.keys():
        if column in smell_characteristics_keep:
            smell_characteristics[utils.format_column_name(column)] = row[column]

    return smell_characteristics


def check_atdi_variation(current_atdi: float, old_atdi: float, current_version_id: str, old_version_id: str,
                         components_affected: str, repo_path: str, language: str, component_type: str):
    atdi_var: dict = {}

    if math.isclose(current_atdi, old_atdi):
        atdi_var["variation"] = "SAME"
    else:
        if current_atdi < old_atdi:
            atdi_var["variation"] = "DOWN"
        elif current_atdi > old_atdi:
            atdi_var["variation"] = "UP"

        if component_type == "CONTAINER":
            atdi_var["diffs"] = "No diff for containers"
            atdi_var["commit_history"] = "No commit history for containers"
        else:
            atdi_var["diffs"] = get_diff.get_diff_all_components(current_version_id, old_version_id,
                                                                 components_affected,
                                                                 repo_path, language)
            atdi_var["commit_history"] = get_commit_history.get_commits_history_all_component(old_version_id, current_version_id,
                                                                           components_affected, repo_path, language)

    return atdi_var
