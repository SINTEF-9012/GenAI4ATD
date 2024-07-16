import git
import common.file_management as file_management


def get_diff_all_components(current_version_id: str, old_version_id: str, components_affected: list, repo_path: str,
                            language: str):
    diffs: list = []

    for c in components_affected:
        d: dict = {
            "component": c,
            "diff": get_diff_one_component(current_version_id, old_version_id, c, repo_path)
        }

        diffs.append(d)

    return diffs


def get_diff_one_component(current_version_id: str, old_version_id: str, component: str, repo_path: str):
    repo = git.Repo(repo_path)

    # command = "cd "+repo_path+" && git diff "+old_version_id+" "+current_version_id+" "+file_full_path
    # return subprocess.run(command, capture_output=True, shell=True)

    return repo.git.diff(current_version_id, old_version_id, component)