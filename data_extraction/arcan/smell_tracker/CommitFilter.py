import os.path
from abc import ABC, abstractmethod
from git import Repo


class CommitFilter(ABC):
    """
    Base class for all commit filters
    """

    @abstractmethod
    def filter_commits(self, commits_history: list, repo_path: str, repo: Repo, unit: str, language: str) -> list:
        """
        Filter commits
        :param commits_history:
        :param repo_path:
        :param repo: Repo object
        :param unit:
        :return: Filtered commits
        """
        pass


class CommitFilterDep(CommitFilter):

    def filter_commits(self, commits_history: list, repo_path: str, repo: Repo, unit: str, language: str) -> list:
        filtered_commits = []

        if language == "JAVA":
            import_statement = "import"
        elif language == "CSHARP":
            import_statement = "using"

        for commit in commits_history:
            git_diff_res = repo.git.diff(commit["commit_id"], commit["commit_parent_id"], os.path.join(repo_path, unit))

            for line in git_diff_res.split("\n"):
                if line.startswith("+" + import_statement):
                    filtered_commits.append(commit)
                    break

        return filtered_commits


class CommitFilterGodComp(CommitFilter):

    def filter_commits(self, commits_history: list, repo_path: str, repo: Repo, unit: str, language: str) -> list:
        # TODO
        filtered_commits = commits_history
        return filtered_commits
