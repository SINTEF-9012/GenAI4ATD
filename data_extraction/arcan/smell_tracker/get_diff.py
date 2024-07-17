import git
import common.file_management as file_management

# We keep the diffs of the units we already know, in case they appear multiple time in the data
# The key is (unit, first_commit_id, last_commit_id)
diffs_known: dict = {}


def get_diff_all_units(last_commit_id: str, first_commit_id: str, unit_list: list, repo_path: str,
                       language: str):
    diffs: list = []

    for unit in unit_list:
        d: dict = {
            "component": unit,
            "diff": get_diff_one_unit(last_commit_id, first_commit_id, unit, repo_path)
        }

        diffs.append(d)

    return diffs


def get_diff_one_unit(last_commit_id: str, first_commit_id: str, unit: str, repo_path: str):
    if (unit, first_commit_id, last_commit_id) not in diffs_known:
        repo = git.Repo(repo_path)

        # command = "cd "+repo_path+" && git diff "+old_version_id+" "+current_version_id+" "+file_full_path
        # return subprocess.run(command, capture_output=True, shell=True)

        return repo.git.diff(last_commit_id, first_commit_id, unit)
    else:
        return diffs_known[(unit, first_commit_id, last_commit_id)]
