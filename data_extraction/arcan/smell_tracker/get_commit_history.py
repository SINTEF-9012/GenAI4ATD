import git
import os
import common.file_management as file_management


def get_commits_history_all_component(first_commit_id: str, last_commit_id: str, components_affected: list,
                                      repo_path: str, language: str):
    commits: list = []

    for c in components_affected:
        d: dict = {
            "component": c,
            "commit_history": get_commits_history_one_component(c, first_commit_id, last_commit_id, repo_path)
        }

        commits.append(d)

    return commits


def get_commits_history_one_component(component: str, first_commit_id: str, last_commit_id: str, repo_path: str):
    commits_history: list = []

    if component is not None:
        component = component.replace("/", "\\")

    repo = git.Repo(repo_path)

    current_commit = repo.commit(last_commit_id)

    while current_commit.hexsha != first_commit_id:
        for file in current_commit.stats.files:

            if os.path.join(repo_path, file).replace("/", "\\") == component:
                commits_history.append({
                    "commit_id": current_commit.hexsha,
                    "message": current_commit.message,
                })

        if current_commit.parents:
            current_commit = current_commit.parents[0]
        else:
            break

    return commits_history

