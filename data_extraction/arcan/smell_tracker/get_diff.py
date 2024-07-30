import git
from git import Repo

# We keep the diffs of the units we already know, in case they appear multiple time in the data
# The key is (unit, first_commit_id, last_commit_id)
diffs_known: dict = {}


def get_diff_all_units(last_commit_id: str, first_commit_id: str, unit_list: list, repo_path: str) -> list:
    """
    Get the diffs between two commits for all units in a list.
    :param last_commit_id:
    :param first_commit_id:
    :param unit_list:
    :param repo_path:
    :return: The diffs list
    """
    diffs: list = []
    repo = git.Repo(repo_path)

    for unit in unit_list:
        d: dict = {
            "component": unit,
            "diff": get_diff_one_unit(last_commit_id, first_commit_id, unit, repo)
        }

        diffs.append(d)

    return diffs


def get_diff_one_unit(last_commit_id: str, first_commit_id: str, unit: str, repo: Repo):
    """
    Get the diff between two commits for one unit.
    :param last_commit_id:
    :param first_commit_id:
    :param unit:
    :param repo_path:
    :param repo: Repo object
    :return: The diff
    """
    if (unit, first_commit_id, last_commit_id) not in diffs_known:
        # command = "cd "+repo_path+" && git diff "+old_version_id+" "+current_version_id+" "+file_full_path
        # return subprocess.run(command, capture_output=True, shell=True)

        return repo.git.diff(last_commit_id, first_commit_id, unit)
    else:
        return diffs_known[(unit, first_commit_id, last_commit_id)]
