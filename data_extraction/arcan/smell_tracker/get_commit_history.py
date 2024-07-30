import git
import os

# We keep the commit history of the units we already know, in case they appear multiple time in the data
# The key is (unit, first_commit_id, last_commit_id)
commits_histories_known: dict = {}


def get_commits_history_all_units(first_commit_id: str, last_commit_id: str, unit_list: list, repo_path: str):
    """
    Get the commit histories between two commits for all units in a list.
    :param last_commit_id:
    :param first_commit_id:
    :param unit_list:
    :param repo_path:
    :return: The commit histories list
    """
    commits: list = []

    if not repo_path.endswith(os.path.sep):
        repo_path += os.path.sep

    for unit in unit_list:

        if unit is not None:
            commits.append({
                "component": unit,
                "commit_history": get_commits_history_one_unit(unit, first_commit_id, last_commit_id, repo_path)
            })

    return commits


def get_commits_history_one_unit(unit: str, first_commit_id: str, last_commit_id: str, repo_path: str):
    """
    Get the commit history between two commits for one unit.
    :param last_commit_id:
    :param first_commit_id:
    :param unit:
    :param repo_path:
    :return: The commit history
    """
    commits_history: list = []

    if (unit, first_commit_id, last_commit_id) not in commits_histories_known:
        repo = git.Repo(repo_path)

        current_commit = repo.commit(last_commit_id)

        while current_commit.hexsha != first_commit_id:
            if unit.replace(repo_path, "").replace(os.path.sep, "/") in current_commit.stats.files:
                commits_history.append({
                    "commit_id": current_commit.hexsha,
                    "message": current_commit.message
                })

            if current_commit.parents:
                current_commit = current_commit.parents[0]
            else:
                break

        commits_histories_known[(unit, first_commit_id, last_commit_id)] = commits_history
    else:
        commits_history = commits_histories_known[(unit, first_commit_id, last_commit_id)]

    return commits_history
