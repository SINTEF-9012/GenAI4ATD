import math
import pandas as pd
import json
import common.utils as utils
import common.file_management as file_management
import data_extraction.arcan.smell_tracker.get_commit_history as get_commit_history
import data_extraction.arcan.smell_tracker.generate_examples as generate_examples
import data_extraction.arcan.smell_tracker.get_diff as get_diff


def main(input_path: str, output_path: str, repo_path: str, language: str, atdi_var_diff: bool = False,
         atdi_var_commit_history: bool = False, only_last_ver=False, number_of_ver=1000, example=False):
    smell_characteristics_keep: list = ["vertexId", "ATDI", "Severity", "Size", "LOCDensity", "NumberOfEdge"]

    smell_characteristics = pd.read_csv(input_path + "smell-characteristics.csv", sep=',')

    smells_by_version: dict = track_smells(smell_characteristics, smell_characteristics_keep, repo_path, language,
                                           number_of_ver, atdi_var_diff, atdi_var_commit_history)

    smell_list: list = write_smells_list(smells_by_version)

    # if only_last_ver:
    #    smells_tracker = keep_only_last_ver(smell_characteristics, smells_tracker)

    if example:
        example_smell: list = generate_examples.generate_examples(smell_list)

        example_file = open(output_path + "_example.json", "w")
        example_file.write(json.dumps(example_smell))

    file = open(output_path + ".json", "w")
    file.write(json.dumps(smell_list))


def track_smells(smell_characteristics, smell_characteristics_keep, repo_path: str, language: str, number_of_ver: int,
                 atdi_var_diff: bool, atdi_var_commit_history: bool):
    versions_analysed = 0

    previous_version_id: str = ""
    previous_smell_version_id: str = smell_characteristics.iloc[0]["versionId"]  # different from previous_version_id
    first_version_id: str = smell_characteristics.iloc[0]["versionId"]

    smell_is_known: bool = False

    smells_by_version: dict = {first_version_id: {}}  # a smell will always be moved into the smell version it appeared
    # or the version in which it disappeared

    for index, row in smell_characteristics.iterrows():
        if row["versionId"] != previous_smell_version_id:
            versions_analysed += 1
            previous_version_id = previous_smell_version_id

            smells_by_version = check_for_smells_that_disappeared(smells_by_version, previous_version_id,
                                                                  repo_path, language, atdi_var_diff,
                                                                  atdi_var_commit_history)

            if versions_analysed == number_of_ver:
                break

            smells_by_version[row["versionId"]] = {}

        if len(smells_by_version) != 0:
            for version in smells_by_version:
                # check is the smell is already in the dict
                if (row["smellType"], row["AffectedElements"]) in smells_by_version[version]:
                    smell_data: dict = smells_by_version[version].pop((row["smellType"], row["AffectedElements"]))

                    smell_data["characteristics_by_version"].append(
                        {
                            "versionId": row["versionId"],
                            "characteristics": write_characteristics(row, smell_characteristics_keep),
                            "ATDI_var": check_atd_variation(row["ATDI"],
                                                            smell_data["characteristics_by_version"][-1]
                                                            ["characteristics"]["ATDI"], row["versionId"],
                                                            smell_data["characteristics_by_version"][-1]["versionId"],
                                                            row["AffectedElements"], repo_path, language,
                                                            row["AffectedComponentType"], atdi_var_diff,
                                                            atdi_var_commit_history)
                        }
                    )

                    smells_by_version[row["versionId"]][(row["smellType"], row["AffectedElements"])] = smell_data

                    smell_is_known = True

                    break

        if len(smells_by_version) == 0 or not smell_is_known:
            smell_data: dict = {
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

            if row["versionId"] != first_version_id:  # this mean this is a new smell
                smell_data["characteristics_by_version"][-1]["ATDI_var"] = (
                    check_atd_variation(row["ATDI"], 0, row["versionId"], previous_version_id, row["AffectedElements"],
                                        repo_path, language, row["AffectedComponentType"], atdi_var_diff,
                                        atdi_var_commit_history))

            smells_by_version[row["versionId"]][(row["smellType"], row["AffectedElements"])] = smell_data

        previous_smell_version_id = row["versionId"]

        smell_is_known = False

        print(row["vertexId"])

    return smells_by_version


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


def check_atd_variation(current_atdi: float, old_atdi: float, current_version_id: str, old_version_id: str,
                        components_affected: str, repo_path: str, language: str, component_type: str, diff: bool,
                        commit_history: bool):
    atdi_var: dict = {}

    if math.isclose(current_atdi, old_atdi):
        atdi_var["variation"] = "SAME"
    else:
        if old_atdi == 0:
            atdi_var["variation"] = "NEW"
        elif current_atdi == 0:
            atdi_var["variation"] = "DISAPPEARED"
        elif current_atdi < old_atdi:
            atdi_var["variation"] = "DOWN"
        elif current_atdi > old_atdi:
            atdi_var["variation"] = "UP"

        if diff or commit_history:
            if component_type == "CONTAINER":
                # atdi_var["diffs"] = "No diff for containers"
                # atdi_var["commit_history"] = "No commit history for containers"
                unit_list: list = file_management.get_unit_list_from_container_list(components_affected,
                                                                                    repo_path, language)
            else:
                unit_list: list = file_management.get_components_as_paths_list(components_affected, repo_path, language,
                                                                               True)

            if diff:
                atdi_var["diffs"] = get_diff.get_diff_all_units(current_version_id, old_version_id, unit_list,
                                                                repo_path, language)

            if commit_history:
                atdi_var["commit_history"] = get_commit_history.get_commits_history_all_units(old_version_id,
                                                                                              current_version_id,
                                                                                              unit_list,
                                                                                              repo_path)

    return atdi_var


def check_for_smells_that_disappeared(smells_by_version: dict, last_version: str, repo_path: str, language: str,
                                      atdi_var_diff: bool, atdi_var_commit_history: bool):
    for version in smells_by_version:
        for smell_data in smells_by_version[version].values():
            if (smell_data not in smells_by_version[last_version].values()
                    and smell_data["ATDI_var"]["variation"] != "DISAPPEARED"):
                smell_data["characteristics_by_version"].append(
                    {
                        "versionId": last_version,
                        "characteristics": {"ATDI": 0},
                        "ATDI_var": check_atd_variation(0,
                                                        smell_data["characteristics_by_version"][-1]
                                                        ["characteristics"]["ATDI"], last_version,
                                                        smell_data["characteristics_by_version"][-1]["versionId"],
                                                        smell_data["components_affected"], repo_path, language,
                                                        smell_data["type_components_affected"], atdi_var_diff,
                                                        atdi_var_commit_history)
                    }
                )

    return smells_by_version


def write_smells_list(smells_by_version: dict):
    smells_list: list = []

    for version in smells_by_version:
        smells_list.extend(smells_by_version[version].values())

    return smells_list
