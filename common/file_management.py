import platform
import os

if platform.system() == "Windows":
    separator: str = "\\"
else:
    separator: str = "/"


def get_paths_main_packages(repo_path: str, language: str):
    paths_main_packages: list = []

    if language == "JAVA":
        for root, dirs, files in os.walk(repo_path):
            for name in dirs:
                if (os.path.join(root, name)).endswith((os.path.join("main", "java"))):
                    paths_main_packages.append(os.path.join(root, name) + separator)
    else:
        raise AttributeError("Language unsupported")

    return paths_main_packages


def convert_unit_to_path(unit: str, language: str):
    unit_path: str = unit.replace(".", separator)

    if language == "JAVA":
        unit_path += ".java"
    elif language == "CSHARP":
        unit_path += ".cs"

    return unit_path


def get_full_path(component: str, repo_path: str, language: str):
    component = convert_unit_to_path(component, language)
    path_main_packages: list = get_paths_main_packages(repo_path, language)

    for main_package in path_main_packages:
        if os.path.isfile(main_package + component):
            return main_package + component
