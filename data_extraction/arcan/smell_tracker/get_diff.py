import git
import common.file_management as file_management
import common.utils as utils

def get_diff_all_components(current_version_id: str, old_version_id: str, components_affected: str, repo_path: str,
                            language: str):
    diffs: list = []
    components: list = utils.get_components_as_list(components_affected)

    for c in components:
        d: dict = {
            "component": c,
            "diff": get_diff_one_component(current_version_id, old_version_id, c, repo_path, language)
        }

        diffs.append(d)

    return diffs


def get_diff_one_component(current_version_id: str, old_version_id: str, component: str, repo_path: str, language: str):
    file_full_path: str = file_management.get_full_path(component, repo_path, language)

    repo = git.Repo(repo_path)

    # command = "cd "+repo_path+" && git diff "+old_version_id+" "+current_version_id+" "+file_full_path
    # return subprocess.run(command, capture_output=True, shell=True)

    return repo.git.diff(current_version_id, old_version_id, file_full_path)