import git
import os

from git import Repo

from data_extraction.arcan.smell_tracker import CommitFilter

# We keep the commit history of the units we already know, in case they appear multiple time in the data
# The key is (unit, first_commit_id, last_commit_id)
commits_histories_known: dict = {}


def get_commits_history_all_units(first_commit_id: str, last_commit_id: str, unit_list: list, repo_path: str,
                                  smell_type: str, filter_commits: bool, language: str) -> list:
    """
    Get the commit histories between two commits for all units in a list.
    :param last_commit_id:
    :param first_commit_id:
    :param unit_list:
    :param repo_path:
    :return: The commit histories list
    """
    commits: list = []

    repo: Repo = git.Repo(repo_path)

    if not repo_path.endswith(os.path.sep):
        repo_path += os.path.sep

    if filter_commits:
        dep_type = ["cyclicDep", "hubLikeDep", "unstableDep"]

        if smell_type in dep_type:
            commit_filter = CommitFilter.CommitFilterDep()
        elif smell_type == "godComponent":
            commit_filter = CommitFilter.CommitFilterGodComp()

    for unit in unit_list:

        if unit is not None:
            commit_history = get_commits_history_one_unit(unit, first_commit_id, last_commit_id, repo_path, repo)

            if filter_commits:
                commit_filter.filter_commits(commit_history, repo_path, repo, unit, language)

            if commit_history:
                commits.append({
                    "component": unit,
                    "commit_history": commit_history
                })

    return commits


def get_commits_history_one_unit(unit: str, first_commit_id: str, last_commit_id: str, repo_path: str,
                                 repo: Repo) -> list:
    """
    Get the commit history between two commits for one unit.
    :param last_commit_id:
    :param first_commit_id:
    :param unit:
    :param repo_path:
    :param repo: Repo object
    :return: The commit history
    """
    commits_history: list = []

    if (unit, first_commit_id, last_commit_id) not in commits_histories_known:
        current_commit = repo.commit(last_commit_id)

        while current_commit.hexsha != first_commit_id:
            if unit.replace(repo_path, "").replace(os.path.sep, "/") in current_commit.stats.files:
                commit = {
                    "commit_id": current_commit.hexsha,
                    "message": current_commit.message
                }

                if current_commit.parents:
                    commit["commit_parent_id"] = current_commit.parents[0].hexsha

                commits_history.append(commit)

            if current_commit.parents:
                current_commit = current_commit.parents[0]
            else:
                break

        commits_histories_known[(unit, first_commit_id, last_commit_id)] = commits_history
    else:
        commits_history = commits_histories_known[(unit, first_commit_id, last_commit_id)]

    return commits_history
