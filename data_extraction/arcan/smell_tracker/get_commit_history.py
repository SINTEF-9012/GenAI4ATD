import git
import os

# We keep the commit history of the units we already know, in case they appear multiple time in the data
# The key is (unit, first_commit_id, last_commit_id)
commits_histories_known: dict = {}


def get_commits_history_all_units(first_commit_id: str, last_commit_id: str, unit_list: list, repo_path: str):
    commits: list = []

    for unit in unit_list:
        commit_history: list = get_commits_history_one_unit(unit, first_commit_id, last_commit_id, repo_path)

        if commit_history:
            commits.append({
                "component": unit,
                "commit_history": commit_history
            })

    return commits


def get_commits_history_one_unit(unit: str, first_commit_id: str, last_commit_id: str, repo_path: str):
    commits_history: list = []

    if unit is not None:
        unit = unit.replace("/", "\\")

    if (unit, first_commit_id, last_commit_id) not in commits_histories_known:
        repo = git.Repo(repo_path)

        current_commit = repo.commit(last_commit_id)

        while current_commit.hexsha != first_commit_id:
            for file in current_commit.stats.files:

                if os.path.join(repo_path, file).replace("/", "\\") == unit:
                    commits_history.append({
                        "commit_id": current_commit.hexsha,
                        "message": current_commit.message,
                    })

            if current_commit.parents:
                current_commit = current_commit.parents[0]
            else:
                break

        commits_histories_known[(unit, first_commit_id, last_commit_id)] = commits_history
    else:
        commits_history = commits_histories_known[(unit, first_commit_id, last_commit_id)]

    return commits_history
